# import os
import datetime
import json
import base64
import copy
# import sys
from dotenv import load_dotenv
from secret_sdk.core.wasm import MsgExecuteContract, MsgInstantiateContract, MsgStoreCode
from secret_sdk.core import Coins, TxResultCode
from secret_sdk.util.tx import get_value_from_raw_log
# from secret_sdk.protobuf.cosmos.tx.v1beta1 import BroadcastMode
# Import only used functions from secret_settings module
from secret.secret_settings import get_client, PATH_WASM, PATH_INFO, PERMIT_NAME, PATH_PERMIT

load_dotenv()


class Client():
    def __init__(self, mode_update=False):
        self.secret, self.wallet = get_client()
        if mode_update:
            self.reset()
        else:
            self.load_contract_info()
        self.balance = None

    def reset(self):
        self.code_id = None
        self.code_hash = None
        self.contract_address = None
        self.count = 0

    def check_balance(self):
        self.balance = self.secret.bank.balance(self.wallet.key.acc_address)
        assert self.balance[0].get("uscrt").amount > 0, "No balance found"
        return self.balance

    def get_balance(self):
        self.balance = self.secret.bank.balance(self.wallet.key.acc_address)
        return self.balance

    def store_code(self):
        with open(PATH_WASM, 'rb') as wasm_file:
            code = wasm_file.read()
        msg_store_code = MsgStoreCode(
            sender=self.wallet.key.acc_address,
            wasm_byte_code=code,
            source="",
            builder="",
        )
        tx_store = self.wallet.create_and_broadcast_tx(
            [msg_store_code], gas='4000000', gas_prices=Coins('0.25uscrt'))
        if tx_store.code != TxResultCode.Success.value:
            raise Exception(f"Failed MsgStoreCode: {tx_store.raw_log}")
        assert tx_store.code == TxResultCode.Success.value
        self.code_id = int(get_value_from_raw_log(tx_store.rawlog, 'message.code_id'))
        code_info = self.secret.wasm.code_info(self.code_id)
        self.code_hash = code_info['code_info']['code_hash']
        print(f"Stored code with ID: {self.code_id}")
        return tx_store

    def instantiate(self):
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
        tx_init = self.wallet.create_and_broadcast_tx(
            [msg_init],
            gas='5000000',
            gas_prices=Coins('0.25uscrt')
        )
        # instantiate : Check tx output
        if tx_init.code != TxResultCode.Success.value:
            raise Exception(f"Failed MsgInstiateContract: {tx_init.raw_log}")
        assert tx_init.code == TxResultCode.Success.value
        assert get_value_from_raw_log(
            tx_init.rawlog, 'message.action') == "/secret.compute.v1beta1.MsgInstantiateContract"
        self.contract_address = get_value_from_raw_log(tx_init.rawlog, 'message.contract_address')
        assert self.contract_address == tx_init.data[0].address  # Check address
        return tx_init

    def create_contract(self):
        self.store_code()
        self.instantiate()
        self.save_contract_info()

    def increment(self):
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
            raise Exception(f"Failed MsgExecuteContract: {tx_execute.raw_log}")
        assert tx_execute.code == TxResultCode.Success.value

        return tx_execute

    def query(self, msg):
        assert (self.contract_address is not None)
        assert (self.code_hash is not None)
        res = self.secret.wasm.contract_query(
            contract_address=self.contract_address,
            query=msg,
            contract_code_hash=self.code_hash,
        )
        return res

    def save_contract_info(self):
        assert (self.code_id is not None)
        assert (self.code_hash is not None)
        assert (self.contract_address is not None)
        assert (self.count is not None)
        with open(PATH_INFO, "w", encoding="utf-8") as f:
            f.write(f"{self.code_id}\n{self.code_hash}\n{self.contract_address}\n{self.count}\n")

    def load_contract_info(self):
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
        #
        '''signature = self.wallet.key.sign(
            bytes(
                json.dumps(
                    self.msg_permit(),
                    separators=(',', ':'),
                    sort_keys=True
                ).encode('utf-8')
            )
        )'''

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

        '''msg_save = {
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
                    "signature": str(signature),
                },
            },
        }'''

        # save  / dump into a file permit.json for debugging purpose.
        with open(PATH_PERMIT, "w", encoding="utf-8") as f:
            json.dump(msg_save, f, indent=2)

        print(msg)
        return msg
        # res = self.query(msg)
