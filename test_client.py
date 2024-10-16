"""
Test cases for the Secret Connect client.
This module includes various unit tests to verify the functionality of the client,
including creating contracts, executing transactions, and querying contract state.
"""
import unittest
from dotenv import load_dotenv
from secret_sdk.core import TxResultCode
# Import only used functions from secret_settings module
from secret.client import Client
from cred.cred import Cred
load_dotenv()

SKIP_UPDATE_CONTRACT = True


class TestSecretConnect(unittest.TestCase):
    """
    Unit tests for the Secret Connect client.
    """
    @classmethod
    def setUpClass(cls):
        """
        Set up class-level resources before running any test methods.
        If SKIP_UPDATE_CONTRACT is True, use an existing client; otherwise, create a new one.
        """
        if SKIP_UPDATE_CONTRACT:
            cls.client = Client()
        else:
            cls.client = Client(True)

    def test_balance(self):
        """
        Test the balance retrieval functionality of the client.
        Asserts that the user's balance is greater than 0.
        """
        balance = self.client.secret.bank.balance(self.client.wallet.key.acc_address)
        assert balance[0].get("uscrt").amount > 0

    @unittest.skipIf(SKIP_UPDATE_CONTRACT, "Skipping this test")
    def test_01_create_contract(self):
        """
        Test the contract creation functionality of the client.
        Asserts that the code_id, code_hash, and contract_address are not None.
        """
        self.client.reset()
        self.client.create_contract()
        assert (self.client.code_id is not None)
        assert (self.client.code_hash is not None)
        assert (self.client.contract_address is not None)
        assert (self.client.count is not None)

    def test_execute_contract(self):
        """
        Test the execution of a contract function.
        Asserts that the transaction code is Success and updates the client's count if successful.
        """
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
        """
        Test the execution of a custom function to add data.
        Asserts that the transaction code is Success and updates the client's state if successful.
        """
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

        assert res[0].to_dict() == my_cred.to_dict()

    def test_query_contract(self):
        """
        Test querying the contract state.
        Asserts that the retrieved count matches the client's current count.
        """
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
        """
        Test querying all data from the contract.
        Asserts that the retrieved results are instances of Cred.
        """
        res = self.client.query_get_all()
        cred_keys = Cred.mock().to_dict().keys()
        # Check if res is of type Cred
        assert isinstance(res[0], Cred)


if __name__ == "__main__":
    unittest.main()
