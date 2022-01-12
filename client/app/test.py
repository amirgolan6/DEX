from datetime import datetime, timedelta

from flask.json.tag import TagTuple
from web3 import Web3
from web3.middleware import geth_poa_middleware
#from solc import compile_standard
from solcx import compile_standard
import json, os
from eth_account.messages import encode_defunct
import logging
from wallet.wallet import EthWallet

w3 = Web3(Web3.HTTPProvider('https://eth.ap.idc.ac.il'))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

MIN_CONTRACT_TIME = 0 # in days
MAX_CONTRACT_TIME = 36500 # in days
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
wallet = EthWallet("wallet/db/db")
comp = {
	"language": "Solidity",
	"sources": {
	    "exchange.sol": {
	        "content":
	            open("contracts/exchange.sol", "r").read()
	    },
	},
	"settings": {
	    "outputSelection": { "*": { "*": [ "*" ], "": [ "*" ] } }
		}
	}
compiled_sol = compile_standard(comp)
bytecode = compiled_sol['contracts']['exchange.sol']['DEX']['evm']['bytecode']['object']
abi = json.loads(compiled_sol['contracts']['exchange.sol']['DEX']['metadata'])['output']['abi']

token_bytecode = compiled_sol['contracts']['exchange.sol']['ERC20Basic']['evm']['bytecode']['object']
token_abi = json.loads(compiled_sol['contracts']['exchange.sol']['ERC20Basic']['metadata'])['output']['abi']
def getTokBalance(account_addr, contract_address, wallet):
    if not wallet.is_unlocked(account_addr):
        return {
            "result": "fail",
            "reason": "Creating account is not known or it's locked - Try unlocking with password first"
        }
    account = wallet.create_w3_account(account_addr)
    
    w3.eth.default_account = account.address
    
    DEX = w3.eth.contract(
        address=contract_address,
        abi=abi
    )

    try:
        balance = DEX.functions.getTokBalance(account.address).call()
    except Exception as e:
        return {
            "result": "fail",
            "reason": str(e)
        }

    return {
        "result": "success",
        "balance": balance
    }

def createNewExchangeContract(account_addr, wallet):
    if not wallet.is_unlocked(account_addr):
        return {
            "result": "fail",
            "reason": "Creating account is not known or it's locked - Try unlocking with password first"
        }
    account = wallet.create_w3_account(account_addr)
    
    w3.eth.default_account = account.address
    
    Exchange = w3.eth.contract(abi=abi, bytecode=bytecode)
    transaction = Exchange.constructor().buildTransaction({
                                "gasPrice": w3.eth.gas_price, 
                                "from": account_addr, 
                                'nonce': w3.eth.get_transaction_count(account_addr),
                                })#({'nonce': w3.eth.get_transaction_count(account_addr)})
    signed_txn = wallet.signTransaction(account_addr, transaction)

    try:
        tx_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
    except Exception as e:
        return {
            "result": "fail",
            "reason": str(e)
        }
    
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    contract_address = tx_receipt["contractAddress"]
    #self.contract_address = contract_address
    return {
        "result": "success",
        "dex_contract_address": contract_address
    }

def buyTokens(account, amount, wallet, contract_address):
    if not wallet.is_unlocked(account):
        return {
            "result": "fail",
            "reason": "Creating account is not known or it's locked - Try unlocking with password first"
        }
    w3_account = wallet.create_w3_account(account);
    if w3_account == "Unknown Account":
        return {
            "result": "fail",
            "reason": "Account is unknown or locked. Try unlocking first"
        }

    DEX = w3.eth.contract(
        address=contract_address,
        abi=abi
    )

    w3.eth.default_account = w3_account.address
    try:

        transaction = DEX.functions.buyTokens(amount).buildTransaction({
                                "gasPrice": w3.eth.gas_price, 
                                "from": account, 
                                'nonce': w3.eth.get_transaction_count(account),
                                'value': amount
                                })
    except Exception as e:
        logging.error(f'error: {e}')  
        return {
            "result": "fail",
            "reason": str(e)
        }
    signed_txn = wallet.signTransaction(account, transaction)

    try:
        tx_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
    except Exception as e:
        logging.error(f'error: {e}')
        return {
            "result": "fail",
            "reason": str(e)
        }

    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    return {
        "result": "success",
        "transaction": transaction
        }


def sellTokens(account, amount, wallet, contract_address):
    if not wallet.is_unlocked(account):
        return {
            "result": "fail",
            "reason": "Creating account is not known or it's locked - Try unlocking with password first"
        }
    w3_account = wallet.create_w3_account(account);
    if w3_account == "Unknown Account":
        return {
            "result": "fail",
            "reason": "Account is unknown or locked. Try unlocking first"
        }

    DEX = w3.eth.contract(
        address=contract_address,
        abi=abi
    )

    w3.eth.default_account = w3_account.address
    try:
        approved = DEX.functions.approve(w3_account.address, amount).call()
        print(f'approved: {approved}')
        if not approved:
            logging.error(f'Failed to sell token, unapproved transaction')
            return {
                "result": "fail",
                "reason": "Failed to sell token, unapproved transaction"
            }
        sold = DEX.functions.sellTokens(amount).transact({
                                "gasPrice": w3.eth.gas_price, 
                                "from": account, 
                                'nonce': w3.eth.get_transaction_count(account),
                                'value': amount
                                })
        logging.info(f"sold:{sold}")
        if not sold:
            logging.error(f'Failed to sell token, unapproved transaction')
            return {
                "result": "fail",
                "reason": "Failed to sell token, unapproved transaction"
            }

    except Exception as e:
        logging.error(f'error: {e}')  
        return {
            "result": "fail",
            "reason": str(e)
        }

    return {
        "result": "success",
        "reason": f"Successfully sold {amount} Ether in token from contract {self.contract_address}"
    }



def main():
    x = wallet.get_account_by_password('0x820Fa62Eb7c3464F41426f80784EE6A8cD9Cac10', '1234')
    print(x)

	#create('0x820Fa62Eb7c3464F41426f80784EE6A8cD9Cac10')
    
    #contract_address = createNewExchangeContract('0x820Fa62Eb7c3464F41426f80784EE6A8cD9Cac10', wallet)['dex_contract_address']
    #print(contract_address)
    
    contract_address = '0x0319fFa06f1593240A0b46cA772aabedA0BE1D3e'
    
    buy_txn = buyTokens('0x820Fa62Eb7c3464F41426f80784EE6A8cD9Cac10', 3, wallet, contract_address)['transaction']
    print(f'buy txn: {buy_txn}')

    # sell_txn = sellTokens('0x820Fa62Eb7c3464F41426f80784EE6A8cD9Cac10', 200, wallet, contract_address)['reason']
    # print(f'sell txn: {sell_txn}')

    balance = getTokBalance('0x820Fa62Eb7c3464F41426f80784EE6A8cD9Cac10',contract_address ,wallet)
    print(f'balance: {balance}')

if __name__ == '__main__':
	main()