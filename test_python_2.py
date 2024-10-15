import unittest
from unittest.mock import patch, MagicMock
import asyncio
import os
import datetime
import sys
from dotenv import load_dotenv
from secret_sdk.core.wasm import MsgExecuteContract, MsgInstantiateContract, MsgStoreCode
from secret_sdk.core import Coins, TxResultCode
from secret_sdk.util.tx import get_value_from_raw_log
from secret_sdk.protobuf.cosmos.tx.v1beta1 import BroadcastMode
# Import only used functions from secret_settings module
from secret.secret_settings import get_client, PATH_WASM
from secret.client import Client
from cred.cred import Cred
load_dotenv()

SKIP_UPDATE_CONTRACT = True


class TestSecretConnect(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        if SKIP_UPDATE_CONTRACT:
            cls.client = Client()
        else:
            cls.client = Client(True)

    def test_balance(self):
        balance = self.client.secret.bank.balance(self.client.wallet.key.acc_address)
        assert balance[0].get("uscrt").amount > 0

    @unittest.skipIf(SKIP_UPDATE_CONTRACT, "Skipping this test")
    def test_01_create_contract(self):
        self.client.reset()
        self.client.create_contract()
        assert (self.client.code_id is not None)
        assert (self.client.code_hash is not None)
        assert (self.client.contract_address is not None)
        assert (self.client.count is not None)

    def test_execute_contract(self):
        if self.client.contract_address is None:
            self.client.load_contract_info()
        assert (self.client.contract_address is not None)
        assert (self.client.code_hash is not None)
        # Execute increment : Prepare tx
        tx_execute = self.client.increment()

        if tx_execute.code != TxResultCode.Success.value:
            raise Exception(f"Failed MsgExecuteContract: {tx_execute.rawlog}")
        assert tx_execute.code == TxResultCode.Success.value

        self.client.count += 1
        self.client.save_contract_info()

    def test_execute_add(self):
        if self.client.contract_address is None:
            self.client.load_contract_info()
        assert (self.client.contract_address is not None)
        assert (self.client.code_hash is not None)
        # prepare a mock cred
        my_cred = Cred.mock()

        # Execute increment : Prepare tx
        tx_execute = self.client.add(my_cred)

        if tx_execute.code != TxResultCode.Success.value:
            raise Exception(f"Failed MsgExecuteContract: {tx_execute.rawlog}")
        assert tx_execute.code == TxResultCode.Success.value

        # self.client.count += 1
        # self.client.save_contract_info()
        res = self.client.query_get_all()

        assert res["vect_cred"][0] == my_cred.to_dict()

    def test_query_contract(self):

        if self.client.contract_address is None:
            self.client.load_contract_info()
        assert (self.client.contract_address is not None)
        assert (self.client.code_hash is not None)
        res = self.client.query({"get_count": {}})
        count_old = self.client.count
        print(res)
        if res != {'count': self.client.count}:
            if res.count >= 0:
                self.client.count = res.count
                self.client.save_contract_info()

        assert res["count"] == count_old

    def test_query_get_all(self):

        res = self.client.query_get_all()
        cred_keys = Cred.mock().to_dict().keys()
        # Check if res is of type Cred
        assert list(res["vect_cred"][0].keys()) == list(cred_keys)


if __name__ == "__main__":
    unittest.main()
