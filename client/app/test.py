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
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

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

wallet = EthWallet("wallet/db/db")
def create(account_addr):
    print(w3)
    account = wallet.create_w3_account(account_addr)
    w3.eth.default_account = account.address
    DEX = w3.eth.contract(abi=abi, address="0x194e93F58c6F1334E59C922866D2EF986F3aB0bb")

    transaction = DEX.functions.buyTokens(1).buildTransaction({'nonce': w3.eth.get_transaction_count(account), 'value': amount})
    print(f'transaction: {transaction}')
    signed_txn = wallet.signTransaction(account_addr, transaction)

    try:
        tx_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
    except Exception as e:
        print(e)
    
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    contract_address = tx_receipt["contractAddress"]
    print(tx_receipt)
    return {
        "result": "success",
        "dex_contract_address": contract_address
    }



def main():
	x = wallet.get_account_by_password('0x820Fa62Eb7c3464F41426f80784EE6A8cD9Cac10', '1234')
	print(x)
	create('0x820Fa62Eb7c3464F41426f80784EE6A8cD9Cac10')

if __name__ == '__main__':
	main()