# Secret Network Credential Vault

This Rust file (`contract.rs`)  provides a secure way to store and manage credentials on the Secret Network. It leverages the Secret Network's built-in privacy features and the Permit system to ensure that only the owner of the contract can access and modify the credentials.

## Contract Overview

The contract has the following features:

- **Credential Storage:**  Stores encrypted credentials in a secure manner.
- **Owner-Only Access:** Only the contract owner can add, read, or delete credentials.
- **Permit-Based Authorization:**  Uses permits to control access to credentials, enabling fine-grained permission management.
- **Privacy-Preserving:** Takes advantage of the Secret Network's privacy features to keep credentials confidential.

## Contract Structure

The contract comprises several key components:

- **`instantiate` function:** Initializes the contract with the owner's address and an optional initial count.
- **`execute` function:** Handles messages to modify the contract state, such as adding new credentials.
- **`query` function:** Handles queries to retrieve information from the contract state, such as getting all credentials or the current count.
- **`try_increment` function:** Increments an internal counter (used for testing and demonstration).
- **`try_reset` function:** Resets the internal counter to a specified value (used for testing and demonstration).
- **`try_add` function:** Adds a new credential to the contract.
- **`query_count` function:** Retrieves the current value of the internal counter.
- **`get_all` function:** Retrieves all credentials stored in the contract for a given wallet, validated by a permit.

## Entry Points

The contract defines the following entry points:

- **`instantiate`**: Initializes the contract with the owner and initial count.
- **`execute`**: Executes messages to modify the contract state.
- **`query`**: Queries the contract state.

### `instantiate`

```rust
#[entry_point]
pub fn instantiate(
    deps: DepsMut,
    _env: Env,
    info: MessageInfo,
    msg: InstantiateMsg,
) -> StdResult<Response> {
    let state = State {
        count: msg.count,
        owner: info.sender.clone(),
    };

    deps.api
        .debug(format!("Contract was initialized by {}", info.sender).as_str());
    config(deps.storage).save(&state)?;

    Ok(Response::default())
}
```
This function sets up the initial state of the contract, saving the owner's address and the initial count to storage.

**execute**

```rust
#[entry_point]
pub fn execute(deps: DepsMut, env: Env, info: MessageInfo, msg: ExecuteMsg) -> StdResult<Response> {
    match msg {
        ExecuteMsg::Increment {} => try_increment(deps, env),
        ExecuteMsg::Reset { count } => try_reset(deps, info, count),
        ExecuteMsg::Add { credential } => try_add(deps, info, credential),
    }
}
```
This function handles execution messages. It dispatches the message to the appropriate function based on the ExecuteMsg variant:

- Increment: Increments an internal counter.
- Reset: Resets the internal counter to a specific value.
- Add: Adds a new credential to the contract.

**query**
```rust
#[entry_point]
pub fn query(deps: Deps, env: Env, msg: QueryMsg) -> StdResult<QueryResponse> {
    match msg {
        QueryMsg::GetCount {} => to_binary(&query_count(deps)?),
        QueryMsg::GetAll { wallet, permit, index } => to_binary(&get_all(deps, env, wallet, permit, index)?),
    }
}
```

This function handles query messages. It dispatches the message to the appropriate function based on the QueryMsg variant:

- GetCount: Returns the current value of the internal counter.
- GetAll: Returns all credentials associated with a specific wallet, validated by a permit.

## Functions



### get_all

```rust
fn get_all(
    deps: Deps,
    env: Env,
    wallet: Addr,
    permit: Permit,
    index: u8,
) -> StdResult<CredListResponse> {

    let contract_address = env.contract.address;
    let viewer = validate(
        deps,
        PREFIX_REVOKED_PERMITS,
        &permit,
        contract_address.to_string(),
        None,
    )?;

    let state = config_read(deps.storage).load()?;

    if wallet != state.owner {
        return Err(StdError::generic_err("Only the owner add Credential"));
    }
    if viewer != state.owner {
        return Err(StdError::generic_err("Only the owner add Credential"));
    }
    let index_conf = b"0"; // Convert the integer to a byte slice
    let credential = config_cred_read(deps.storage, index_conf).load()?;
    Ok(CredListResponse { 
        vect_cred: vec![credential]
    })
} 
```

Retrieves all credentials associated with a specific wallet. The function verifies that the caller has the necessary permissions based on the provided permit. Only the contract owner can retrieve credentials.



# Testing

The contract includes unit tests to verify its functionality. The tests cover scenarios such as:

## Initialization
- Verifying that the contract is initialized correctly.

## Adding Credentials
- Testing the `try_add` function, ensuring that only the owner can add credentials.

## Retrieving Credentials
- Testing the `get_all` function, confirming that it retrieves the correct credentials and that only the owner can access them.

## Permit Validation
- Testing the permit validation mechanism, ensuring that unauthorized users cannot access credentials.

# Usage

To use the credential vault contract:

1. **Deploy the Contract**: Deploy the compiled contract bytecode to the Secret Network.
2. **Set Up Owner**: The contract needs an owner, which will be the only entity with read/write permissions.
3. **Add Credentials**: The owner can use the `Add` execution message to store new credentials in the vault.
4. **Retrieve Credentials**: The owner can use the `GetAll` query message with a valid permit to retrieve their stored credentials.

# Security Considerations

- **Key Management**: The contract currently stores credentials directly. For enhanced security, consider implementing a more robust key management system, such as using encryption keys stored in a separate contract or using threshold cryptography.
- **Permit Revocation**: Implement a mechanism to revoke permits, ensuring that access to credentials can be revoked if necessary.
- **Auditing**: Regularly audit the contract's code and logic to identify potential vulnerabilities.

> **Disclaimer**: This documentation is for informational purposes only and should not be considered as legal or financial advice. It is recommended to consult with a qualified professional for any legal or financial matters.
