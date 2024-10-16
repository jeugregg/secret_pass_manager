use cosmwasm_std::Addr;
use cosmwasm_std::{
    entry_point, to_binary, Deps, DepsMut, Env, MessageInfo, QueryResponse, Response, StdError, StdResult
};
use secret_toolkit::permit::validate;
use secret_toolkit::permit::Permit;
use crate::msg::{CountResponse, ExecuteMsg, InstantiateMsg, QueryMsg, CredListResponse};
use crate::state::{config, config_cred, config_cred_read, config_read, Cred, State};
use crate::state::PREFIX_REVOKED_PERMITS;
/// Initializes the contract with a given count and sets the owner of the contract.
///
/// # Arguments
///
/// * `deps` - A mutable reference to the dependencies required by CosmWasm contracts.
/// * `_env` - The environment object containing information about the current block, transaction, etc.
/// * `info` - Information about the message sender and other metadata.
/// * `msg` - Message containing the initial count value to set for the contract.
///
/// # Returns
///
/// A `StdResult<Response>` indicating the success or failure of the initialization process.
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

/// Handles execute messages to modify the contract's state.
///
/// # Arguments
///
/// * `deps` - A mutable reference to the dependencies required by CosmWasm contracts.
/// * `env` - The environment object containing information about the current block, transaction, etc.
/// * `info` - Information about the message sender and other metadata.
/// * `msg` - Message containing the operation to be executed (increment, reset, add credential).
///
/// # Returns
///
/// A `StdResult<Response>` indicating the success or failure of the execute operation.
#[entry_point]
pub fn execute(deps: DepsMut, env: Env, info: MessageInfo, msg: ExecuteMsg) -> StdResult<Response> {
    match msg {
        ExecuteMsg::Increment {} => try_increment(deps, env),
        ExecuteMsg::Reset { count } => try_reset(deps, info, count),
        ExecuteMsg::Add { credential  } => try_add(deps, info, credential),
    }
}

/// Attempts to increment the counter state of the contract.
///
/// # Arguments
///
/// * `deps` - A mutable reference to the dependencies required by CosmWasm contracts.
/// * `_env` - The environment object containing information about the current block, transaction, etc.
///
/// # Returns
///
/// A `StdResult<Response>` indicating the success or failure of the increment operation.
pub fn try_increment(deps: DepsMut, _env: Env) -> StdResult<Response> {
    config(deps.storage).update(|mut state| -> Result<_, StdError> {
        state.count += 1;
        Ok(state)
    })?;

    deps.api.debug("count incremented successfully");
    Ok(Response::default())
}

/// Attempts to reset the counter state of the contract to a specified value.
///
/// # Arguments
///
/// * `deps` - A mutable reference to the dependencies required by CosmWasm contracts.
/// * `info` - Information about the message sender and other metadata.
/// * `count` - The new count value to set for the counter.
///
/// # Returns
///
/// A `StdResult<Response>` indicating the success or failure of the reset operation.
pub fn try_reset(deps: DepsMut, info: MessageInfo, count: i32) -> StdResult<Response> {
    let sender_address = info.sender.clone();
    config(deps.storage).update(|mut state| {
        if sender_address != state.owner {
            return Err(StdError::generic_err("Only the owner can reset count"));
        }
        state.count = count;
        Ok(state)
    })?;

    deps.api.debug("count reset successfully");
    Ok(Response::default())
}

/// Attempts to add a new credential to the contract's state.
///
/// # Arguments
///
/// * `deps` - A mutable reference to the dependencies required by CosmWasm contracts.
/// * `info` - Information about the message sender and other metadata.
/// * `credential` - The credential to be added to the contract.
///
/// # Returns
///
/// A `StdResult<Response>` indicating the success or failure of the add operation.
pub fn try_add(deps: DepsMut, info: MessageInfo, credential: Cred) -> Result< Response, StdError> {
    let sender_address = info.sender.clone();
    let state = config_read(deps.storage).load()?;
    if sender_address != state.owner {
        return Err(StdError::generic_err("Only the owner add Credential"))?;
    }
    let index = b"0"; // Convert the integer to a byte slice
    config_cred(deps.storage, index).save(&credential)?;
    deps.api.debug("credential added successfully");
    Ok(Response::default())
}

/// Handles query messages to retrieve data from the contract's state.
///
/// # Arguments
///
/// * `deps` - A reference to the dependencies required by CosmWasm contracts.
/// * `env` - The environment object containing information about the current block, transaction, etc.
/// * `msg` - Message containing the query operation to be executed (get count, get all credentials).
///
/// # Returns
///
/// A `StdResult<QueryResponse>` indicating the success or failure of the query operation.
#[entry_point]
pub fn query(deps: Deps, env: Env, msg: QueryMsg) -> StdResult<QueryResponse> {
    match msg {
        QueryMsg::GetCount {} => to_binary(&query_count(deps)?),
        QueryMsg::GetAll {
            wallet,
            permit,
            index,
        } => to_binary(&get_all(deps, env, wallet, permit, index)?),
    }
}

/// Retrieves the current count value from the contract's state.
///
/// # Arguments
///
/// * `deps` - A reference to the dependencies required by CosmWasm contracts.
///
/// # Returns
///
/// A `StdResult<CountResponse>` containing the current count value.
fn query_count(deps: Deps) -> StdResult<CountResponse> {
    let state = config_read(deps.storage).load()?;
    Ok(CountResponse { count: state.count })
}

/// Retrieves all credentials for a given wallet, validated by a permit.
///
/// # Arguments
///
/// * `deps` - A reference to the dependencies required by CosmWasm contracts.
/// * `env` - The environment object containing information about the current block, transaction, etc.
/// * `wallet` - The address of the wallet for which credentials are being retrieved.
/// * `permit` - The permit used to validate access to the credentials.
/// * `index` - The index at which to start retrieving credentials.
///
/// # Returns
///
/// A `StdResult<CredListResponse>` containing the list of credentials.
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

#[cfg(test)]
mod tests {
    use super::*;
    use cosmwasm_std::testing::*;
    use cosmwasm_std::{from_binary, Coin, StdError, Uint128};
    const PATH_PERMIT: &str = "../permit.json";
    use serde::{Deserialize, Serialize};
    use serde_json::from_str;
    use std::fs::read_to_string;

    // Struct to deserialize data from a JSON file
    #[derive(Serialize, Deserialize)]
    struct GetAllData {
        pub wallet: Addr,
        pub index: u8,
        pub permit: Permit,
    }

    // Struct to hold the deserialized JSON data
    #[derive(Serialize, Deserialize)]
    struct JsonData {
        pub get_all: GetAllData,
    }

    /// Test function for retrieving all credentials.
    #[test]
    fn get_cred_all() {
        let mut deps = mock_dependencies();
        // Load data from a permet JSON file on disk (create by Client.query_get_all)
        let json_data_str = read_to_string(PATH_PERMIT).expect("Unable to read file");
        let json_data: JsonData = from_str(&json_data_str).expect("Failed to deserialize JSON data");
        let wallet = &json_data.get_all.wallet;
        let index = json_data.get_all.index;
        let permit = json_data.get_all.permit;
        println!("wallet: {:?}", &wallet);
        println!("index: {:?}", index);
        println!("permit: {:?}", permit);
        // Set up the mock environment and contract address
        let info = mock_info(
            &wallet.clone().into_string(),
            &[Coin {
                denom: "earth".to_string(),
                amount: Uint128::new(1000),
            }],
        );
        let mut env = mock_env();
        let contract_address = permit.clone().params.allowed_tokens[0].clone();
        env.contract.address = Addr::unchecked(contract_address);

        // Instantiate the contract
        let instantiate_msg = InstantiateMsg { count: 0 };
        let _res = instantiate(
            deps.as_mut(), 
            env.clone(), 
            info.clone(), 
            instantiate_msg
        ).unwrap();

        // Define a credential to add
        let credential = Cred {
            name: "example_name".to_string(),
            url: "example_url".to_string(),
            email: "example_email".to_string(),
            login: "example_login".to_string(),
            password: "example_password".to_string(),
            note: "example_note".to_string(),
            share: "example_share".to_string(),
        };

        // Call the try_add function
        let execute_msg = ExecuteMsg::Add { credential: credential.clone() };
        let _res = execute(
            deps.as_mut(), 
            env.clone(), 
            info.clone(), 
            execute_msg
        ).unwrap();

        // Verify that the credential was added successfully
        assert_eq!(_res.messages.len(), 0);

        // Call the get_all function to retrieve all credentials
        let list_cred = get_all(
            deps.as_ref(),
            env.clone(),
            wallet.clone(),
            permit,
            index,
        );

        println!("list_cred: {:?}", list_cred);

        // Verify that the credential was added successfully
        match list_cred {
            Err(StdError::GenericErr { .. }) => panic!("Must return unauthorized error"),
            _ => {}
        }

    }

    /// Test function to ensure proper contract initialization.
    #[test]
    fn proper_initialization() {
        let mut deps = mock_dependencies();

        // Set up the mock environment and instantiate message
        let info = mock_info(
            "creator",
            &[Coin {
                denom: "earth".to_string(),
                amount: Uint128::new(1000),
            }],
        );
        let init_msg = InstantiateMsg { count: 17 };

        // Instantiate the contract
        let res = instantiate(deps.as_mut(), mock_env(), info.clone(), init_msg).unwrap();

        assert_eq!(0, res.messages.len());

        // Query the state to verify initialization
        let res = query(
            deps.as_ref(),
            mock_env(),
            QueryMsg::GetCount {}
        ).unwrap();
        let value: CountResponse = from_binary(&res).unwrap();
        assert_eq!(17, value.count);
    }

    /// Test function for adding a credential.
    #[test]
    fn add_credential() {
        // Initialize mock dependencies
        let mut deps = mock_dependencies_with_balance(&[Coin {
            denom: "token".to_string(),
            amount: Uint128::new(2),
        }]);

        // Set up the mock environment and instantiate message
        let info = mock_info(
            "creator",
            &[Coin {
                denom: "token".to_string(),
                amount: Uint128::new(2),
            }],
        );

        // Instantiate the contract
        let instantiate_msg = InstantiateMsg { count: 0 };
        let _res = instantiate(
            deps.as_mut(), 
            mock_env(), 
            info.clone(), 
            instantiate_msg
        ).unwrap();

    
        // Define a credential to add
        let credential = Cred {
            name: "example_name".to_string(),
            url: "example_url".to_string(),
            email: "example_email".to_string(),
            login: "example_login".to_string(),
            password: "example_password".to_string(),
            note: "example_note".to_string(),
            share: "example_share".to_string(),
        };

        // Call the try_add function
        let execute_msg = ExecuteMsg::Add { credential: credential.clone() };
        let _res = execute(
            deps.as_mut(), 
            mock_env(), 
            info.clone(), 
            execute_msg
        ).unwrap();
    
        // Verify that the credential was added successfully
        assert_eq!(_res.messages.len(), 0);
        
    
        // Retrieve and verify the saved credential
        let index = b"0"; // Convert the integer to a byte slice
        let stored_cred: Cred = config_cred_read(deps.as_mut().storage, index).load().unwrap();

        assert_eq!(stored_cred.name, "example_name");
        assert_eq!(stored_cred.url, "example_url");
        assert_eq!(stored_cred.email, "example_email");
        assert_eq!(stored_cred.login, "example_login");
        assert_eq!(stored_cred.password, "example_password");
        assert_eq!(stored_cred.note, "example_note");
        assert_eq!(stored_cred.share, "example_share");

        // Verfy that only "creator" can add a credential
        let _info_public = mock_info(
            "public",
            &[Coin {
                denom: "token".to_string(),
                amount: Uint128::new(2),
            }],
        );
        let execute_msg = ExecuteMsg::Add { credential: credential.clone()};
        let _res  = execute(
            deps.as_mut(), 
            mock_env(), 
            _info_public.clone(), 
            execute_msg
        );
        
        // Verify that the credential is not added
        match _res {
            Err(StdError::GenericErr { .. }) => {}
            _ => panic!("Must return unauthorized error")
        }

    }

   /// Test function for incrementing a counter.
    #[test]
    fn increment() {
        let mut deps = mock_dependencies_with_balance(&[Coin {
            denom: "token".to_string(),
            amount: Uint128::new(2),
        }]);

        // Set up the mock environment and instantiate message
        let info = mock_info(
            "creator",
            &[Coin {
                denom: "token".to_string(),
                amount: Uint128::new(2),
            }],
        );

        let init_msg = InstantiateMsg { count: 17 };

        // Instantiate the contract
        let _res = instantiate(deps.as_mut(), mock_env(), info, init_msg).unwrap();

        // Anyone can increment the counter
        let info = mock_info(
            "anyone",
            &[Coin {
                denom: "token".to_string(),
                amount: Uint128::new(2),
            }],
        );

        let exec_msg = ExecuteMsg::Increment {};
        let _res = execute(deps.as_mut(), mock_env(), info.clone(), exec_msg).unwrap();

        // Should increase counter by 1
        let res = query(deps.as_ref(), mock_env(), QueryMsg::GetCount {}).unwrap();
        let value: CountResponse = from_binary(&res).unwrap();
        assert_eq!(18, value.count);
    }

    /// Test function to verify that only the contract creator can reset the counter.
    #[test]
    fn reset() {
        let mut deps = mock_dependencies_with_balance(&[Coin {
            denom: "token".to_string(),
            amount: Uint128::new(2),
        }]);
        let info = mock_info(
            "creator",
            &[Coin {
                denom: "token".to_string(),
                amount: Uint128::new(2),
            }],
        );
        let init_msg = InstantiateMsg { count: 17 };

        let _res = instantiate(deps.as_mut(), mock_env(), info, init_msg).unwrap();

        // Verify that only the creator can reset the counter

        let info = mock_info(
            "anyone",
            &[Coin {
                denom: "token".to_string(),
                amount: Uint128::new(2),
            }],
        );
        let exec_msg = ExecuteMsg::Reset { count: 5 };

        let res = execute(deps.as_mut(), mock_env(), info, exec_msg);

        match res {
            Err(StdError::GenericErr { .. }) => {}
            _ => panic!("Must return unauthorized error"),
        }

        // Only the original creator can reset the counter
        let info = mock_info(
            "creator",
            &[Coin {
                denom: "token".to_string(),
                amount: Uint128::new(2),
            }],
        );
        let exec_msg = ExecuteMsg::Reset { count: 5 };

        let _res = execute(deps.as_mut(), mock_env(), info.clone(), exec_msg).unwrap();

        // Verify that the counter has been reset to 5
        let res = query(deps.as_ref(), mock_env(), QueryMsg::GetCount {}).unwrap();
        let value: CountResponse = from_binary(&res).unwrap();
        assert_eq!(5, value.count);
    }

}
