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

load_dotenv()

SKIP_UPDATE_CONTRACT = True


def save_contract_info(code_id, code_hash, contract_address, count):
    with open("contract_info.txt", "w") as f:
        f.write(f"{code_id}\n{code_hash}\n{contract_address}\n{count}\n")


def load_contract_info():
    with open("contract_info.txt", "r") as f:
        tuple_ = [line.strip() for line in f.readlines()]
        return tuple_[0], tuple_[1],  tuple_[2], int(tuple_[3])


class TestSecretConnect(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.secret, cls.wallet = get_client()
        if SKIP_UPDATE_CONTRACT:
            cls.code_id, cls.code_hash, cls.contract_address, cls.count = load_contract_info()
        else:
            cls.code_id = None
            cls.code_hash = None
            cls.contract_address = None
            cls.count = 0

    def test_balance(self):
        balance = self.secret.bank.balance(self.wallet.key.acc_address)
        assert balance[0].get("uscrt").amount > 0

    @unittest.skipIf(SKIP_UPDATE_CONTRACT, "Skipping this test")
    def test_01_create_contract(self):
        with self.subTest("Check Balance"):
            balance = self.secret.bank.balance(self.wallet.key.acc_address)
            assert balance[0].get("uscrt").amount > 0

        with self.subTest("Check code Store"):
            with open(PATH_WASM, "rb") as file:
                wasm_byte_code = file.read()

            msg_store_code = MsgStoreCode(
                sender=self.wallet.key.acc_address,
                wasm_byte_code=wasm_byte_code,
                source="",
                builder="",
            )

            tx_store = self.wallet.create_and_broadcast_tx(
                [msg_store_code], gas='4000000', gas_prices=Coins('0.25uscrt'))

            assert tx_store.code == TxResultCode.Success.value
            self.__class__.code_id = int(get_value_from_raw_log(tx_store.rawlog, 'message.code_id'))
            code_info = self.secret.wasm.code_info(self.code_id)
            self.__class__.code_hash = code_info['code_info']['code_hash']

        with self.subTest("Check Instantiate"):
            assert (self.code_id is not None)
            assert (self.code_hash is not None)
            self.__class__.count = 0
            msg_init = MsgInstantiateContract(
                sender=self.wallet.key.acc_address,
                code_id=self.code_id,
                code_hash=self.code_hash,
                init_msg={"count": self.count},
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
            assert tx_init.code == TxResultCode.Success.value
            assert get_value_from_raw_log(
                tx_init.rawlog, 'message.action') == "/secret.compute.v1beta1.MsgInstantiateContract"
            self.__class__.contract_address = get_value_from_raw_log(
                tx_init.rawlog, 'message.contract_address')

            save_contract_info(self.code_id, self.code_hash, self.contract_address, self.count)

    def test_execute_contract(self):
        if self.contract_address is None:
            self.__class__.code_id, self.__class__.code_hash, self.__class__.contract_address, self.__class__.count = load_contract_info()

        assert (self.contract_address is not None)
        assert (self.code_hash is not None)
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
        self.__class__.count += 1
        save_contract_info(self.code_id, self.code_hash, self.contract_address, self.count)

    def test_async_execute_contract(self):
        if self.contract_address is None:
            self.__class__.code_id, self.__class__.code_hash, self.__class__.contract_address, self.__class__.count = load_contract_info()
        assert (self.contract_address is not None)
        assert (self.code_hash is not None)
        # Execute increment : Prepare tx
        msg_execute = MsgExecuteContract(
            sender=self.wallet.key.acc_address,
            contract=self.contract_address,
            msg={"increment": {}},
            code_hash=self.code_hash,
            encryption_utils=self.secret.encrypt_utils,
        )
        # Execute increment async mode : Send tx
        tx = self.wallet.create_and_broadcast_tx(
            [msg_execute],
            gas='5000000',
            gas_prices=Coins('0.25uscrt'),
            broadcast_mode=BroadcastMode.BROADCAST_MODE_ASYNC,
        )
        # Execute increment async mode : Check tx
        tx_hash = tx.txhash
        tx_execute_async = self.secret.tx.get_tx(tx_hash)
        while tx_execute_async is None:
            tx_execute_async = self.secret.tx.get_tx(tx_hash)
        assert tx_execute_async.code == TxResultCode.Success.value

        self.__class__.count += 1
        save_contract_info(self.code_id, self.code_hash, self.contract_address, self.count)

    def test_query_contract(self):
        if self.contract_address is None:
            self.__class__.code_id, self.__class__.code_hash, self.__class__.contract_address, self.__class__.count = load_contract_info()
        assert (self.contract_address is not None)
        assert (self.code_hash is not None)
        res = self.secret.wasm.contract_query(
            contract_address=self.contract_address,
            query={"get_count": {}},
            contract_code_hash=self.code_hash,
        )
        print(res)
        assert res == {'count': self.count}
        save_contract_info(self.code_id, self.code_hash, self.contract_address, self.count)


if __name__ == "__main__":
    unittest.main()
