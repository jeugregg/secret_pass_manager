# Tests for Secret Connect Client

## Overview
This document provides an overview of the unit tests conducted on the `SecretConnect` client module. The tests cover various functionalities, including balance retrieval, contract creation, executing transactions, and querying contract state.

## Environment
- **Python Version**: Python 3.12
- **Framework**: `unittest`, `asyncio`, `dotenv`, `secret_sdk`
- **Date of Testing**: [2024-10-16]

## Test Cases

### test_balance
**Description**: Verifies that the client retrieves a non-zero balance for the user's account.
**Outcome**: Successful. The balance is greater than 0.

### test_01_create_contract
**Description**: Tests the creation of a new contract and ensures that essential attributes (code_id, code_hash, contract_address) are not None.
**Outcome**: Successful. All required attributes are set correctly.

### test_execute_contract
**Description**: Executes a contract function (`increment`) and asserts that the transaction is successful.
**Outcome**: Successful. The transaction code is `Success`.

### test_execute_add
**Description**: Executes a custom function (`add`) to add data and ensures the transaction is successful.
**Outcome**: Successful. The transaction code is `Success` and the client's state is updated correctly.

### test_query_contract
**Description**: Queries the contract for its count and asserts that it matches the client's current count.
**Outcome**: Successful. The retrieved count matches the client's current count.

### test_query_get_all
**Description**: Queries all data from the contract and asserts that the results are instances of `Cred`.
**Outcome**: Successful. All retrieved results are valid instances of `Cred`.

## Summary
All tests were executed successfully, ensuring the functionality of the `SecretConnect` client is working as expected.

---

This Markdown documentation provides a structured overview of the test results, making it easy to understand and review the outcomes.