# Secret Network Settings Module

This module is responsible for setting up and managing Secret Network settings and client. It includes functions for creating a wallet, getting a client, and handling faucet operations.

## Configuration

### Constants

- `MODE_TEST`: Boolean flag to determine if the application is running in test mode.
- `PERMIT_NAME`: Name of the permit used for viewing credentials.
- `MNEMONIC_PHRASE`: Mnemonic phrase loaded from environment variables.
- `PATH_CONTRACT`: Path to the contract directory.
- `PATH_WASM`: Path to the WebAssembly contract file.
- `PATH_INFO`: Path to the contract information file.
- `PATH_PERMIT`: Path to the permit JSON file.

### Network Settings

The module defines settings for both test and GitPod environments:

- Chain IDs
- Node REST endpoints
- Faucet endpoints
- Explorer endpoints

The active settings are determined by the `MODE_TEST` flag.

## Functions

### `get_wallet(secret, mnemonic_phrase=MNEMONIC_PHRASE)`

Creates a wallet using the provided mnemonic phrase and adds funds if necessary.

#### Parameters:
- `secret`: The Secret client instance.
- `mnemonic_phrase` (str, optional): The mnemonic phrase used to create the wallet. Defaults to `MNEMONIC_PHRASE`.

#### Returns:
- A Wallet object.

#### Behavior:
- Checks the wallet balance.
- In test mode, prompts the user to add funds via a faucet if the balance is zero.
- In non-test mode, automatically requests funds from the faucet.

### `get_client(mnemonic_phrase=MNEMONIC_PHRASE)`

Creates a Secret client and wallet.

#### Parameters:
- `mnemonic_phrase` (str, optional): The mnemonic phrase used to create the wallet. Defaults to `MNEMONIC_PHRASE`.

#### Returns:
- A tuple containing the Secret client and wallet.

#### Behavior:
- Creates a new event loop.
- Initializes the Secret client with the appropriate chain ID and node REST endpoint.
- Calls `get_wallet()` to create and fund the wallet.

## Dependencies

- `os`: For environment variable handling.
- `webbrowser`: For opening the faucet website.
- `asyncio`: For asynchronous operations.
- `requests`: For making HTTP requests to the faucet.
- `dotenv`: For loading environment variables from a .env file.
- `secret_sdk.client.lcd.LCDClient`: For creating the Secret Network client.
- `secret_sdk.key.mnemonic.MnemonicKey`: For creating a wallet from a mnemonic phrase.

## Usage

To use this module, ensure that the required environment variables are set, particularly the `MNEMONIC` variable. The module will automatically load these from a .env file if present.