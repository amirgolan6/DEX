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

MIN_CONTRACT_TIME = 0 # in days
MAX_CONTRACT_TIME = 36500 # in days
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
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


def getTokenContractAddress(account_addr, contract_address, wallet):
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
        addr = DEX.functions.getTokenContractAddress().call()
    except Exception as e:
        return {
            "result": "fail",
            "reason": str(e)
        }

    return {
        "result": "success",
        "addr": addr
    }

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
        "transaction": tx_receipt['status']
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

def initialize(account, tok_amount, eth_amount, wallet, contract_address):
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

        transaction = DEX.functions.initialize(tok_amount).buildTransaction({
                                "gasPrice": w3.eth.gas_price, 
                                "from": account, 
                                'nonce': w3.eth.get_transaction_count(account),
                                'value': eth_amount
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
        "tx_receipt": tx_receipt['status']
        }

def tokenApprove(account_addr, token_contract_address, dex_contract_address, amount, wallet):
    if not wallet.is_unlocked(account_addr):
        return {
            "result": "fail",
            "reason": "Creating account is not known or it's locked - Try unlocking with password first"
        }
    account = wallet.create_w3_account(account_addr)
    
    w3.eth.default_account = account.address
    
    TOKEN = w3.eth.contract(
        address=token_contract_address,
        abi=token_abi
    )
    try:
        transaction = TOKEN.functions.approve(dex_contract_address, amount).buildTransaction({
                                "gasPrice": w3.eth.gas_price, 
                                "from": account_addr, 
                                'nonce': w3.eth.get_transaction_count(account_addr),
                            })
    except Exception as e:
        logging.error(f'error: {e}')  
        return {
            "result": "fail",
            "reason": str(e)
        }
    signed_txn = wallet.signTransaction(account_addr, transaction)

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
        "approved": tx_receipt['status']
        }

def tokenAllowence(account_addr, token_contract_address, dex_contract_address, wallet):
    if not wallet.is_unlocked(account_addr):
        return {
            "result": "fail",
            "reason": "Creating account is not known or it's locked - Try unlocking with password first"
        }
    account = wallet.create_w3_account(account_addr)
    
    w3.eth.default_account = account.address
    
    TOKEN = w3.eth.contract(
        address=token_contract_address,
        abi=token_abi
    )
    try:
        allowance = TOKEN.functions.allowance(account_addr, dex_contract_address).call()
        #balance = TOKEN.functions.balanceOf(account_addr).call()
    except Exception as e:
        return {
            "result": "fail",
            "reason": str(e)
        }

    return {
        "result": "success",
        "allowance": allowance
    }


def tokenToEther(account, token_amount,dex_contract_address, wallet):
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
        address=dex_contract_address,
        abi=abi
    )

    w3.eth.default_account = w3_account.address
    try:
        logging.info(f'before transaction execution token2ether')
        transaction = DEX.functions.tokenToEthSwap(token_amount).buildTransaction({
                            "gasPrice": w3.eth.gas_price, 
                            "from": account,
                            'nonce': w3.eth.get_transaction_count(account),
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
    status = tx_receipt['status']
    logging.info(f'tok2ether receipt: {status}')
    return {
        "result": "success",
        "reason": f"success"
    }

def main():
    x = wallet.get_account_by_password('0x820Fa62Eb7c3464F41426f80784EE6A8cD9Cac10', '1234')
    print(x)

	#create('0x820Fa62Eb7c3464F41426f80784EE6A8cD9Cac10')
    
    dex_contract_address = createNewExchangeContract('0x820Fa62Eb7c3464F41426f80784EE6A8cD9Cac10', wallet)['dex_contract_address']
    print(f'dex contract address: {dex_contract_address}')

    
    
    buy_txn = buyTokens('0x820Fa62Eb7c3464F41426f80784EE6A8cD9Cac10', 3, wallet, dex_contract_address)['transaction']
    print(f'buy txn: {buy_txn}')

    # sell_txn = sellTokens('0x820Fa62Eb7c3464F41426f80784EE6A8cD9Cac10', 200, wallet, contract_address)['reason']
    # print(f'sell txn: {sell_txn}')

    balance = getTokBalance('0x820Fa62Eb7c3464F41426f80784EE6A8cD9Cac10',dex_contract_address ,wallet)['balance']
    print(f'balance before: {balance}')


    token_contract_address = getTokenContractAddress('0x820Fa62Eb7c3464F41426f80784EE6A8cD9Cac10', dex_contract_address, wallet)['addr']
    print(f'token contract address: {token_contract_address}')

    approved = tokenApprove('0x820Fa62Eb7c3464F41426f80784EE6A8cD9Cac10', token_contract_address, dex_contract_address, 300, wallet)        
    print(f'approved: {approved}')

    allowance = tokenAllowence('0x820Fa62Eb7c3464F41426f80784EE6A8cD9Cac10', token_contract_address, dex_contract_address, wallet)['allowance']
    print(f'allowance: {allowance}')

    # sell_txn = sellTokens('0x820Fa62Eb7c3464F41426f80784EE6A8cD9Cac10', 200, wallet, dex_contract_address)['reason']
    # print(f'sell txn: {sell_txn}')


    init = initialize('0x820Fa62Eb7c3464F41426f80784EE6A8cD9Cac10', 100, 5, wallet, dex_contract_address)
    print(f'init: {init}')

    # balance = getTokBalance('0x820Fa62Eb7c3464F41426f80784EE6A8cD9Cac10',contract_address ,wallet)['balance']
    # print(f'balance after: {balance}')
    token2ether = tokenToEther('0x820Fa62Eb7c3464F41426f80784EE6A8cD9Cac10', 50 ,dex_contract_address, wallet)
    print(f'token2ether: {token2ether}')

if __name__ == '__main__':
	main()