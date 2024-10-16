# Client Class Documentation

## Overview

The `Client` class is designed to interact with a blockchain wallet using a mnemonic phrase. It provides functionality to manage smart contracts, perform transactions, and query the blockchain.

## Installation

Ensure you have the required dependencies installed:

```
pip install secret-sdk python-dotenv
```

## Usage

```python
from client import Client

# Initialize the client
client = Client()

# Check balance
balance = client.check_balance()

# Create a new contract
client.create_contract()

# Perform operations
client.increment()
```

## Class: Client

### Initialization

```python
Client(mode_update=False, mnemonic_phrase=MNEMONIC_PHRASE)
```

- `mode_update` (bool): Flag indicating if the client is in update mode (creates a new vault contract)
- `mnemonic_phrase` (str): The mnemonic phrase used for wallet creation

### Methods

#### `reset()`
Resets the client's state by clearing code_id and code_hash.

#### `check_balance()`
Checks the wallet balance and asserts that it has a positive amount.

**Returns:** dict - The balance information

#### `get_balance()`
Gets the current balance of the wallet.

**Returns:** dict - The balance information

#### `store_code()`
Stores a smart contract code on the blockchain.

**Returns:** Transaction result

#### `instantiate()`
Instantiates a stored smart contract on the blockchain.

**Returns:** Transaction result

#### `create_contract()`  
- Creates a smart contract by storing the code and instantiating it.  
- The Contract information is saved into 
    - `contract_info.txt`  It contains: 
        - code id
        - code hash
        - contract address
        - counter 
    

#### `increment()`
Performs an increment operation on the contract.

**Returns:** Transaction result

#### `add(cred: Cred)`
Adds a credential to the smart contract.

**Parameters:**
- `cred` (Cred): The credential to be added

**Returns:** Transaction result

#### `query(msg)`
Queries the smart contract with a given message.

**Parameters:**
- `msg` (dict): The message to be queried

**Returns:** dict - The query result

#### `save_contract_info()`
Saves the smart contract information to a file.

#### `load_contract_info()`
Loads the smart contract information from a file.

#### `msg_permit()`
Generates a message to query a permit for the given contract address.

**Returns:** dict - A dictionary representing the transaction message

#### `signAmino(msg)`
Signs the given message using the wallet's private key.

**Parameters:**
- `msg`: The message to be signed

**Returns:** dict - A dictionary with keys 'pub_key' and 'signature'

#### `query_get_all()`
Queries all Cred using a prepared message and handles the response.

**Returns:** list - A list of Cred objects retrieved from the query response

#### `get_url_tx(tx_hash)` (static method)
Gets the URL for a given transaction hash.

**Parameters:**
- `tx_hash` (str): The transaction hash

**Returns:** str - The URL of the transaction on the blockchain explorer

#### `get_url_faucet()` (static method)
Gets the URL of the faucet.

**Returns:** str - The URL of the faucet where users can request tokens

## Note

This client is designed to work with a specific blockchain implementation. Ensure you have the correct environment variables and file paths set up before using this class.
