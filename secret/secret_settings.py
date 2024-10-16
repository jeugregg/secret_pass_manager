"""
Module for setting up and managing Secret Network settings and client.
This module includes functions for creating a wallet, getting a client,
and handling faucet operations.
"""
import os
import webbrowser

import asyncio
import requests
from dotenv import load_dotenv


from secret_sdk.client.lcd import LCDClient
from secret_sdk.key.mnemonic import MnemonicKey
# definitions
MODE_TEST = True
PERMIT_NAME = "view_cred"
load_dotenv()  # Load the .env file

# Create wallet from Mnemonic into .env file using secret-sdk-python library
MNEMONIC_PHRASE = os.getenv('MNEMONIC')
PATH_CONTRACT = "contract"
PATH_WASM = os.path.join(PATH_CONTRACT, "contract.wasm.gz")
PATH_INFO = "contract_info.txt"
PATH_PERMIT = "permit.json"

# Chain ID and endpoint configuration
chain_id_gitpod = "secretdev-1"
node_rest_endpoint_gitpod = "https://1317-scrtlabs-gitpodlocalsec-4ogk0hk9djs.ws-us116.gitpod.io"
faucet_endpoint_gitpod = "https://5000-scrtlabs-gitpodlocalsec-4ogk0hk9djs.ws-us116.gitpod.io"
explorer_endpoint_gitpod = "TO BE UPDATED"

chain_id_test = "pulsar-3"
node_rest_endpoint_test = "https://api.pulsar.scrttestnet.com"
faucet_endpoint_test = "https://faucet.pulsar.scrttestnet.com"
explorer_endpoint_test = "https://testnet.ping.pub/secret/tx/"

# Determine the chain ID and endpoint based on the mode
if MODE_TEST:
    chain_id = chain_id_test
    node_rest_endpoint = node_rest_endpoint_test
    faucet_endpoint = faucet_endpoint_test
    explorer_endpoint = explorer_endpoint_test
else:
    chain_id = chain_id_gitpod
    node_rest_endpoint = node_rest_endpoint_gitpod
    faucet_endpoint = faucet_endpoint_gitpod
    explorer_endpoint = explorer_endpoint_gitpod


def get_wallet(secret, mnemonic_phrase=MNEMONIC_PHRASE):
    """
    Creates a wallet using the provided mnemonic phrase and adds funds if necessary.

    Args:
        secret: The Secret client instance.
        mnemonic_phrase (str): The mnemonic phrase used to create the wallet. Defaults to MNEMONIC_PHRASE.

    Returns:
        A Wallet object.
    """
    mnk = MnemonicKey(mnemonic=mnemonic_phrase)
    wallet = secret.wallet(mnk)

    # Check and add funds if necessary
    balance = secret.bank.balance(wallet.key.acc_address)
    if MODE_TEST:
        if balance[0].get("uscrt").amount <= 0:
            print("Add fund in wallet")
            print(f"Wallet address : {wallet.key.acc_address}")
            print("Open the website faucet and add fund to your wallet")
            print("https://faucet.pulsar.scrttestnet.com")
            webbrowser.open(faucet_endpoint)
            input("Press Enter to continue...")
            balance = secret.bank.balance(wallet.key.acc_address)
            assert balance[0].get("uscrt").amount > 0
            print(f"New balance : {balance[0].get('uscrt')}")
    else:
        url_faucet = f"{faucet_endpoint}/faucet?address={wallet.key.acc_address}"
        response_faucet = requests.get(url_faucet)
        print(response_faucet.text)

    return wallet


def get_client(mnemonic_phrase=MNEMONIC_PHRASE):
    """
    Create a Secret client and wallet.

    Returns:
        A tuple containing the Secret client and wallet.
    """
    # Create a new event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Initialize the client
    secret = LCDClient(chain_id=chain_id, url=node_rest_endpoint)

    # Get the wallet using the provided mnemonic phrase or the default one
    wallet = get_wallet(secret, mnemonic_phrase=mnemonic_phrase)

    return secret, wallet
