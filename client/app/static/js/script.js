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
    document.getElementById('add_exchange_addr_res').innerHTML = "Creating Exchange...";
    fetch(apiUrl, {
        method: 'POST'
    }).then(response => {
        return response.json();
    }).then(data => {
        if (data["result"] == "fail"){
            if (data["reason"] == "Invalid public key"){
                document.getElementById('add_exchange_addr_res').innerHTML = "Account invalid or doesn't exist";
            } else {
                document.getElementById('add_exchange_addr_res').innerHTML = "Unknown error: " + data["reason"];
            }
        } else {
            document.getElementById('add_exchange_addr_res').innerHTML = 'Created DEX contract: ' + data['dex_contract_address'];
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

function buyToken(){
    var account = document.getElementById("buy_token_addr").value;
    var amount = document.getElementById("buy_token_amount").value;
    var contract_address = document.getElementById("buy_token_dex_addr").value;
    if (amount <= 0){
       document.getElementById('buy_token_res').innerHTML = "Amount must be greater than zero";
      return;
    }
    if (account == "" || contract_address == ""){
      document.getElementById('buy_token_res').innerHTML = "Contract and Account addresses must be not empty";
      return;
    }
    params = {
        account: account,
        amount: amount,
        contract_address: contract_address
    }

    var apiUrl = new URL('/api/exchange/buy_token', document.baseURI);

    apiUrl.search = new URLSearchParams(params).toString();
    document.getElementById('buy_token_res').innerHTML = "Executing Transaction...";
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
                document.getElementById('buy_token_res').innerHTML = "Unknown error: " + data["reason"];
            }
        } else {
            document.getElementById('buy_token_res').innerHTML = 'Buying Token Succeeded: ' + data;
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
                document.getElementById('add_existing_account').innerHTML = "Unknown error: " + data["reason"];
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
                document.getElementById('deleted_account').innerHTML = "Unknown error: " + data["reason"];
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
                document.getElementById('account_balance').innerHTML = "Unknown error: " + data["reason"];
            }
        } else {
            var num = BigInt(data['balance'])
            num = wei2eth(num);
            res = "Account balance is " + data['balance'] + " wei =~\n" + num + " eth"
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
    return Number(num * 100000n / 1000000000000000000n) / 100000
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
                document.getElementById('lock_account').innerHTML = "Unknown error: " + data["reason"];
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
                document.getElementById('unlock_account').innerHTML = "Unknown error: " + data["reason"];
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
                document.getElementById('account_sk').innerHTML = "Unknown error: " + data["reason"];
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
        for (let key of ['Account','State', 'Wei Balance', 'Eth Balance']) {
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
            text = document.createTextNode(element['balance']);
            cell.appendChild(text);

            cell = row.insertCell();
            text = document.createTextNode(wei2eth(BigInt(element['balance'])));
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