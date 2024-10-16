# State Management for Secret Vault Smart Contract

This Rust file (`state.rs`) defines the state structures and storage management functions for a password manager secret vault smart contract on the Secret Network.

## Imports

```rust
use schemars::JsonSchema;
use serde::{Deserialize, Serialize};
use cosmwasm_std::{Addr, Storage};
use cosmwasm_storage::{singleton, singleton_read, ReadonlySingleton, Singleton};
```

## State Structures

### State

```rust
#[derive(Serialize, Deserialize, Clone, Debug, Eq, PartialEq, JsonSchema)]
pub struct State {
    pub count: i32,
    pub owner: Addr,
}
```

This structure represents the main state of the contract, including:
- `count`: An integer counter
- `owner`: The address of the contract owner

### Cred

```rust
#[derive(Serialize, Deserialize, Clone, Debug, Eq, PartialEq, JsonSchema)]
pub struct Cred {
    pub name: String,
    pub url: String,
    pub email: String,
    pub login: String,
    pub password: String,
    pub note: String,
    pub share: String,
}
```

This structure represents a single credential entry, containing:
- `name`: Name of the credential
- `url`: Associated URL
- `email`: Email address
- `login`: Login username
- `password`: Password (stored securely)
- `note`: Additional notes
- `share`: Sharing information

## Storage Management

### Main State

```rust
pub static CONFIG_KEY: &[u8] = b"config";

pub fn config(storage: &mut dyn Storage) -> Singleton<State> {
    singleton(storage, CONFIG_KEY)
}

pub fn config_read(storage: &dyn Storage) -> ReadonlySingleton<State> {
    singleton_read(storage, CONFIG_KEY)
}
```

These functions manage the storage of the main `State` structure:
- `config`: Returns a writable `Singleton` for the main state
- `config_read`: Returns a read-only `Singleton` for the main state

### Credential Storage

```rust
pub fn config_cred<'a>(storage: &'a mut dyn Storage, index: &[u8]) -> Singleton<'a, Cred> {
    singleton(storage, index)
}

pub fn config_cred_read<'a>(storage: &'a dyn Storage, index: &[u8]) -> ReadonlySingleton<'a, Cred> {
    singleton_read(storage, index)
}
```

These functions manage the storage of individual `Cred` structures:
- `config_cred`: Returns a writable `Singleton` for a specific credential
- `config_cred_read`: Returns a read-only `Singleton` for a specific credential

Each credential is stored as a separate singleton, identified by an index.

## Constants

```rust
pub const PREFIX_REVOKED_PERMITS: &str = "revoked_permits"
```

This constant defines a prefix for storing revoked permits, which can be used for access control management.

## Usage

This file provides the necessary structures and functions to manage the state of the secret vault smart contract. It allows for storing and retrieving the main contract state, as well as individual credential entries. The use of singletons ensures efficient and secure storage management within the Secret Network ecosystem.
