"""
This is a test script for connecting to a secret resource.
"""

import asyncio
import base64
import webbrowser
import os
import datetime
from dotenv import load_dotenv
import requests
from secret_sdk.client.lcd import AsyncLCDClient, LCDClient
from secret_sdk.client.lcd.api.tx import CreateTxOptions
from secret_sdk.core import Coins, TxResultCode
from secret_sdk.core.tx import StdFee
from secret_sdk.core.wasm import (MsgExecuteContract, MsgInstantiateContract,
                                  MsgStoreCode)
from secret_sdk.key.mnemonic import MnemonicKey
from secret_sdk.util.tx import get_value_from_raw_log
from secret_sdk.protobuf.cosmos.tx.v1beta1 import BroadcastMode

# definitions
MODE_TEST = True

load_dotenv()  # Load the .env file
#   create wallet from Mnemonic into .env file using secret-sdk-python library
mnemonic_phrase = os.getenv('MNEMONIC')
PATH_DATA = "contract"
PATH_WASM = os.path.join(PATH_DATA, "contract.wasm.gz")

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

secret = LCDClient(chain_id=chain_id, url=node_rest_endpoint)
print(secret)
print(secret.tendermint.block_info()['block']['header']['height'])

# test community_pool info :


async def main():
    async with AsyncLCDClient(url=node_rest_endpoint, chain_id=chain_id) as secret:
        community_pool = await secret.distribution.community_pool()
        print(community_pool)
        await secret.session.close()  # you must close the session
# This function runs the `main` coroutine using asyncio's event loop
asyncio.get_event_loop().run_until_complete(main())


# Create a new wallet using the mnemonic phrase
mnk = MnemonicKey(mnemonic=mnemonic_phrase)
wallet = secret.wallet(mnk)
print(wallet)

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


# Store the contract into local-secret node

# Store code : prepare tx
with open(PATH_WASM, "rb") as file:
    wasm_byte_code = file.read()
msg_store_code = MsgStoreCode(
    sender=wallet.key.acc_address,
    wasm_byte_code=wasm_byte_code,
    source="",
    builder="",
)
# Store code : Send tx
tx_store = wallet.create_and_broadcast_tx(
    [msg_store_code],
    gas='4000000',
    gas_prices=Coins('0.25uscrt')
)
# Store code : Check tx output
# print(tx_store)
if tx_store.code != TxResultCode.Success.value:
    raise Exception(f"Failed MsgStoreCode: {tx_store.raw_log}")
assert tx_store.code == TxResultCode.Success.value

# Instantiate contract : Prepare tx
code_id = int(get_value_from_raw_log(tx_store.rawlog, 'message.code_id'))
code_info = secret.wasm.code_info(code_id)
code_hash = code_info['code_info']['code_hash']

msg_init = MsgInstantiateContract(
    sender=wallet.key.acc_address,
    code_id=code_id,
    code_hash=code_hash,
    init_msg={"count": 0},
    label=f"counter {datetime.datetime.now()}",
    encryption_utils=secret.encrypt_utils,
)

# Instantiate contract : Send tx
tx_init = wallet.create_and_broadcast_tx(
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
contract_adress = get_value_from_raw_log(tx_init.rawlog, 'message.contract_address')
assert contract_adress == tx_init.data[0].address

# Execute increment : Prepare tx
msg_execute = MsgExecuteContract(
    sender=wallet.key.acc_address,
    contract=contract_adress,
    msg={"increment": {}},
    code_hash=code_hash,
    encryption_utils=secret.encrypt_utils,
)
# Execute increment : Send tx
tx_execute = wallet.create_and_broadcast_tx(
    [msg_execute],
    gas='5000000',
    gas_prices=Coins('0.25uscrt'),
)
# Execute increment : Check tx
if tx_execute.code != TxResultCode.Success.value:
    raise Exception(f"Failed MsgExecuteContract: {tx_execute.raw_log}")
assert tx_execute.code == TxResultCode.Success.value

# Execute increment async mode : Send tx
tx = wallet.create_and_broadcast_tx(
    [msg_execute],
    gas='5000000',
    gas_prices=Coins('0.25uscrt'),
    broadcast_mode=BroadcastMode.BROADCAST_MODE_ASYNC,
)
# Execute increment async mode : Check tx
tx_hash = tx.txhash
tx_execute_async = secret.tx.get_tx(tx_hash)
while tx_execute_async is None:
    tx_execute_async = secret.tx.get_tx(tx_hash)
if tx_execute_async.code != TxResultCode.Success.value:
    raise Exception(f"Failed MsgExecuteContract: {tx_execute_async.raw_log}")
assert tx_execute_async.code == TxResultCode.Success.value

# Query contract

res = secret.wasm.contract_query(
    contract_address=contract_adress,
    query={"get_count": {}},
    contract_code_hash=code_hash,
)
print(res)
assert res == {'count': 2}
