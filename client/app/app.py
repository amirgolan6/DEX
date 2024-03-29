import os

from client_contract_manager import ClientContractManager
from wallet.wallet import EthWallet

from flask import Flask, request, json, jsonify, make_response, render_template, url_for
from flask_swagger_ui import get_swaggerui_blueprint
from datetime import datetime


wallet = EthWallet(os.environ['WALLET_DB'])

contract_manager = ClientContractManager()
app = Flask(__name__)
import logging
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

### swagger specific ###
SWAGGER_URL = '/api'
API_URL = '/static/swagger.yml'
SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Etherium Crowdfunding - Amir Golan"
    }
)
app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)
### end swagger specific ###


def verify_public_key_syntax(public_key):
    if public_key is None:
        return None
    if public_key.startswith('0x') and len(public_key) == 42:
        int(public_key[2:], 16) # check valid byte string
        return public_key
    elif public_key.startswith('0X') and len(public_key) == 42:
        int(public_key[2:], 16) # check valid byte string
        return public_key.replace("0X", '0x')
    elif len(public_key) == 40:
        int(public_key, 16) # check valid byte string
        return '0x' + public_key
    else:
        return None

def verify_private_key_syntax(key):
    if key is None:
        return None
    if key.startswith('0x') and len(key) == 66:
        int(key[2:], 16) # check valid byte string
        return key
    elif key.startswith('0X') and len(key) == 66:
        int(key[2:], 16) # check valid byte string
        return key.replace("0X", '0x')
    elif len(key) == 64:
        int(key, 16) # check valid byte string
        return '0x' + key
    else:
        return None

@app.route("/", methods=['GET'])
def hello():
    with open("/app/static/index2.html", "r") as f:
        return f.read()
    #return render_template('index.html')


################################################################################
################################################################################
######               Account related routes:                       #############
################################################################################
################################################################################

@app.route("/api/account/create/", methods=['POST'])
def create_account():
    try:
        password = request.args.get('password').strip()
        print("Creating account with password {}".format(password), flush=True)
        public_key, private_key = wallet.create_new_account(password)

        return jsonify({
            "result": "success",
            "public_key": public_key
        })
    except Exception as e:
        print(str(e), flush=True)
        return jsonify({
            "result": "fail",
            "reason": str(e)
        })

@app.route("/api/account/list", methods=['GET'])
def get_accounts():
    try:
        print("Getting all accounts", flush=True)
        accounts = wallet.get_accounts()
        print(accounts, flush=True)
        for account in list(accounts.keys()):
            tok_balance = contract_manager.getTokBalance(account, wallet)
            accounts[account]['tok_balance'] = tok_balance
            lqt_res = contract_manager.getLQTBalances(account, wallet)
            accounts[account]['account_lqt_balance'] = lqt_res["account_lqt_balance"] if lqt_res["result"] == "success" else 0
        return jsonify(accounts)
    except Exception as e:
        print(str(e), flush=True)
        return jsonify({
            "result": "fail",
            "reason": str(e)
        })


@app.route("/api/account/unlock", methods=['POST'])
def unlock_account():
    try:
        password = request.args.get('password').strip()
        public_key = request.args.get('account').strip()
        public_key = verify_public_key_syntax(public_key)
        if public_key is None:
            print("Invalid public key", flush=True)
            return make_response(jsonify({
                "result": "fail",
                "reason": "Invalid public key"
            }), 404)
        print("Unlocking public key", flush=True)
        res = wallet.get_account_by_password(public_key, password)
        if res == "Wrong password":
            return make_response(jsonify({
                "result": "fail",
                "reason": "Wrong password"
            }), 404)
        elif res == "Unlocked":
            return jsonify({
                "result": res
            })
        else:
            return make_response(jsonify({
                "result": "fail",
                "reason": "unknown"
            }),
            500)
        
    except Exception as e:
        print(str(e), flush=True)
        return make_response(jsonify({
            "result": "fail",
            "reason": str(e)
        }),
        500)

@app.route("/api/account/add", methods=['POST'])
def add_account():
    try:
        password = request.args.get('password').strip()
        private_key = request.args.get('private_key').strip()
        private_key = verify_private_key_syntax(private_key)
        if private_key is None:
            print("Invalid private key", flush=True)
            return make_response(jsonify({
                "result": "fail",
                "reason": "Invalid private key"
            }), 404)
        print("Adding private key", flush=True)
        res = wallet.upload_account(private_key, password)
        return make_response(jsonify({
            "result": "success"
        }),
        500)
        
    except Exception as e:
        print(str(e), flush=True)
        return make_response(jsonify({
            "result": "fail",
            "reason": str(e)
        }),
        500)

@app.route("/api/account/lock", methods=['POST'])
def lock_account():
    try:
        public_key = request.args.get('public_key').strip()
        public_key = verify_public_key_syntax(public_key)
        if public_key is None:
            print("Invalid public key", flush=True)
            return make_response(jsonify({
                "result": "fail",
                "reason": "Invalid public key"
            }), 404)
        print("Locking public key (Only owner of password will be able to use it)", flush=True)
        res = wallet.lock_account(public_key)
        return jsonify({
            "result": res
        })
        
    except Exception as e:
        print(str(e), flush=True)
        return make_response(jsonify({
            "result": "fail",
            "reason": str(e)
        }),
        500)

@app.route("/api/account/private-key", methods = ['GET'])
def get_private_key():
    try:
        public_key = request.args.get('account').strip()
        public_key = verify_public_key_syntax(public_key)
        if public_key is None:
            print("Invalid public key", flush=True)
            return make_response(jsonify({
                "result": "fail",
                "reason": "Invalid public key"
            }), 404)
        print("Getting private key for public key {}".format(public_key), flush=True)
        res = wallet.get_private_key(public_key)
        return jsonify({
            "result": res
        })
        
    except Exception as e:
        print(str(e), flush=True)
        return make_response(jsonify({
            "result": "fail",
            "reason": str(e)
        }),
        500)

@app.route("/api/account/delete", methods=['DELETE'])
def delete_account():
    try:
        public_key = request.args.get('public_key').strip()
        public_key = verify_public_key_syntax(public_key)
        if public_key is None:
            print("Invalid public key", flush=True)
            return make_response(jsonify({
                "result": "fail",
                "reason": "Invalid public key"
            }), 404)
        print("Deleting key", flush=True)
        res = wallet.delete_account(public_key)
        return jsonify({
            "result": res
        })
        
    except Exception as e:
        print(str(e), flush=True)
        return make_response(jsonify({
            "result": "fail",
            "reason": str(e)
        }),
        500)


@app.route("/api/account/get_balance", methods=['GET'])
def get_account_balance():
    try:
        account = verify_public_key_syntax(request.args.get('account').strip())
    except (ValueError, TypeError):
        return jsonify({
            "result": "fail",
            "reson": "Params account not included or invalid"
        })
    try:
        eth_balance = wallet.get_balance(account)
        tok_res = contract_manager.getTokBalance(account, wallet)
        tok_balance = tok_res if isinstance(tok_res, int) else 0
        lqt_res = contract_manager.getLQTBalances(account, wallet)
        lqt_balance= lqt_res["account_lqt_balance"] if lqt_res["result"] == "success" else 0
        return jsonify({
            "result": "success",
            "eth_balance": eth_balance,
            "lqt_balance": lqt_balance,
            "tok_balance": tok_balance
            })
    except Exception as e:
        print(str(e), flush=True)
        return jsonify({
            "result": "fail",
            "reason": str(e)
        })


################################################################################
################################################################################
######               DEX related routes:                            ############
################################################################################
################################################################################


@app.route("/api/exchange/create", methods=['POST'])
def create_new_exchange():
    try:
        account = verify_public_key_syntax(request.args.get('account').strip())
    except (ValueError, TypeError):
        return jsonify({
            "result": "fail",
            "reson": "Params account not included or invalid"
        })
    return jsonify(contract_manager.createNewExchangeContract(account, wallet))



@app.route("/api/exchange/buy_token", methods=['POST'])
def buy_token():
    try:
        account = verify_public_key_syntax(request.args.get('account').strip())
        amount = float(request.args.get('amount').strip())
    except (ValueError, TypeError):
        return jsonify({
            "result": "fail",
            "reson": "Params account not included or invalid"
        })
    return jsonify(contract_manager.buyToken(account, amount, wallet))




@app.route("/api/exchange/token_to_ether", methods=['POST'])
def token_to_ether():
    try:
        account = verify_public_key_syntax(request.args.get('account').strip())
        token_amount = int(request.args.get('token_amount').strip())
    except (ValueError, TypeError):
        return jsonify({
            "result": "fail",
            "reson": "Params account not included or invalid"
        })
    approve_transfer = contract_manager.tokenApprove(account, token_amount, wallet)
    if approve_transfer['result'] == "fail":
        return approve_transfer
    return jsonify(contract_manager.tokenToEther(account, token_amount, wallet))




@app.route("/api/exchange/ether_to_token", methods=['POST'])
def ether_to_token():
    try:
        account = verify_public_key_syntax(request.args.get('account').strip())
        eth_amount = float(request.args.get('eth_amount').strip())
    except (ValueError, TypeError):
        return jsonify({
            "result": "fail",
            "reson": "Params account not included or invalid"
        })
    return jsonify(contract_manager.etherToToken(account, eth_amount, wallet))




@app.route("/api/exchange/initialize_lp", methods=['POST'])
def initialize_lp():
    try:
        account = verify_public_key_syntax(request.args.get('account').strip())
        eth_amount = float(request.args.get('eth_amount').strip())
        token_amount = int(request.args.get('token_amount').strip())
    except (ValueError, TypeError):
        return jsonify({
            "result": "fail",
            "reson": "Params not included or invalid"
        })
    approve_transfer = contract_manager.tokenApprove(account, token_amount, wallet)
    if approve_transfer['result'] == "fail":
        return approve_transfer
    
    result = contract_manager.initializeLP(account, token_amount, eth_amount, wallet)
    return jsonify(result)




@app.route("/api/exchange/add_liquidity", methods=['POST'])
def add_liquidity():
    try:
        account = verify_public_key_syntax(request.args.get('account').strip())
        eth_amount = float(request.args.get('eth_amount').strip())
    except (ValueError, TypeError):
        return jsonify({
            "result": "fail",
            "reson": "Params account not included or invalid"
        })

    token_amount = contract_manager.getNumTokensRequired(account, eth_amount, wallet)
    approve_transfer = contract_manager.tokenApprove(account, token_amount, wallet)
    if approve_transfer['result'] == "fail":
        return approve_transfer
    
    add_liquidity = contract_manager.addLiquidity(account, token_amount, eth_amount, wallet)
    if add_liquidity['result'] == "fail":
        return add_liquidity
    return jsonify({
        "result": "success",
        "token_amount": token_amount,
        "eth_amount": eth_amount
        })




@app.route("/api/exchange/details", methods=['GET'])
def get_contract_details():
    try:
        account = verify_public_key_syntax(request.args.get('account').strip())
    except (ValueError, TypeError):
        return jsonify({
            "result": "fail",
            "reson": "Params account not included or invalid"
        })
    return jsonify(contract_manager.getContractDetails(account, wallet))




@app.route("/api/exchange/lp_balance", methods=['GET'])
def get_lp_balance():
    try:
        account = verify_public_key_syntax(request.args.get('account').strip())
    except (ValueError, TypeError):
        return jsonify({
            "result": "fail",
            "reson": "Params account not included or invalid"
        })
    return jsonify(contract_manager.getLPbalance(account, wallet))



@app.route("/api/exchange/lqt_balances", methods=['GET'])
def lqt_balances():
    try:
        account = verify_public_key_syntax(request.args.get('account').strip())
    except (ValueError, TypeError):
        return jsonify({
            "result": "fail",
            "reson": "Params account not included or invalid"
        })
    return jsonify(contract_manager.getLQTBalances(account, wallet))





@app.route("/api/exchange/burn_liquidity", methods=['POST'])
def burn_liquidity():
    try:
        account = verify_public_key_syntax(request.args.get('account').strip())
        lqt_amount = int(request.args.get('lqt_amount').strip())
    except (ValueError, TypeError):
        return jsonify({
            "result": "fail",
            "reson": "Params account not included or invalid"
        })
    return jsonify(contract_manager.burnLiquidity(account, lqt_amount, wallet))




@app.route("/api/exchange/sell_token", methods=['POST'])
def sell_token():
    try:
        account = verify_public_key_syntax(request.args.get('account').strip())
        amount = int(request.args.get('amount').strip())
    except (ValueError, TypeError):
        return jsonify({
            "result": "fail",
            "reson": "Params account not included or invalid"
        })
    approve_transfer = contract_manager.tokenApprove(account, amount, wallet)
    if approve_transfer['result'] == "fail":
        return approve_transfer
    return jsonify(contract_manager.sellToken(account, amount, wallet))



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=False)

