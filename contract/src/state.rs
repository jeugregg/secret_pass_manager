use schemars::JsonSchema;
use serde::{Deserialize, Serialize};

use cosmwasm_std::{Addr, Storage};
use cosmwasm_storage::{singleton, singleton_read, ReadonlySingleton, Singleton};

pub static CONFIG_KEY: &[u8] = b"config";

#[derive(Serialize, Deserialize, Clone, Debug, Eq, PartialEq, JsonSchema)]
pub struct State {
    pub count: i32,
    pub owner: Addr,
}

pub fn config(storage: &mut dyn Storage) -> Singleton<State> {
    singleton(storage, CONFIG_KEY)
}

pub fn config_read(storage: &dyn Storage) -> ReadonlySingleton<State> {
    singleton_read(storage, CONFIG_KEY)
}

// One singleton per Credentials information & just use index to identify the credential
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

pub fn config_cred<'a>(storage: &'a mut dyn Storage, index: &[u8]) -> Singleton<'a, Cred> {
    singleton(storage, index)
}

pub fn config_cred_read<'a>(storage: &'a dyn Storage, index: &[u8]) -> ReadonlySingleton<'a, Cred> {
    singleton_read(storage, index)
}