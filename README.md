# secret_pass_manager
Password manager using Secret Network Blockchain

## Overview

`secret_pass_manager` is a project that aims to provide a secure and private way to store your credentials (passwords, access keys, etc.) online using the Secret Network blockchain. The project leverages advanced security features of the blockchain, including confidential computing via SGX (Software Guard Extensions), to ensure that sensitive data remains encrypted and inaccessible to unauthorized parties.

## Context

This project was initiated during the Secret Network [HackSecret 4](https://dorahacks.io/hackathon/hacksecret4/detail) Hackathon by a data scientist without any knowlege in rust. Even the web UI is done with a python framework that I have never really used before.

## Video demo
- [Click here to watch](https://app.guidde.com/share/playbooks/2scuhL2Jtg1NrTvGkkSJRh)
- [Have a look to the markdown guide](/docs/doc_video_guide.md)
## Demo on line 
- Follow this [link on streamlit cloud](/docs/doc_streamlit_app.md#demo-on-line)

## Architecture

The architecture of the project consists of several components:

1. **Smart Contract**: A smart contract written in Rust is deployed on the Secret Network. This contract manages the storage, retrieval, and manipulation of credentials.
2. **Web Application**: A web application built with Streamlit (a Python framework for building data apps) that interacts with the smart contract. The app provides a user-friendly interface to manage your credentials securely.
3. **Client Library**: Python scripts (`client.py`) that interact with the smart contract and provide necessary functionality, such as querying permits for blockchain transactions.

## Features

### Smart Contract

The smart contract is designed to:

- Store credentials securely on the blockchain using the Secret Network's confidential computing capabilities (SGX).
- Allow only the owner of the credentials to reset or modify them.
- Provide a mechanism for querying and retrieving stored credentials.

- Documentation : 
    - [contract.rs](docs/doc_contract.md)
    - [msg.rs](docs/doc_contract_msg.md)
    - [state.rs](docs/doc_contract_state.md)

### Web Application

The web application provides:

- A user interface to add, view, and manage your credentials.
- Interactivity through Streamlit's components and event handling.
- Integration with the smart contract via Python scripts (`client.py`).

- Documentation : 
    - [streamlit_app.py](docs/doc_streamlit_app.md)

### Client Library

The client library includes:

- Functions for interacting with the smart contract, such as querying permits and managing transactions.
- Utility functions to handle blockchain operations.

- Documentation : 

    - [secret/client.py](docs/doc_client.md)
    - [test_client.py](docs/doc_test_client.md)
    - [secret/secret_settings.py](docs/doc_client.md) 
    - [cred/cred.py](docs/doc_cred.md)

## Getting Started

### Prerequisites

To run this project, you will need:

- Python 3.8 or higher (to be check 3.12 is used during dev)
- For dev : Rust (for compiling the smart contract)
- Access to a Secret Network testnet or mainnet
- Streamlit installed

### Installation for used-end user
- Follow the [Client installation](/docs/doc_streamlit_app.md#installation)

### Installation for development

1. **Install dev env**: check this [Secret Network tutorial]( https://docs.scrt.network/secret-network-documentation/development/readme-1/setting-up-your-environment) 
    - by default the projet is on testnet `pulsar-3`
2. **Clone the Repository**: Clone this repository to your local machine.
3. **Install the python env**: Follow the [Client installation](/docs/doc_streamlit_app.md#installation)
3. **Compile the Smart Contract**:
   ```sh
   cd contract
   cargo build --release
   ```
4. **Deploy the Smart Contract**: Deploy the compiled smart contract on the Secret Network testnet or mainnet : you can use the [Client.py documentation](/docs/doc_client.md)

5. **Run the Web Application**:
   ```sh
   streamlit run streamlit_app.py
   ```

## Configuration

The project includes configuration files such as:
-  `contract_info.txt` [details](docs/doc_client.md#create_contract), 
- `requirements.txt` for Python installation, 
- 2 Mnemonic files (look here : [Web app doc](docs/doc_streamlit_app.md#installation)). 

Ensure that these files are properly configured to interact with your Secret Network environment.


## Development Deepdive 

The development of this codebase was a collaborative effort (with myself ;-)) aimed at creating a smart contract for managing credentials, which could interact with both blockchain and a frontend application. The contract, defined in `contract.rs`, is written in Rust and utilizes the Cosmos SDK's CosmWasm framework for building applications on Tendermint-based blockchains.

The contracts' primary functions include initializing, executing, querying, and interacting with the smart contract. `instantiate` sets up the initial state of the contract, while `execute` handles actions like adding credentials. The `query` function allows for retrieving credential information.

The contracts interact through messages (`ExecuteMsg`) and responses. When querying the counter's value, the `query_count` function loads the current count from storage and returns it as part of a response.

The design choices include leveraging Rust for performance and safety, adhering to CosmWasm standards for blockchain-specific functionalities, and keeping the contract logic clear and modular. This approach facilitates testing and maintenance.

For testing, we use `test_client.py`, which simulates the entire workflow from deploying the contract to interacting with it via a client. The client (`client.py`) manages the contract's lifecycle, including storing the code, instantiating it, and saving crucial information such as the contract address and initial count.

The frontend, managed by `streamlit_app.py`, interacts with the smart contract through the client. It provides a user interface for interacting with the blockchain application, allowing users to perform actions like  managing his credentials.

Overall, this development process involved a blend of backend Rust logic and frontend Python interaction, showcasing a comprehensive approach to developing, deploying, and managing smart contracts on a blockchain.

## TODO

The TODO list for the `secret_pass_manager` project includes several enhancements and new features that were not fully implemented due to time constraints. The primary areas of focus are:

1. **Web UI Development**: The current web application is still under development, with specific functionalities like contract creation and wallet connection using Keplr support in Python yet to be completed.

2. **Smart Contract Enhancements**:
   - Currently, the smart contract only allows for storing a single credential. Future updates will add the capability to store multiple credentials.
   
3. **Feature Additions**:
   - **Credential Sharing**: Implementing functionality that allows users to share their credentials securely with others.
   - **Desktop Application**: Developing a desktop application version of the web app, enhancing usability and accessibility for non-web-based users.
   - **Keychain Support**: Adding the capability to store private keys in the user's local keychain device, ensuring enhanced security and convenience.
   - **Multi-User Vault Contract**: Creating a multi-user vault contract that can be used by organizations to manage credentials collectively.

These features are essential for making the project more comprehensive and usable. By addressing these TODO items, the project aims to become a more robust and versatile tool for managing sensitive information securely on the Secret Network blockchain.

## License

This software is licensed under the MIT license. See the [LICENSE](LICENSE) file for full disclosure.

For more information on using the Secret Network blockchain and its features, refer to the official [Secret Network documentation](https://docs.secret.network/).