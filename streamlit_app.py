"""
Streamlit App : Password Manager with Secret Network Blockchain
DONE : 
    - interface
    - wallet display
TODO : 
    - add password to the blockchain
    - display passwords from the blockchain
"""
import os

import pandas as pd
import numpy as np
import streamlit as st

from secret.secret_settings import get_client


@st.cache_resource
def get_secret_client():
    return get_client(st.secrets.MNEMONIC)


def get_balance():
    balance = secret.bank.balance(wallet.key.acc_address)
    return balance


# get secret ressources
# secret, wallet = get_secret_client()
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
    """
    add a Credential into the blockchain
    """
    # prepare data to be sent to secret network contract using function add_cred
    st.write(f"name : {name}")
    st.write(f"url : {url}")
    st.write(f"username : {username}")
    st.write("password : ****")
    st.write(f"shared_to : {shared_to}")
    st.write(f"note : {note}")
    st.session_state.add_cred_button = False
    # TODO add to blockchain


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
