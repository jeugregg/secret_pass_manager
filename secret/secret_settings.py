"""
This is a test script for connecting to a secret resource.
"""
import webbrowser
import os
from dotenv import load_dotenv
import requests
import asyncio
# from secret_sdk.client.lcd import LCDClient
from secret_sdk.key.mnemonic import MnemonicKey
from secret_sdk.client.lcd import LCDClient

# definitions
MODE_TEST = True

load_dotenv()  # Load the .env file
#   create wallet from Mnemonic into .env file using secret-sdk-python library
MNEMONIC_PHRASE = os.getenv('MNEMONIC')
PATH_CONTRACT = "contract"
PATH_WASM = os.path.join(PATH_CONTRACT, "contract.wasm.gz")

chain_id_gitpod = "secretdev-1"
node_rest_endpoint_gitpod = "https://1317-scrtlabs-gitpodlocalsec-4ogk0hk9djs.ws-us116.gitpod.io"
faucet_endpoint_gitpod = "https://5000-scrtlabs-gitpodlocalsec-4ogk0hk9djs.ws-us116.gitpod.io"

chain_id_test = "pulsar-3"
node_rest_endpoint_test = "https://api.pulsar.scrttestnet.com"
faucet_endpoint_test = "https://faucet.pulsar.scrttestnet.com"


if MODE_TEST:
    chain_id = chain_id_test
    node_rest_endpoint = node_rest_endpoint_test
    faucet_endpoint = faucet_endpoint_test
else:
    chain_id = chain_id_gitpod
    node_rest_endpoint = node_rest_endpoint_gitpod
    faucet_endpoint = faucet_endpoint_gitpod

# secret = LCDClient(chain_id=chain_id, url=node_rest_endpoint)
# print(secret)
# print(secret.tendermint.block_info()['block']['header']['height'])


# Create a new wallet using the mnemonic phrase


def get_wallet(secret, mnemonic_phrase=MNEMONIC_PHRASE):
    mnk = MnemonicKey(mnemonic=mnemonic_phrase)
    wallet = secret.wallet(mnk)
    # Add fund in wallet
    if MODE_TEST:
        # check balance
        balance = secret.bank.balance(wallet.key.acc_address)
        if balance[0].get("uscrt").amount <= 0:
            # open navigator on the website faucet
            print("Add fund in wallet")
            print(f"Wallet address : {wallet.key.acc_address}")
            print("Open the website faucet and add fund to your wallet")
            print("https://faucet.pulsar.scrttestnet.com")
            # open website
            webbrowser.open(faucet_endpoint)
            # wait user to validate
            input("Press Enter to continue...")
            # check balance
            balance = secret.bank.balance(wallet.key.acc_address)
            assert balance[0].get("uscrt").amount > 0
            print(f"New balance : {balance[0].get("uscrt")}")
    else:
        url_faucet = f"{faucet_endpoint}/faucet?address={wallet.key.acc_address}"
        response_faucet = requests.get(url_faucet)
        print(response_faucet.text)
    return wallet


def get_client(mnemonic_phrase=MNEMONIC_PHRASE):
    """
    create secret client and wallet
    """
    # Créez une nouvelle boucle d'événements
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    # Initialisez le client
    secret = LCDClient(chain_id=chain_id, url=node_rest_endpoint)
    wallet = get_wallet(secret, mnemonic_phrase=mnemonic_phrase)
    return secret, wallet
