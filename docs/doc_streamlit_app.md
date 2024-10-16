# Secret Password Manager Client
### with Streamlit and Secret Network Blockchain

This application allows you to manage your passwords securely using the Secret Network blockchain. The interface provides a simple way to add, update, and view credentials while keeping them encrypted on the blockchain.

## Table of Contents
- [Demo on line](#demo-on-line)
- [Installation](#installation)
- [Usage](#usage)
  - [Adding Credentials](#adding-credentials)
  - [Updating Credentials](#updating-credentials)
  - [Viewing Credentials](#viewing-credentials)
- [TODO](#todo)

## Demo on line 
- Follow this link for a [demo on streamlit cloud](https://jeugregg-secret-pass-manager-streamlit-app-9logha.streamlit.app/)  
## Installation
This part explain how to install all from scratch for using it with your private key

1. **Install Dependencies**:
    ```sh
    pip install -r requirements.txt 
    ```

2. **Set Up Secrets**:
   - Create a `.streamlit/secrets.toml` file (for Streamlit app deployment):
     ```toml
     MNEMONIC="your new mnemonic phrase here"
     ```
    - [Optionnal] for dev  
        - Create a `.env` file in your project root (for testing purposes).
        - Add your MNEMONIC to the `.env` file:
            ```
            MNEMONIC="your new mnemonic phrase here"
            ```

3. [Optional] For dev or issue with a new private key  
Explanation : If you use your own private key, you will need to create a new vault for your personal credentials.
For that purpose, the web interface can do it by itself but can have issue (need to be fixed). 
In the meanwhile, you can use this procedure to solve le issue before launching the web UI. 
- Use the `create_contract` method:
   - In your Python script, import the Client class:
     ```python
     from client import Client
     ```
   - Initialize the client with your new mnemonic:
     ```python
     client = Client(mode_update=True, mnemonic_phrase=None)  # It will use the MNEMONIC from .env or secrets.toml
     ```
   - Call the `create_contract` method:
     ```python
     client.create_contract()
     ```

4. Automatic Save of the contract information:
   - After successful creation, the contract address and other details will be saved automatically.
   - You can access the contract address using `client.contract_address`.

## Important Notes

- Always keep your mnemonic phrase secure and never share it.
- The `mode_update=True` parameter ensures a new contract is created.
- Make sure you have sufficient funds in your wallet for contract deployment.
- For Streamlit deployment, use the `.streamlit/secrets.toml` file and access the mnemonic with `st.secrets.MNEMONIC`.

By following these steps, you'll create your first vault on the Secret Network blockchain using the `create_contract` method from `client.py`.


## Usage

### Adding Credentials

1. **Open the Streamlit App**:
    Run the script to start the app:
    ```sh
    streamlit run streamlit_app.py
    ```

2. **Add Credentials Form**:
    - Navigate to the "Add credentials" section.
    - Fill in all required fields: name, URL, email, login, password, note, and share.
    - Click the "Save" button to add the credential to the blockchain.

### Updating Credentials

1. **Edit Credentials**:
    - Go to the "List credentials" section.
    - Click the "Edit" button next to the credential you want to update.
    - A dialog will open where you can modify the details of the credential.
    - Click the "Update" button in the dialog to save changes.

### Viewing Credentials

1. **View Credentials List**:
    - Navigate to the "List credentials" section.
    - The app will display a list of all stored credentials with their names and URLs.
    - Click the "Edit" button next to any credential to view or update its details.

## TODO

- Add multi credentials to the blockchain
- Connect with Keplr wallet extension
- Create a new secret vault Button logic
- Connect vault button logic

---

This documentation should provide a clear overview of how to use your Streamlit application for managing passwords on the Secret Network blockchain.