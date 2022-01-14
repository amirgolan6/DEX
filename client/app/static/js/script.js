function createAccount() {
    var password = document.getElementById("new_password").value;
    if (password == ""){
      document.getElementById('new_created_account').innerHTML = "Password must be not empty";
      return;
    }
    var apiUrl = new URL('/api/account/create/', document.baseURI),
    params = {
    password: password
    }
    apiUrl.search = new URLSearchParams(params).toString();
    document.getElementById('new_created_account').innerHTML = "Creating account...";
    fetch(apiUrl, {
        method: 'POST'
    }).then(response => {
        return response.json();
    }).then(data => {
        document.getElementById('create_account_btn').remove()
        document.getElementById('new_created_account').innerHTML = "New account created and saved: " + data["public_key"];
        console.log(data);
    }).catch(err => {
        console.log("err");
        console.log(err);
    });
}

function initializeLP(){

    var account = document.getElementById("iniitialize_lp_addr").value;
    var eth_amount = document.getElementById("iniitialize_lp_eth_amnt").value;
    var token_amount = document.getElementById("iniitialize_lp_token_amnt").value;
    if (eth_amount <= 0 || token_amount <=0){
       document.getElementById('initialize_lp_res').innerHTML = "Both amounts must be greater than zero";
      return;
    }
    if (account == ""){
      document.getElementById('initialize_lp_res').innerHTML = "Contract and Account addresses must be not empty";
      return;
    }
    params = {
        account: account,
        eth_amount: eth_amount,
        token_amount: token_amount
    }

    var apiUrl = new URL('/api/exchange/initialize_lp', document.baseURI);

    apiUrl.search = new URLSearchParams(params).toString();
    document.getElementById('initialize_lp_res').innerHTML = "Executing Transaction (might take a minute)...";
    fetch(apiUrl, {
        method: 'POST'
    }).then(response => {
        return response.json();
    }).then(data => {
        if (data["result"] == "fail"){
            if (data["reason"] == "Invalid public key"){
                document.getElementById('initialize_lp_res').innerHTML = "Account invalid or doesn't exist";
            } else {
                console.log(data);
                document.getElementById('initialize_lp_res').innerHTML = "Error: " + data["reason"];
            }
        } else {
            document.getElementById('initialize_lp_btn').remove()
            document.getElementById('initialize_lp_res').innerHTML = "<strong>Initlized Liquidity Pool Successfully</strong>";
            console.log(data);
        }
    }).catch(err => {
        console.log("err");
        console.log(err);
        if (err["reason"] == "Invalid public key"){
            document.getElementById('initialize_lp_res').innerHTML = "Account invalid or doesn't exist";
        }
    });
}


function burnLiquidity(){
    var account = document.getElementById("burn_liquidity_addr").value;
    var lqt_amount = document.getElementById("burn_liquidity_lqt_amount").value;
    var apiUrl = new URL('/api/exchange/burn_liquidity', document.baseURI);
    params = {
        account: account,
        lqt_amount: lqt_amount
    }
    if (account == "" || lqt_amount <= 0){
      document.getElementById('burn_liquidity_res').innerHTML = "Account and LQT amount must be not empty";
      return;
    }
    apiUrl.search = new URLSearchParams(params).toString();
    document.getElementById('burn_liquidity_res').innerHTML = "Burning LQT...";
    fetch(apiUrl, {
        method: 'POST'
    }).then(response => {
        return response.json();
    }).then(data => {
        if (data["result"] == "fail"){
            console.log(data);
            document.getElementById('burn_liquidity_res').innerHTML = "Error: " + data["reason"];
        }
        else {
            document.getElementById('burn_liquidity_btn').remove();
            document.getElementById('burn_liquidity_res').innerHTML = data["reason"];
            console.log(data);
        }
    }).catch(err => {
        console.log(err);
    
    });
}

function getUserLQTBalance(){
    var account = document.getElementById("burn_liquidity_addr").value;
    var apiUrl = new URL('/api/exchange/lqt_balances', document.baseURI);
    params = {
        account: account
    }
    if (account == ""){
      document.getElementById('burn_liquidity_lqt_balance_res').innerHTML = "Account must be not empty";
      return;
    }
    apiUrl.search = new URLSearchParams(params).toString();
    document.getElementById('burn_liquidity_lqt_balance_res').innerHTML = "Getting LQT balance...";
    fetch(apiUrl, {
        method: 'GET'
    }).then(response => {
        return response.json();
    }).then(data => {
        if (data["result"] == "fail"){
            console.log(data);
            document.getElementById('burn_liquidity_lqt_balance_res').innerHTML = "Error: " + data["reason"];
        }
        else {
            //document.getElementById('add_liquidity_ratio_btn').remove();
            user_lqt = '<b>User LQT Balance: ' + data['user_lqt_balance'] + '</b><br><br>';
            total_lqt = '<b>Total LQT Balance: ' + data['total_lqt'] + '</b><br><br>';
            document.getElementById('burn_liquidity_lqt_balance_res').innerHTML = user_lqt + total_lqt;
            console.log(data);
        }
    }).catch(err => {
        console.log(err);
    
    });
}



function getLiquidityRatio(){
    var account = document.getElementById("add_liquidity_addr").value;
    var apiUrl = new URL('/api/exchange/lp_balance', document.baseURI);
    params = {
        account: account
    }
    if (account == ""){
      document.getElementById('add_liquidity_ratio_res').innerHTML = "Account must be not empty";
      return;
    }
    apiUrl.search = new URLSearchParams(params).toString();
    document.getElementById('add_liquidity_ratio_res').innerHTML = "Getting balances...";
    fetch(apiUrl, {
        method: 'GET'
    }).then(response => {
        return response.json();
    }).then(data => {
        if (data["result"] == "fail"){
            console.log(data);
            document.getElementById('add_liquidity_ratio_res').innerHTML = "Error: " + data["reason"];
        }
        else {
            //document.getElementById('add_liquidity_ratio_btn').remove();
            str = '<b>EtH Balance: ' + data['eth_balance'] + '</b><br>' + '<b>\n Token Balance: ' + data['token_balance'] + 
            '</b><br>' + '<b>\n Liquidity Pool Tokens Balance: ' + data['lp_balance'] + '</b><br>';
            ratio_str = '<b>\n Tokens/ETH Ratio: ' + (data['token_balance']/data['eth_balance']) + ':1</b><br>';
            
            document.getElementById('add_liquidity_ratio_res').innerHTML = str + ratio_str;
            console.log(data);
        }
    }).catch(err => {
        console.log(err);
    
    });
}

function addLiquidity(){
    var account = document.getElementById("add_liquidity_addr").value;
    var eth_amount = document.getElementById("add_liquidity_eth_amount").value;
    var token_amount = document.getElementById("add_liquidity_token_amount").value;
    if (eth_amount <= 0 || token_amount <=0){
       document.getElementById('add_liquidity_add_res').innerHTML = "Both amounts must be greater than zero";
      return;
    }
    if (account == ""){
      document.getElementById('add_liquidity_add_res').innerHTML = "Contract and Account addresses must be not empty";
      return;
    }
    params = {
        account: account,
        eth_amount: eth_amount,
        token_amount: token_amount
    }

    var apiUrl = new URL('/api/exchange/add_liquidity', document.baseURI);

    apiUrl.search = new URLSearchParams(params).toString();
    document.getElementById('add_liquidity_add_res').innerHTML = "<br><br>Executing Transaction (might take a minute)...<br><br>";
    fetch(apiUrl, {
        method: 'POST'
    }).then(response => {
        return response.json();
    }).then(data => {
        if (data["result"] == "fail"){
            if (data["reason"] == "Invalid public key"){
                document.getElementById('add_liquidity_add_res').innerHTML = "Account invalid or doesn't exist";
            } else {
                console.log(data);
                document.getElementById('add_liquidity_add_res').innerHTML = "Error: " + data["reason"];
            }
        } else {
            document.getElementById('add_liquidity_add_btn').remove()
            document.getElementById('add_liquidity_add_res').innerHTML = "<br><br><strong>Added Liquidity to Pool Successfully</strong><br><br>";
            console.log(data);
        }
    }).catch(err => {
        console.log("err");
        console.log(err);
        if (err["reason"] == "Invalid public key"){
            document.getElementById('add_liquidity_add_res').innerHTML = "Account invalid or doesn't exist";
        }
    });

}



function getLPbalance(){
    var account = document.getElementById("lp_balance_addr").value;
    var apiUrl = new URL('/api/exchange/lp_balance', document.baseURI);
    params = {
        account: account
    }
    if (account == ""){
      document.getElementById('lp_balance_res').innerHTML = "Account must be not empty";
      return;
    }
    apiUrl.search = new URLSearchParams(params).toString();
    document.getElementById('lp_balance_res').innerHTML = "Getting balances...";
    fetch(apiUrl, {
        method: 'GET'
    }).then(response => {
        return response.json();
    }).then(data => {
        if (data["result"] == "fail"){
            console.log(data);
            document.getElementById('lp_balance_res').innerHTML = "Error: " + data["reason"];
        }
        else {
            document.getElementById('lp_balance_btn').remove();
            str = '<br><br><br><b>EtH Balance: ' + data['eth_balance'] + '</b><br>' + '<b>\n Token Balance: ' + data['token_balance'] + 
            '</b><br>' + '<b>\n Liquidity Pool Tokens Balance: ' + data['lp_balance'] + '</b><br>';
            document.getElementById('lp_balance_res').innerHTML = str;
            console.log(data);
        }
    }).catch(err => {
        console.log(err);
    
    });

}


function tokenToEther(){
    var account = document.getElementById("token_to_ether_addr").value;
    var token_amount = document.getElementById("token_to_ether_amount").value;
    if (token_amount <= 0){
       document.getElementById('token_to_ether_res').innerHTML = "Amount must be greater than zero";
      return;
    }
    if (account == "" ){
      document.getElementById('token_to_ether_res').innerHTML = "Contract and Account addresses must be not empty";
      return;
    }
    params = {
        account: account,
        token_amount: token_amount,
    }

    var apiUrl = new URL('/api/exchange/token_to_ether', document.baseURI);

    apiUrl.search = new URLSearchParams(params).toString();
    document.getElementById('token_to_ether_res').innerHTML = "Executing Transaction (might take a minute)...";
    fetch(apiUrl, {
        method: 'POST'
    }).then(response => {
        return response.json();
    }).then(data => {
        if (data["result"] == "fail"){
            if (data["reason"] == "Invalid public key"){
                document.getElementById('token_to_ether_res').innerHTML = "Account invalid or doesn't exist";
            } else {
                console.log(data);
                document.getElementById('token_to_ether_res').innerHTML = "Error: " + data["reason"];
            }
        } else {
            document.getElementById('token_to_ether_btn').remove()
            document.getElementById('token_to_ether_res').innerHTML = data["reason"];
            console.log(data);
        }
    }).catch(err => {
        console.log("err");
        console.log(err);
        if (err["reason"] == "Invalid public key"){
            document.getElementById('account_balance').innerHTML = "Account invalid or doesn't exist";
        }
    });

}



function etherToToken(){
    var account = document.getElementById("ether_to_token_addr").value;
    var eth_amount = document.getElementById("ether_to_token_amount").value;
    if (eth_amount <= 0){
       document.getElementById('ether_to_token_res').innerHTML = "Amount must be greater than zero";
      return;
    }
    if (account == "" ){
      document.getElementById('ether_to_token_res').innerHTML = "Contract and Account addresses must be not empty";
      return;
    }
    params = {
        account: account,
        eth_amount: eth_amount,
    }

    var apiUrl = new URL('/api/exchange/ether_to_token', document.baseURI);

    apiUrl.search = new URLSearchParams(params).toString();
    document.getElementById('ether_to_token_res').innerHTML = "Executing Transaction (might take a minute)...";
    fetch(apiUrl, {
        method: 'POST'
    }).then(response => {
        return response.json();
    }).then(data => {
        if (data["result"] == "fail"){
            if (data["reason"] == "Invalid public key"){
                document.getElementById('ether_to_token_res').innerHTML = "Account invalid or doesn't exist";
            } else {
                console.log(data);
                document.getElementById('ether_to_token_res').innerHTML = "Error: " + data["reason"];
            }
        } else {
            document.getElementById('ether_to_token_btn').remove()
            document.getElementById('ether_to_token_res').innerHTML = data["reason"];
            console.log(data);
        }
    }).catch(err => {
        console.log("err");
        console.log(err);
        if (err["reason"] == "Invalid public key"){
            document.getElementById('ether_to_token_res').innerHTML = "Account invalid or doesn't exist";
        }
    });

}




function createExchange() {
    var account = document.getElementById("add_exchange_addr").value;
    var apiUrl = new URL('/api/exchange/create', document.baseURI),
    params = {
        account: account
    }
    if (account == ""){
      document.getElementById('add_exchange_addr_res').innerHTML = "Account must be not empty";
      return;
    }
    apiUrl.search = new URLSearchParams(params).toString();
    document.getElementById('add_exchange_addr_res').innerHTML = "Creating Exchange (this might take a minute)...";
    fetch(apiUrl, {
        method: 'POST'
    }).then(response => {
        return response.json();
    }).then(data => {
        if (data["result"] == "fail"){
            if (data["reason"] == "Invalid public key"){
                document.getElementById('add_exchange_addr_res').innerHTML = "Account invalid or doesn't exist";
            } else {
                document.getElementById('add_exchange_addr_res').innerHTML = "Error: " + data["reason"];
            }
        } else {
            document.getElementById('add_exchange_btn').remove();
            document.getElementById('add_exchange_addr_res').innerHTML = 'Created DEX with contract address: ' + data['dex_contract_address'] + 
            ', token contract address: ' + data['token_contract_address'];
            console.log(data);
        }
    }).catch(err => {
        console.log("err");
        console.log(err);
        if (err["reason"] == "Invalid public key"){
            document.getElementById('account_balance').innerHTML = "Account invalid or doesn't exist";
        }
    });
}


function getContractDetails(){
    var account = document.getElementById("contract_details_account_addr").value;
    var apiUrl = new URL('/api/exchange/details', document.baseURI);
    params = {
        account: account
    }
    if (account == ""){
      document.getElementById('add_exchange_addr_res').innerHTML = "Account must be not empty";
      return;
    }
    apiUrl.search = new URLSearchParams(params).toString();
    //apiUrl.search = new URLSearchParams(params).toString();
    document.getElementById('get_contract_details_res').innerHTML = "Getting details...";
    fetch(apiUrl, {
        method: 'GET'
    }).then(response => {
        return response.json();
    }).then(data => {
        if (data["result"] == "fail"){
            console.log(data);
            document.getElementById('get_contract_details_res').innerHTML = "Error: " + data["reason"];
        }
        else {
            document.getElementById('get_contract_details_btn').remove()
            str = '<b>DEX Address: ' + data['dex_contract_address'] + '</b><br>' + '<b>\n Token Address: ' + data['token_contract_address'] + 
            '</b><br>' + '<b>\n ETH Balance: ' + data['eth_balance'] + '</b><br>' + '<b>\n Tokens Quantity in Ether: ' + data['tok_balance'] + '</b><br>' 
            + '<b>\n Tokens Quantity: ' + data['tok_quantity'] + '</b><br>';
            document.getElementById('get_contract_details_res').innerHTML = str;
            console.log(data);
        }
    }).catch(err => {
        console.log(err);
    
    });
}


function buyToken(){
    var account = document.getElementById("buy_token_addr").value;
    var amount = document.getElementById("buy_token_amount").value;
    if (amount <= 0){
       document.getElementById('buy_token_res').innerHTML = "Amount must be greater than zero";
      return;
    }
    if (account == "" ){
      document.getElementById('buy_token_res').innerHTML = "Contract and Account addresses must be not empty";
      return;
    }
    params = {
        account: account,
        amount: amount,
    }

    var apiUrl = new URL('/api/exchange/buy_token', document.baseURI);

    apiUrl.search = new URLSearchParams(params).toString();
    document.getElementById('buy_token_res').innerHTML = "Executing Transaction (might take a minute)...";
    fetch(apiUrl, {
        method: 'POST'
    }).then(response => {
        return response.json();
    }).then(data => {
        if (data["result"] == "fail"){
            if (data["reason"] == "Invalid public key"){
                document.getElementById('buy_token_res').innerHTML = "Account invalid or doesn't exist";
            } else {
                console.log(data);
                document.getElementById('buy_token_res').innerHTML = "Error: " + data["reason"];
            }
        } else {
            document.getElementById('buy_token_btn').remove()
            document.getElementById('buy_token_res').innerHTML = data["reason"];
            console.log(data);
        }
    }).catch(err => {
        console.log("err");
        console.log(err);
        if (err["reason"] == "Invalid public key"){
            document.getElementById('account_balance').innerHTML = "Account invalid or doesn't exist";
        }
    });
}




function sellToken(){
    var account = document.getElementById("sell_token_addr").value;
    var amount = document.getElementById("sell_token_amount").value;
    if (amount <= 0){
       document.getElementById('sell_token_res').innerHTML = "Amount must be greater than zero";
      return;
    }
    if (account == "" ){
      document.getElementById('sell_token_res').innerHTML = "Contract and Account addresses must be not empty";
      return;
    }
    params = {
        account: account,
        amount: amount,
    }

    var apiUrl = new URL('/api/exchange/sell_token', document.baseURI);

    apiUrl.search = new URLSearchParams(params).toString();
    document.getElementById('sell_token_res').innerHTML = "Executing Transaction (might take a minute)...";
    fetch(apiUrl, {
        method: 'POST'
    }).then(response => {
        return response.json();
    }).then(data => {
        if (data["result"] == "fail"){
            if (data["reason"] == "Invalid public key"){
                document.getElementById('sell_token_res').innerHTML = "Account invalid or doesn't exist";
            } else {
                console.log(data);
                document.getElementById('sell_token_res').innerHTML = "Error: " + data["reason"];
            }
        } else {
            document.getElementById('sell_token_btn').remove()
            document.getElementById('sell_token_res').innerHTML = data["reason"];
            console.log(data);
        }
    }).catch(err => {
        console.log("err");
        console.log(err);
        if (err["reason"] == "Invalid public key"){
            document.getElementById('account_balance').innerHTML = "Account invalid or doesn't exist";
        }
    });
}




function addExistingAccount() {
    var password = document.getElementById("add_account_password").value;
    var private_key = document.getElementById("add_account_private_key").value;
    if (password == "" || private_key == ""){
      document.getElementById('add_existing_account').innerHTML = "Private Key and Password must be not empty";
      return;
    }
    var apiUrl = new URL('/api/account/add', document.baseURI),
    params = {
        password: password,
        private_key: private_key
    }
    apiUrl.search = new URLSearchParams(params).toString();
    document.getElementById('add_existing_account').innerHTML = "Adding account...";
    fetch(apiUrl, {
        method: 'POST'
    }).then(response => {
        return response.json();
    }).then(data => {
        if (data["result"] == "fail"){
            if (data["reason"] == "Invalid private key"){
                document.getElementById('add_existing_account').innerHTML = "Invalid private key";
            } else {
                document.getElementById('add_existing_account').innerHTML = "Error: " + data["reason"];
            }
        } else {
            console.log(data);
            document.getElementById('add_existing_acnt_btn').remove();
            document.getElementById('add_existing_account').innerHTML = "Account added and saved";
        }
        
    }).catch(err => {
        console.log("err");
        console.log(err);
    });
}

function deleteAccount() {
    var account = document.getElementById("delete_acoount").value;
    var apiUrl = new URL('/api/account/delete', document.baseURI),
    params = {
        public_key: account
    }
    if (account == ""){
      document.getElementById('deleted_account').innerHTML = "Account must be not empty";
      return;
    }
    apiUrl.search = new URLSearchParams(params).toString();
    document.getElementById('deleted_account').innerHTML = "Deleting account...";
    fetch(apiUrl, {
        method: 'DELETE'
    }).then(response => {
        return response.json();
    }).then(data => {
        if (data["result"] == "fail"){
            if (data["reason"] == "Invalid public key"){
                document.getElementById('deleted_account').innerHTML = "Account invalid or doesn't exist";
            } else {
                document.getElementById('deleted_account').innerHTML = "Error: " + data["reason"];
            }
        } else {
            document.getElementById('delete_acnt_btn').remove();
            document.getElementById('deleted_account').innerHTML = "Account deleted";
        }
    }).catch(err => {
        console.log("err");
        console.log(err);
        if (err["reason"] == "Invalid public key"){
            document.getElementById('deleted_account').innerHTML = "Account invalid or doesn't exist";
        }
    });
}

function accountTokBalance(){
    var account = document.getElementById("account_tok_public_key").value;
    var apiUrl = new URL('/api/account/get_tok_balance', document.baseURI),
    params = {
        account: account
    }
    if (account == ""){
      document.getElementById('account_tok_balance').innerHTML = "Account must be not empty";
      return;
    }
    apiUrl.search = new URLSearchParams(params).toString();
    document.getElementById('account_tok_balance').innerHTML = "Getting account balance...";
    fetch(apiUrl, {
        method: 'GET'
    }).then(response => {
        return response.json();
    }).then(data => {
        if (data["result"] == "fail"){
            if (data["reason"] == "Invalid public key"){
                document.getElementById('account_tok_balance').innerHTML = "Account invalid or doesn't exist";
            } else {
                document.getElementById('account_tok_balance').innerHTML = "Error: " + data["reason"];
            }
        } else { 
            document.getElementById('tok_balance_btn').remove();
            tok_balance = data['tok_balance'] > 0 ? data['tok_balance'] : 0;
            res = "Account balance is " + tok_balance + " Tok.";
            document.getElementById('account_tok_balance').innerHTML = res;
        }
    }).catch(err => {
        console.log("err");
        console.log(err);
        if (err["reason"] == "Invalid public key"){
            document.getElementById('account_tok_balance').innerHTML = "Account invalid or doesn't exist";
        }
    });


}

function accountBalance() {
    var account = document.getElementById("account_public_key").value;
    var apiUrl = new URL('/api/account/get_balance', document.baseURI),
    params = {
        account: account
    }
    if (account == ""){
      document.getElementById('account_balance').innerHTML = "Account must be not empty";
      return;
    }
    apiUrl.search = new URLSearchParams(params).toString();
    document.getElementById('account_balance').innerHTML = "Getting account balance...";
    fetch(apiUrl, {
        method: 'GET'
    }).then(response => {
        return response.json();
    }).then(data => {
        if (data["result"] == "fail"){
            if (data["reason"] == "Invalid public key"){
                document.getElementById('account_balance').innerHTML = "Account invalid or doesn't exist";
            } else {
                document.getElementById('account_balance').innerHTML = "Error: " + data["reason"];
            }
        } else { 
            document.getElementById('account_balance_btn').remove()
            res = "Account balance is " + data['balance'] + " eth."
            document.getElementById('account_balance').innerHTML = res;
        }
    }).catch(err => {
        console.log("err");
        console.log(err);
        if (err["reason"] == "Invalid public key"){
            document.getElementById('account_balance').innerHTML = "Account invalid or doesn't exist";
        }
    });
}

function wei2eth(num) {
    return Number(num  / (10**18))
}

function lockAccount() {
    var account = document.getElementById("lock_account_pk").value;
    var apiUrl = new URL('/api/account/lock', document.baseURI),
    params = {
        public_key: account
    }
    if (account == ""){
      document.getElementById('lock_account').innerHTML = "Account must be not empty";
      return;
    }
    apiUrl.search = new URLSearchParams(params).toString();
    document.getElementById('lock_account').innerHTML = "Locking account...";
    fetch(apiUrl, {
        method: 'POST'
    }).then(response => {
        return response.json();
    }).then(data => {
        if (data["result"] == "fail"){
            if (data["reason"] == "Invalid public key"){
                document.getElementById('lock_account').innerHTML = "Account invalid or doesn't exist";
            } else {
                document.getElementById('lock_account').innerHTML = "Error: " + data["reason"];
            }
        } else {
            document.getElementById('lock_account').innerHTML = "Account locked";
        }
    }).catch(err => {
        console.log("err");
        console.log(err);
        if (err["reason"] == "Invalid public key"){
            document.getElementById('lock_account').innerHTML = "Account invalid or doesn't exist";
        }
    });
}

function unlockAccount() {
    var account = document.getElementById("unlock_account_pk").value;
    var password = document.getElementById("unlock_account_password").value;
    var apiUrl = new URL('/api/account/unlock', document.baseURI),
    params = {
        account: account,
        password: password
    }
    if (password == "" || account == ""){
      document.getElementById('unlock_account').innerHTML = "Public Key and Password must be not empty";
      return;
    }
    apiUrl.search = new URLSearchParams(params).toString();
    document.getElementById('unlock_account').innerHTML = "Unlocking account...";
    fetch(apiUrl, {
        method: 'POST'
    }).then(response => {
        return response.json();
    }).then(data => {
        if (data["result"] == "fail"){
            if (data["reason"] == "Invalid public key"){
                document.getElementById('unlock_account').innerHTML = "Account invalid or doesn't exist";
            } else if (data["reason"] == "Wrong password") {
                document.getElementById('unlock_account').innerHTML = "Password is wrong";
            } else {
                document.getElementById('unlock_account').innerHTML = "Error: " + data["reason"];
            }
        } else {
            document.getElementById('unlock_account').innerHTML = "Account unlocked";
        }
    }).catch(err => {
        console.log("err");
        console.log(err);
        if (err["reason"] == "Invalid public key"){
            document.getElementById('unlock_account').innerHTML = "Account invalid or doesn't exist";
        }
    });
}

function getPrivateKey() {
    var account = document.getElementById("get_account_sk").value;
    var apiUrl = new URL('/api/account/private-key', document.baseURI),
    params = {
        account: account
    }
    if (account == ""){
      document.getElementById('account_sk').innerHTML = "Account must be not empty";
      return;
    }
    apiUrl.search = new URLSearchParams(params).toString();
    document.getElementById('account_sk').innerHTML = "Locking account...";
    fetch(apiUrl, {
        method: 'GET'
    }).then(response => {
        return response.json();
    }).then(data => {
        if (data["result"] == "fail"){
            if (data["reason"] == "Invalid public key"){
                document.getElementById('account_sk').innerHTML = "Account invalid or doesn't exist";
            } else {
                document.getElementById('account_sk').innerHTML = "Error: " + data["reason"];
            }
        } else {
            document.getElementById('account_sk').innerHTML = "Private Key: " + data['result'];
        }
    }).catch(err => {
        console.log("err");
        console.log(err);
        if (err["reason"] == "Invalid account_sk key"){
            document.getElementById('account_sk').innerHTML = "Account invalid or doesn't exist";
        }
    });
}



function listAccounts(){
    document.getElementById('list_accounts').innerHTML = 'Getting Accounts...';
    var apiUrl = '/api/account/list';
    fetch(apiUrl).then(response => {
        return response.json();
    }).then(data => {
        var table = document.createElement('table');
        let thead = table.createTHead();
        let row = thead.insertRow();
        for (let key of ['Account','State', 'Eth Balance', 'Tok Balance']) {
            let th = document.createElement("th");
            let text = document.createTextNode(key);
            th.appendChild(text);
            row.appendChild(th);
        }
        for(let key of Object.keys(data)) {
            let row = table.insertRow();
            element = data[key];
            
            let cell = row.insertCell();
            let text = document.createTextNode(key);
            cell.appendChild(text);

            cell = row.insertCell();
            text = document.createTextNode(element['state']);
            cell.appendChild(text);

            cell = row.insertCell();
            text = document.createTextNode(element['eth_balance']);
            cell.appendChild(text);

            cell = row.insertCell();
            text = document.createTextNode(element['tok_balance'] > 0 ? element['tok_balance'] : 0);
            cell.appendChild(text);

        }
        document.getElementById('get_list_btn').remove();
        document.getElementById('list_accounts').innerHTML = '';
        document.getElementById('list_accounts').appendChild(table);
    }).catch(err => {
        console.log("err");
        console.log(err);
    });
  }




  function is_address(s) {
      if (s.length == 40) return true;
      if (s.length == 42 && s[0] == '0' && (s[1] == 'x' || s[1] == 'X')) return true;
      return false;
  }

  function is_signature(s) {
      if (s.length == 130) return true;
      if (s.length == 132 && s[0] == '0' && (s[1] == 'x' || s[1] == 'X')) return true;
      return false;
  }


function produceSignature() {
    document.getElementById('produce_sig_res').innerHTML = "Attempting signing...";
    withdrawal_account = document.getElementById("produce_sig_dest_address").value.trim();
    authorizing_account = document.getElementById("produce_sig_author_address").value.trim();
    contract_address = document.getElementById("produce_sig_campaign_address").value.trim();
    if (!is_address(withdrawal_account)) {
        document.getElementById('produce_sig_res').innerHTML = "Invalid Account";
        return;
    }
    if (!is_address(authorizing_account)) {
        document.getElementById('produce_sig_res').innerHTML = "Invalid Account for Authorizer";
        return;
    }

    var apiUrl = new URL('/api/campaign/signwithdrawal', document.baseURI),
    params = {
        dest_account: withdrawal_account,
        fund_address: contract_address,
        account: authorizing_account
    }
    apiUrl.search = new URLSearchParams(params).toString();
    fetch(apiUrl, {
        method: 'POST'
    }).then(response => {
        return response.json();
    }).then(data => {
        if (data["result"] == "fail"){
            if (data["reason"] == "Invalid public key"){
                document.getElementById('produce_sig_res').innerHTML = "Account invalid or doesn't exist";
            } else {
                document.getElementById('produce_sig_res').innerHTML = "Error: " + data["reason"];
            }
        } else if (data["result"] == "success") {
            document.getElementById('produce_sig_btn').remove();
            document.getElementById('produce_sig_res').innerHTML = data["signed_message"];
        }
    }).catch(err => {
        console.log("err");
        console.log(err);
        if (err["reason"] == "Invalid public key"){
            document.getElementById('produce_sig_res').innerHTML = "Account invalid or doesn't exist";
        }
    });
}