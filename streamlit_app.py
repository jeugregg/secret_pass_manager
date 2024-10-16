"""
Streamlit App : Password Manager with Secret Network Blockchain
DONE : 
    - interface
    - wallet display
TODO : 
    - add password to the blockchain
    - display passwords from the blockchain
"""
import streamlit as st
from secret_sdk.core import TxResultCode
from secret.client import Client
from cred.cred import Cred


@st.cache_resource
def get_secret_client():
    return Client(mode_update=False, mnemonic_phrase=st.secrets.MNEMONIC)


def get_balance():
    balance = client.secret.bank.balance(client.wallet.key.acc_address)
    return balance


def update_sidebar_balance():
    with st.spinner('Calculating balance...'):
        balance = get_balance()
    st.write(f"Balance: {balance[0]}")
    st.caption(f"Website faucet: {Client.get_url_faucet()}")
    st.session_state.balance = balance


def add_cred(my_cred):
    """
    add a Credential into the blockchain
    """
    # prepare data to be sent to secret network contract using function add_cred
    with st.sidebar:
        st.subheader("account")
        with st.status("Adding...", expanded=True) as status:
            st.write(f"name : {my_cred.name}")
            st.write(f"url : {my_cred.url}")
            st.write(f"email : {my_cred.email}")
            st.write(f"login : {my_cred.login}")
            st.write("password : ****")
            st.write(f"note : {my_cred.note}")
            st.write(f"shared_to : {my_cred.share}")
            # add to blockchain
            tx_execute = client.add(my_cred)
            if tx_execute.code != TxResultCode.Success.value:
                raise Exception(f"Failed MsgExecuteContract: {tx_execute.rawlog}")
            assert tx_execute.code == TxResultCode.Success.value
            st.success("Credential added to blockchain")
            status.update(label="Credential added!", state="complete", expanded=False)
            # status
            st.session_state.tx_add["update"] = True
            st.session_state.tx_add["status"] = "Credential added!"
            st.session_state.tx_add["tx"] = tx_execute
            if st.session_state.tx_add["tx"] is not None:
                st.write(Client.get_url_tx(st.session_state.tx_add["tx"].txhash))
            status.update(
                label=st.session_state.tx_add["status"],
                state="complete",
                expanded=True,
            )


def update_cred(index, my_cred):
    """
    Update a Credential into the blockchain
    """
    # prepare data to be sent to secret network contract using function add_cred
    with st.sidebar:
        with st.status("Updating...", expanded=True) as status:
            st.write(f"name : {my_cred.name}")
            st.write(f"url : {my_cred.url}")
            st.write(f"email : {my_cred.email}")
            st.write(f"login : {my_cred.login}")
            st.write("password : ****")
            st.write(f"note : {my_cred.note}")
            st.write(f"share : {my_cred.share}")
            if my_cred.to_dict() != st.session_state.list_cred[index].to_dict():
                # Update to blockchain
                with st.spinner('Updating Credential...'):
                    tx_execute = client.add(my_cred)
                if tx_execute.code != TxResultCode.Success.value:
                    raise Exception(f"Failed MsgExecuteContract: {tx_execute.rawlog}")
                assert tx_execute.code == TxResultCode.Success.value
                st.success("Credential updated to blockchain")
                status.update(label="Credential updated!", state="complete", expanded=True)
                st.session_state.list_cred[index] = my_cred
                # status
                st.session_state.tx_update["update"] = True
                st.session_state.tx_update["status"] = "Credential updated!"
                st.session_state.tx_update["tx"] = tx_execute

            else:
                st.warning("Nothing to Update!")
                status.update(label="Nothing to Update!", state="complete", expanded=True)
                st.session_state.tx_update["update"] = True
                st.session_state.tx_update["status"] = "Nothing to Update!"
                st.session_state.tx_update["tx"] = None

            status.update(
                label=st.session_state.tx_update["status"],
                state="complete",
                expanded=True,
            )

# init status


def initial_tx_status():
    return {
        "update": False,
        "status": "",
        "tx": None,
    }


@st.dialog("Create a new Vault")
def dialog_create_vault():
    st.markdown("**Create a new empty Vault ?**")
    if st.button("OK"):
        st.warning("Not implemented yet!")
    if st.button("Cancel"):
        st.warning("Not implemented yet!")


if st.session_state.get("tx_add") is None:
    st.session_state.tx_add = initial_tx_status()

if st.session_state.get("tx_update") is None:
    st.session_state.tx_update = initial_tx_status()

# Sidebar
with st.sidebar:
    st.title("Secret Password Manager")
    st.divider()
    # Connect to wallet
    client = get_secret_client()
    st.markdown(f"**Your Wallet** : {client.wallet.key.acc_address}")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Connect Wallet"):
            st.warning("Not implemented yet!")
    with col2:
        # add a button to check balance in sidebar
        if st.button("Check Balance"):
            update_sidebar_balance()

    st.markdown(f"**Your Secret Vault** : {client.contract_address}")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Connect Vault"):
            st.warning("Not implemented yet!")
    with col2:
        if st.button("Create"):
            dialog_create_vault()

    st.markdown(f"**Status**")
    # ADD check status
    if st.session_state.tx_add["update"]:
        add_cred(st.session_state.tx_add["cred_to_add"])
        # re-init
        st.session_state.tx_add = initial_tx_status()
    # UPDATE check status
    elif st.session_state.tx_update["update"]:
        update_cred(st.session_state.tx_add["index"], st.session_state.tx_add["my_cred_update"])
        # re-init
        st.session_state.tx_update = initial_tx_status()


# load data from BC
def load_cred():
    with st.spinner('Loading credentials...'):
        list_cred = client.query_get_all()
        st.session_state.list_cred = list_cred


load_cred()


if "list_cred" in st.session_state:
    list_cred = st.session_state.list_cred
else:
    list_cred = []

if "update_cred_button" not in st.session_state:
    st.session_state.update_cred_button = False


def click_update_cred(index):
    st.session_state.update_index = index
    st.session_state.update_cred_button = True


def update_credential(index, my_cred):
    with st.form(key=f'update_form_{index}', clear_on_submit=True):
        my_cred_update = Cred.mock()
        my_cred_update.name = st.text_input("name",  my_cred.name)
        my_cred_update.url = st.text_input("url",  my_cred.url)
        my_cred_update.email = st.text_input("email",  my_cred.email)
        my_cred_update.login = st.text_input("login",  my_cred.login)
        my_cred_update.password = st.text_input(
            "password", value=my_cred.password, type="password")
        my_cred_update.note = st.text_area("note",  my_cred.note)
        my_cred_update.share = st.text_input("share",  my_cred.share)

        if st.form_submit_button(label="Update"):
            st.session_state.tx_add["index"] = index
            st.session_state.tx_add["my_cred_update"] = my_cred_update
            st.session_state.tx_update["update"] = True
            st.rerun()


@st.dialog("Update Credential")
def dialog(my_cred):
    index = st.session_state.update_index
    update_credential(index, my_cred)


# st.title("Secret Password Manager")
with st.container(border=True):
    st.subheader("Your credentials")
    for i_row, cred in enumerate(list_cred):
        with st.container(border=True):
            with st.container():
                col1, col2, col3 = st.columns([4, 1, 1])
                # Display credential details
                with col1:
                    st.markdown(f"**Name**: {cred.name}")
                    st.markdown(f"**URL**: {cred.url}")
                # Add button to update this credential
                with col2:
                    if st.button("Edit", key=f'update_button_{i_row}'):
                        st.session_state.update_index = i_row
                        dialog(st.session_state.list_cred[i_row])
                with col3:
                    if st.button("Remove", key=f'remove_button_{i_row}'):
                        st.sidebar.warning("Not implemented yet!")


# ADD CRED

def click_add_cred():
    st.session_state.add_cred_button = True


if st.session_state.get("expanded") is None:
    st.session_state.expanded = False


# Add Cred Form to input information about your login credentials
def display_add_cred():
    with st.expander(
        "Add credentials",
        expanded=st.session_state.expanded,
        icon=":material/add_circle:"
    ):

        with st.form(key='add_cred', clear_on_submit=True):
            name = st.text_input("name")
            url = st.text_input("url")
            email = st.text_input("email")
            login = st.text_input("login")
            password = st.text_input("password", type="password")
            note = st.text_area("note")
            share = st.text_input("share")

            # create my new credential to add
            cred_to_add = Cred(
                name=name,
                url=url,
                email=email,
                login=login,
                password=password,
                note=note,
                share=share,
            )
            # add to session state cred_to_add
            st.session_state.cred_to_add = cred_to_add
            # add a button to save the credentials
            if st.form_submit_button(label="Add", type="primary"):
                st.session_state.tx_add["update"] = True
                st.session_state.tx_add["cred_to_add"] = cred_to_add
                if cred_to_add.isempty():
                    st.warning("No fields is filled")
                    st.session_state.tx_add["cred_to_add"] = None
                else:
                    st.session_state.tx_add["cred_to_add"] = cred_to_add
                st.session_state.expanded = False
                st.rerun()


display_add_cred()


st.caption("MIT license, Source: https://github.com/jeugregg/secret_pass_manager ")
