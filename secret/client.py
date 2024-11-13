import os
import time
import datetime
import json
import base64
import copy
from dotenv import load_dotenv
from secret_sdk.core.wasm import MsgExecuteContract, MsgInstantiateContract, MsgStoreCode
from secret_sdk.core import Coins, TxResultCode
from secret_sdk.util.tx import get_value_from_events
from secret_sdk.protobuf.cosmos.tx.v1beta1 import BroadcastMode
from secret_sdk.exceptions import LCDResponseError
from secret.secret_settings import get_client, PATH_WASM, PATH_INFO
from secret.secret_settings import PERMIT_NAME, PATH_PERMIT, explorer_endpoint, faucet_endpoint
from cred.cred import Cred
load_dotenv()
MNEMONIC_PHRASE = os.getenv('MNEMONIC')

class Client():
    """
    A client class used to interact with a blockchain wallet using a mnemonic phrase.

    TODO : add python support to Keplr wallet extension
    """

    def __init__(self, mode_update=False, mnemonic_phrase=MNEMONIC_PHRASE):
        """
        Initialize the Client object.

        Args:
            mode_update (bool): Flag indicating if the client is in update mode => create new vault contract 
            mnemonic_phrase (str): The mnemonic phrase used for wallet creation. Defaults to the environment variable MNEMONIC.
        """
        self.secret, self.wallet = get_client(mnemonic_phrase)
        if mode_update:
            self.reset()
        else:
            self.load_contract_info()
        self.balance = None

    def create_and_broadcast_tx(self, msgs, gas=None, gas_prices=None):
        """
        Creates and broadcasts a transaction to the network, returns the broadcast receipt
        Args:
            msgs: msgs to be sent

        Returns:
                the receipt of the broadcast transaction

        """
        max_retries = 20
        wait_interval = 3
        max_broadcast_attempts = 3  # Number of times to retry the entire broadcast process
        broadcast_attempt = 0

        while broadcast_attempt < max_broadcast_attempts:
            try:
                # Broadcast the transaction in SYNC mode
                final_tx = self.wallet.create_and_broadcast_tx(msgs, gas=gas, gas_prices=gas_prices, broadcast_mode=BroadcastMode.BROADCAST_MODE_SYNC)
                tx_hash = final_tx.txhash
                print(f"Transaction broadcasted with hash: {tx_hash}")

                # Repeatedly fetch the transaction result until it's included in a block
                for attempt in range(max_retries):
                    try:
                        tx_result = self.wallet.lcd.tx.tx_info(tx_hash)
                        if tx_result:
                            print(f"Transaction included in block: {tx_result.height}")
                            return tx_result  # Exit function if transaction is successfully included in a block
                    except LCDResponseError as e:
                        if 'not found' in str(e).lower():
                            # Transaction not yet found, wait and retry
                            print(f"Transaction not found, retrying... ({attempt + 1}/{max_retries})")
                            time.sleep(wait_interval)
                            continue
                        else:
                            print(f"LCDResponseError while fetching tx result: {e}")
                            raise e
                    except Exception as e:
                        print(f"Unexpected error while fetching tx result: {e}")
                        raise e
                # If max_retries are exceeded and no result is found, retry broadcasting
                print(
                    f"Transaction {tx_hash} not included in a block after {max_retries} retries. Retrying broadcast... ({broadcast_attempt + 1}/{max_broadcast_attempts})")

            except LCDResponseError as e:
                print(f"LCDResponseError during transaction broadcast: {e}")
                raise e
            except Exception as e:
                print(f"An unexpected error occurred during transaction broadcast: {e}")
                raise e

            # Increment the broadcast attempt counter
            broadcast_attempt += 1

    def reset(self):
        """
        Reset the client's state by clearing code_id and code_hash.
        """
        self.code_id = None
        self.code_hash = None
        self.contract_address = None
        self.count = 0

    def check_balance(self):
        """
        Check the balance of the wallet and assert that it has a positive amount.

        Returns:
            dict: The balance information.

        Raises:
            AssertionError: If no balance is found.
        """
        self.balance = self.secret.bank.balance(self.wallet.key.acc_address)
        assert self.balance[0].get("uscrt").amount > 0, "No balance found"
        return self.balance

    def get_balance(self):
        """
        Get the current balance of the wallet.

        Returns:
            dict: The balance information.
        """
        self.balance = self.secret.bank.balance(self.wallet.key.acc_address)
        return self.balance

    def store_code(self):
        """
        Store a smart contract code on the blockchain.

        Raises:
            FileNotFoundError: If the WASM file is not found.
        """
        with open(PATH_WASM, 'rb') as wasm_file:
            code = wasm_file.read()
        msg_store_code = MsgStoreCode(
            sender=self.wallet.key.acc_address,
            wasm_byte_code=code,
            source="",
            builder="",
        )
        tx_store = self.create_and_broadcast_tx([msg_store_code], gas='4000000', gas_prices=Coins('0.25uscrt'))
        if tx_store.code != TxResultCode.Success.value:
            raise Exception(f"Failed MsgStoreCode: {tx_store.rawlog}")
        self.code_id = int(get_value_from_events(tx_store.events, 'message.code_id'))
        code_info = self.secret.wasm.code_info(self.code_id)
        self.code_hash = code_info['code_info']['code_hash']
        print(f"Stored code with ID: {self.code_id}")
        return tx_store

    def instantiate(self):
        """
        Store a smart contract code on the blockchain.

        Raises:
            FileNotFoundError: If the WASM file is not found.
        """
        self.check_balance()
        assert (self.code_id is not None)
        assert (self.code_hash is not None)
        msg_init = MsgInstantiateContract(
            sender=self.wallet.key.acc_address,
            code_id=self.code_id,
            code_hash=self.code_hash,
            init_msg={"count": 0},
            label=f"counter {datetime.datetime.now()}",
            encryption_utils=self.secret.encrypt_utils,
        )

        # Instantiate contract : Send tx
        tx_init = self.create_and_broadcast_tx(
            [msg_init],
            gas='5000000',
            gas_prices=Coins('0.25uscrt')
        )
        # instantiate : Check tx output
        if tx_init.code != TxResultCode.Success.value:
            raise Exception(f"Failed MsgInstiateContract: {tx_init.rawlog}")
        assert get_value_from_events(
            tx_init.events, 'message.action') == "/secret.compute.v1beta1.MsgInstantiateContract"
        self.contract_address = get_value_from_events(tx_init.events, 'message.contract_address')
        return tx_init

    def create_contract(self):
        """
        Create a smart contract by storing the code and instantiating it.

        Raises:
            Exception: If the creation fails.
        """
        self.store_code()
        self.instantiate()
        self.save_contract_info()

    def increment(self):
        """
        Check the balance before performing an operation on the contract.

        Raises:
            AssertionError: If the balance is insufficient.
        """
        self.check_balance()
        assert (self.code_id is not None)
        assert (self.code_hash is not None)
        assert (self.contract_address is not None)
        # Execute increment : Prepare tx
        msg_execute = MsgExecuteContract(
            sender=self.wallet.key.acc_address,
            contract=self.contract_address,
            msg={"increment": {}},
            code_hash=self.code_hash,
            encryption_utils=self.secret.encrypt_utils,
        )
        # Execute increment : Send tx
        tx_execute = self.wallet.create_and_broadcast_tx(
            [msg_execute],
            gas='5000000',
            gas_prices=Coins('0.25uscrt'),
        )
        # Execute increment : Check tx
        if tx_execute.code != TxResultCode.Success.value:
            raise Exception(f"Failed MsgExecuteContract: {tx_execute.rawlog}")
        assert tx_execute.code == TxResultCode.Success.value

        return tx_execute

    def add(self, cred: Cred):
        """
        Add a credential to the smart contract and check the balance.

        Args:
            cred (Cred): The credential to be added.

        Returns:
            dict: The transaction result.

        Raises:
            AssertionError: If the balance is insufficient or if the code hash or contract address is missing.
        """
        self.check_balance()
        assert (self.code_hash is not None)
        assert (self.contract_address is not None)
        # Execute increment : Prepare tx
        msg_execute = MsgExecuteContract(
            sender=self.wallet.key.acc_address,
            contract=self.contract_address,
            msg={"add": {"credential": cred.to_dict()}},
            code_hash=self.code_hash,
            encryption_utils=self.secret.encrypt_utils,
        )
        # Execute increment : Send tx
        tx_execute = self.create_and_broadcast_tx(
            [msg_execute],
            gas='5000000',
            gas_prices=Coins('0.25uscrt'),
        )
        # Execute increment : Check tx
        if tx_execute.code != TxResultCode.Success.value:
            raise Exception(f"Failed MsgExecuteContract: {tx_execute.rawlog}")
        assert tx_execute.code == TxResultCode.Success.value

        return tx_execute

    def query(self, msg):
        """
        Query the smart contract with a given message and check the balance.

        Args:
            msg (dict): The message to be queried.

        Returns:
            dict: The query result.

        Raises:
            AssertionError: If the code hash or contract address is missing.
        """
        assert (self.contract_address is not None)
        assert (self.code_hash is not None)
        res = self.secret.wasm.contract_query(
            contract_address=self.contract_address,
            query=msg,
            contract_code_hash=self.code_hash,
        )
        return res

    def save_contract_info(self):
        """
        Save the smart contract information to a file.

        Raises:
            AssertionError: If any of the required information is missing.
        """
        assert (self.code_id is not None)
        assert (self.code_hash is not None)
        assert (self.contract_address is not None)
        assert (self.count is not None)
        with open(PATH_INFO, "w", encoding="utf-8") as f:
            f.write(f"{self.code_id}\n{self.code_hash}\n{self.contract_address}\n{self.count}\n")

    def load_contract_info(self):
        """
        Load the smart contract information from a file.

        Raises:
            AssertionError: If any of the required information is missing.
        """
        with open(PATH_INFO, "r", encoding="utf-8") as f:
            tuple_ = [line.strip() for line in f.readlines()]
        assert (tuple_ is not None)
        assert (tuple_[0] is not None)
        assert (tuple_[1] is not None)
        assert (tuple_[2] is not None)
        assert (tuple_[3] is not None)
        self.code_id = tuple_[0]
        self.code_hash = tuple_[1]
        self.contract_address = tuple_[2]
        self.count = int(tuple_[3])

    def msg_permit(self):
        """
        Generate a message to query a permit for the given contract address.

        This method constructs a Cosmos SDK transaction message with specific parameters
        to request a permit. The permit is used to authorize interactions with the specified
        smart contract on the Secret Network.

        Returns:
            dict: A dictionary representing the transaction message.
        """
        assert (self.contract_address is not None)
        msg = {
            "chain_id": self.secret.chain_id,
            "account_number": "0",
            "sequence": "0",
            "fee": {
                "amount": [{"denom": "uscrt", "amount": "0"}],  # Must be 0 uscrt
                "gas": "1",  # Must be 1
            },
            "msgs": [
                {
                    "type": "query_permit",  # Must be "query_permit"
                    "value": {
                        "permit_name": PERMIT_NAME,
                        "allowed_tokens": [self.contract_address],
                        "permissions": [],
                    },
                },
            ],
            "memo": "",  # Must be empty
        }
        return msg

    def signAmino(self, msg):
        """
        Sign the given message using the wallet's private key and 
          return a dictionary containing the public key and signature.

        Args:
            msg: The message to be signed.

        Returns:
            A dictionary with keys 'pub_key' and 'signature'.
        """
        signature = self.wallet.key.sign(
            bytes(
                json.dumps(
                    msg,
                    separators=(',', ':'),
                    sort_keys=True
                ).encode('utf-8')
            )
        )
        print(signature)
        return {
            "pub_key": {
                "type": self.wallet.key.public_key.type_amino,
                "value": self.wallet.key.public_key.key,
            },
            "signature": signature,
        }

    def query_get_all(self):
        """
        Query all Cred using a prepared message and handle the response.

        Returns:
            A list of Cred objects retrieved from the query response.
        """
        self.check_balance()
        assert (self.code_hash is not None)
        assert (self.contract_address is not None)

        sign_amino = self.signAmino(self.msg_permit())

        msg = {
            "get_all": {
                "wallet": self.wallet.key.acc_address,
                "index": 0,
                "permit": {
                    "params": {
                        "permit_name": PERMIT_NAME,
                        "allowed_tokens": [self.contract_address],
                        "chain_id": self.secret.chain_id,
                        "permissions": [],
                    },
                    "signature": sign_amino,
                },
            },
        }
        msg_save = copy.deepcopy(msg)
        signature_save = msg_save["get_all"]["permit"]["signature"]["signature"]
        signature_save = base64.b64encode(signature_save).decode('utf-8')
        msg_save["get_all"]["permit"]["signature"]["signature"] = signature_save
        pubkey_save = msg_save["get_all"]["permit"]["signature"]["pub_key"]["value"]
        pubkey_save = base64.b64encode(pubkey_save).decode('utf-8')
        msg_save["get_all"]["permit"]["signature"]["pub_key"]["value"] = pubkey_save

        # save  / dump into a file permit.json for debugging purpose.
        with open(PATH_PERMIT, "w", encoding="utf-8") as f:
            json.dump(msg_save, f, indent=2)

        print("msg: ", msg)
        # query  all Cred : Prepare tx
        res = self.query(msg_save)
        print("res: ", res)

        return [Cred.from_dict(cred_curr) for cred_curr in res["vect_cred"]]

    @staticmethod
    def get_url_tx(tx_hash):
        """
        Get the URL for a given transaction hash.

        Args:
            tx_hash (str): The transaction hash to generate the URL for.

        Returns:
            str: The URL of the transaction on the blockchain explorer.
        """
        return f"{explorer_endpoint}{tx_hash}"

    @staticmethod
    def get_url_faucet():
        """
        Get the URL of the faucet.

        Returns:
            str: The URL of the faucet where users can request tokens.
        """
        return faucet_endpoint
