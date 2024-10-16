/// This module contains the definitions and functions related to state management in the secret pass manager contract.
///
/// It includes configurations and credentials, providing a structured way to store and retrieve data persistently using CosmWasm's storage system.
use schemars::JsonSchema;
use serde::{Deserialize, Serialize};

use cosmwasm_std::{Addr, Storage};
use cosmwasm_storage::{singleton, singleton_read, ReadonlySingleton, Singleton};

/// The key used for storing the configuration in the contract's storage.
pub static CONFIG_KEY: &[u8] = b"config";

/// Represents the state of the secret pass manager contract, including a count and an owner.
///
/// This structure is serialized and deserialized using serde and stored persistently in the blockchain.
#[derive(Serialize, Deserialize, Clone, Debug, Eq, PartialEq, JsonSchema)]
pub struct State {
    /// The current count value.
    pub count: i32,
    /// The address of the contract owner.
    pub owner: Addr,
}

/// Retrieves a mutable singleton handle for the contract's configuration.
///
/// This function takes a mutable reference to a storage implementation and returns a Singleton handle that can be used
/// to read and write the configuration data persistently in the blockchain.

pub fn config(storage: &mut dyn Storage) -> Singleton<State> {
    singleton(storage, CONFIG_KEY)
}

/// Retrieves a read-only singleton handle for the contract's configuration.
///
/// This function takes a reference to a storage implementation and returns a ReadonlySingleton handle that can be used
/// to read the configuration data persistently in the blockchain without being able to modify it.
pub fn config_read(storage: &dyn Storage) -> ReadonlySingleton<State> {
    singleton_read(storage, CONFIG_KEY)
}

/// Represents a credential entry in the secret pass manager contract.
///
/// This structure is serialized and deserialized using serde and stored persistently in the blockchain. Each credential
/// can be identified by an index.
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

/// Retrieves a mutable singleton handle for a credential based on an index.
///
/// This function takes a mutable reference to a storage implementation and an index, returning a Singleton handle that
/// can be used to read and write the credential data persistently in the blockchain.
pub fn config_cred<'a>(storage: &'a mut dyn Storage, index: &[u8]) -> Singleton<'a, Cred> {
    singleton(storage, index)
}

/// Retrieves a read-only singleton handle for a credential based on an index.
///
/// This function takes a reference to a storage implementation and an index, returning a ReadonlySingleton handle that
/// can be used to read the credential data persistently in the blockchain without being able to modify it.
pub fn config_cred_read<'a>(storage: &'a dyn Storage, index: &[u8]) -> ReadonlySingleton<'a, Cred> {
    singleton_read(storage, index)
}

/// A constant prefix used for storing revoked permits.
///
/// This prefix is intended to be used in conjunction with a key-value store to manage and track revoked permissions
/// within the contract's state.
pub const PREFIX_REVOKED_PERMITS: &str = "revoked_permits";