"""
Streamlit App
Import CSV file
Display a table
Display a dataframe
DONE : - test to identify data to anoymize (replace by XXXX)
    - save data anon
    - undo-anon  all 
TODO : 
    - use a bool dataframe to specify if public/private instead of replace by XXXX
    - colorize cells anonymized
    - correct issue when undo all : coll + some values in another coll
    - undo-anon only selected cells
"""

import streamlit as st
import asyncio
import pandas as pd
import os
import numpy as np
from secret_sdk.client.lcd import LCDClient
from secret.secret_settings import chain_id
from secret.secret_settings import node_rest_endpoint
from secret.secret_settings import get_wallet


@st.cache_resource
def get_secret_client():
    """
    create secret client and wallet
    """
    # Créez une nouvelle boucle d'événements
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    # Initialisez le client
    secret = LCDClient(chain_id=chain_id, url=node_rest_endpoint)
    wallet = get_wallet(secret, mnemonic_phrase=st.secrets.MNEMONIC)
    return secret, wallet


def get_balance():
    balance = secret.bank.balance(wallet.key.acc_address)
    return balance


# get secret ressources
secret, wallet = get_secret_client()

# Utilisez wallet comme nécessaire
# st.write(f"Wallet address: {wallet.key.acc_address}")
str_print = f"Wallet connected : {wallet.key.acc_address}"
st.sidebar.markdown(str_print)

# add a button to check balance in sidebar
if st.sidebar.button("Check Balance"):
    with st.spinner('Calculating balance...'):
        balance = get_balance()
    st.sidebar.write(f"Balance: {balance}")

# definitions
PATH_DATA = "data"
# constants
MODE_TEST = True


def add_cred():
    # prepare data to be sent to secret network contract using function add_cred
    st.write(f"name : {name}")
    st.write(f"url : {url}")
    st.write(f"username : {username}")
    st.write("password : ****")
    st.write(f"shared_to : {shared_to}")
    st.write(f"note : {note}")
    st.session_state.add_cred_button = False


def click_add_cred():
    st.session_state.add_cred_button = True


# form to input information about your login creadentials
with st.form(key='add_cred'):
    name = st.text_input("Name")
    url = st.text_input("URL")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    shared_to = st.text_input("Shared to")
    note = st.text_area("Note")
    # create dict credentials
    cred_to_add = {
        'name': name,
        'url': url,
        'username': username,
        'password': password,
        'shared_to': shared_to,
        'note': note,
    }
    # add to session state cred_to_add
    st.session_state.cred_to_add = cred_to_add
    # add a button to save the credentials
    add_cred_button = st.form_submit_button(
        label="Save",
        on_click=click_add_cred,
    )

if "add_cred_button" not in st.session_state:
    st.session_state.add_cred_button = False


if st.session_state.add_cred_button:
    if name and url and username and password:
        add_cred()
    else:
        st.warning("Please fill all fields")
        add_cred()
