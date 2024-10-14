import unittest
from unittest.mock import patch, MagicMock
import asyncio
import os
import datetime
import sys
from dotenv import load_dotenv
from secret_sdk.client.lcd import AsyncLCDClient, LCDClient
from secret_sdk.client.lcd.api.tx import CreateTxOptions
from secret_sdk.core import Coins
from secret_sdk.core.wasm import MsgExecuteContract, MsgInstantiateContract, MsgStoreCode
from secret_sdk.key.mnemonic import MnemonicKey

# Load environment variables from .env file
load_dotenv()

MODE_TEST = True

if MODE_TEST:
    chain_id = "pulsar-3"
    node_rest_endpoint = "https://api.pulsar.scrttestnet.com"
    faucet_endpoint = "https://faucet.pulsar.scrttestnet.com"
else:
    chain_id = "secretdev-1"
    node_rest_endpoint = "https://1317-scrtlabs-gitpodlocalsec-4ogk0hk9djs.ws-us116.gitpod.io"
    faucet_endpoint = "https://5000-scrtlabs-gitpodlocalsec-4ogk0hk9djs.ws-us116.gitpod.io"


class TestSecretConnect(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.secret = LCDClient(chain_id=chain_id, url=node_rest_endpoint)
        cls.mnemonic_phrase = os.getenv('MNEMONIC')
        cls.mnk = MnemonicKey(mnemonic=cls.mnemonic_phrase)
        cls.wallet = cls.secret.wallet(cls.mnk)

    @patch('webbrowser.open')
    def test_balance_check(self, mock_open):
        balance = self.secret.bank.balance(self.wallet.key.acc_address)
        if balance[0].get("uscrt").amount <= 0:
            mock_open(faucet_endpoint)
            input("Press Enter to continue...")
            balance = self.secret.bank.balance(self.wallet.key.acc_address)
            assert balance[0].get("uscrt").amount > 0
        else:
            assert balance[0].get("uscrt").amount > 0

    def test_store_code(self):
        # Open and read the WASM file
        with open(PATH_WASM, "rb") as file:
            wasm_byte_code = file.read()

        # Create the store code message
        msg_store_code = MsgStoreCode(
            sender=self.wallet.key.acc_address,
            wasm_byte_code=wasm_byte_code,
            source="",
            builder="",
        )

        # Send the transaction to instantiate the contract
        tx_store = self.wallet.create_and_broadcast_tx(
            [msg_store_code], gas='4000000', gas_prices=Coins('0.25uscrt'))

        # Check that the transaction was successful
        assert tx_store.code == TxResultCode.Success.value

    @patch('secret_sdk.client.lcd.AsyncLCDClient.instantiate_contract')
    def test_instantiate_contract(self, mock_instantiate_contract):
        code_id = 123456789
        msg_init = MsgInstantiateContract(
            sender=self.wallet.key.acc_address,
            code_id=code_id,
            init_msg={"count": 0},
            label=f"counter {datetime.datetime.now()}",
            encryption_utils=None,
        )
        tx_init = self.wallet.create_and_broadcast_tx(
            [msg_init], gas='5000000', gas_prices=Coins('0.25uscrt'))
        mock_instantiate_contract.assert_called_once_with(
            sender=self.wallet.key.acc_address,
            code_id=code_id,
            init_msg={"count": 0},
            label=f"counter {datetime.datetime.now()}",
            encryption_utils=None
        )
        assert tx_init.code == 0

    @patch('secret_sdk.client.lcd.AsyncLCDClient.execute_contract')
    def test_execute_contract(self, mock_execute_contract):
        code_id = 123456789
        contract_adress = "contract_address"
        msg_execute = MsgExecuteContract(
            sender=self.wallet.key.acc_address,
            contract=contract_adress,
            msg={"increment": {}},
            code_hash=None,
            encryption_utils=None,
        )
        tx_execute = self.wallet.create_and_broadcast_tx(
            [msg_execute], gas='5000000', gas_prices=Coins('0.25uscrt'))
        mock_execute_contract.assert_called_once_with(
            sender=self.wallet.key.acc_address,
            contract=contract_adress,
            msg={"increment": {}},
            code_hash=None,
            encryption_utils=None
        )
        assert tx_execute.code == 0

    @patch('secret_sdk.client.lcd.AsyncLCDClient.contract_query')
    def test_query_contract(self, mock_contract_query):
        contract_address = "contract_address"
        res = self.secret.wasm.contract_query(
            contract_address=contract_address,
            query={"get_count": {}},
            contract_code_hash=None,
        )
        mock_contract_query.assert_called_once_with(
            contract_address=contract_address,
            query={"get_count": {}},
            contract_code_hash=None,
        )
        assert res == {'count': 2}


if __name__ == "__main__":
    unittest.main()
