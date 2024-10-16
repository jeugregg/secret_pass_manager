# Contract messages

This Rust file (`msg.rs`) contains message definitions for a secret pass manager contract. It includes messages for instantiation, execution, and querying of the contract.

## Imports

```rust
use cosmwasm_std::Addr;
use schemars::JsonSchema;
use serde::{Deserialize, Serialize};
use secret_toolkit::permit::Permit;
use crate::state::Cred;
```

### `cosmwasm_std::Addr`

- Represents an address on the Cosmos blockchain.

### `schemars::JsonSchema`

- Allows for schema generation of JSON data structures.

### `serde::{Deserialize, Serialize}`

- Enables serialization and deserialization of Rust structs to and from JSON format.

### `secret_toolkit::permit::Permit`

- A structure used for authenticating queries with permissions.

### `crate::state::Cred`

- Represents a credential stored within the contract's state.

## Messages

### Instantiate Message

```rust
/// Instantiate message for the secret pass manager contract.
///
/// This message is used to initialize the contract with a starting count.
#[derive(Serialize, Deserialize, Clone, Debug, Eq, PartialEq, JsonSchema)]
pub struct InstantiateMsg {
    pub count: i32,
}
```

- **Purpose**: Initializes the contract with a starting count value.

### Execute Messages

```rust
/// Execute messages for the secret pass manager contract.
///
/// These messages are used to interact with and modify the state of the contract.
#[derive(Serialize, Deserialize, Clone, Debug, Eq, PartialEq, JsonSchema)]
#[serde(rename_all = "snake_case")]
pub enum ExecuteMsg {
    /// Increment the count by 1.
    Increment {},
    /// Reset the count to a specified value.
    Reset { count: i32 },
    /// Add a new credential to the contract.
    Add { credential: Cred},
}
```

- **Purpose**: Defines various actions that can be performed on the contract:
  - `Increment`: Increases the count by 1.
  - `Reset`: Sets the count to a specified value.
  - `Add`: Adds a new credential to the contract.

### Query Messages

```rust
/// Query messages for the secret pass manager contract.
///
/// These messages are used to retrieve data from the contract.
#[derive(Serialize, Deserialize, Clone, Debug, Eq, PartialEq, JsonSchema)]
#[serde(rename_all = "snake_case")]
pub enum QueryMsg {
    /// GetCount returns the current count as a json-encoded number
    GetCount {},
    /// Retrieve all credentials associated with a given wallet address.
    GetAll {
        /// The wallet address to retrieve credentials for
        wallet: Addr,
         /// A permit to authenticate the query request.
        permit: Permit,
        /// An index to paginate through the results.
        index: u8,
    },
}
```

- **Purpose**: Defines methods to query data from the contract:
  - `GetCount`: Returns the current count value.
  - `GetAll`: Retrieves all credentials associated with a given wallet address, including pagination.

### Responses

#### GetCount Response

```rust
/// Response for the `GetCount` query message.
///
/// This response contains the current count value.
#[derive(Serialize, Deserialize, Clone, Debug, Eq, PartialEq, JsonSchema)]
pub struct CountResponse {
    pub count: i32,
}
```

- **Purpose**: Contains the response to a `GetCount` query.

#### GetAll Response

```rust
/// Response for the `GetAll` query message.
///
/// This response contains a vector of credentials associated with a wallet address.
#[derive(Serialize, Deserialize, Clone, Debug, Eq, PartialEq, JsonSchema)]
pub struct CredListResponse {
    pub vect_cred: Vec<Cred>,
}
```

- **Purpose**: Contains the response to a `GetAll` query, returning a list of credentials.