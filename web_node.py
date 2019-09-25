from flask import Flask, jsonify, request
from flask_cors import CORS

from wallet import Wallet
from blockchain import Blockchain


app = Flask(__name__)
CORS(app)

wallet = Wallet()
blockchain = Blockchain(wallet.public_key)


@app.route('/wallet', methods=['POST'])
def create_keys():
    wallet.create_keys()

    response = None
    status_code = 201

    if wallet.save_keys():
        global blockchain
        blockchain = Blockchain(wallet.public_key)

        response = {
            'public_key': wallet.public_key,
            'private_key': wallet.private_key,
            'funds': blockchain.get_balance()
        }
    else:
        response = {
            'message': 'Saving the keys failed'
        }
        status_code = 500

    return jsonify(response), status_code


@app.route('/wallet', methods=['GET'])
def load_keys():
    response = None
    status_code = 201

    if wallet.load_keys():
        global blockchain
        blockchain = Blockchain(wallet.public_key)

        response = {
            'public_key': wallet.public_key,
            'private_key': wallet.private_key,
            'funds': blockchain.get_balance()
        }
    else:
        response = {
            'message': 'Saving the keys failed'
        }
        status_code = 500

    return jsonify(response), status_code


@app.route('/balance', methods=['GET'])
def get_balance():
    response = None
    status_code = 200

    balance = blockchain.get_balance()

    if balance != None:
        response = {
            'message': 'Success',
            'balance': balance
        }
    else:
        response = {
            'message': 'Loading balance failed',
            'wallet_set_up': wallet.public_key != None
        }
        status_code = 500

    return jsonify(response), status_code


@app.route('/transactions', methods=['GET'])
def get_open_transactions():
    transactions = [tx.__dict__ for tx in blockchain.get_open_transactions()]

    return jsonify(transactions), 200


@app.route('/chain', methods=['GET'])
def get_chain():
    chain_snapshot = blockchain.chain
    dict_chain = [block.__dict__.copy() for block in chain_snapshot]

    for block in dict_chain:
        block['transactions'] = [tx.__dict__.copy()
                                 for tx in block['transactions']]

    return jsonify(dict_chain), 200


@app.route('/transaction', methods=['POST'])
def add_transaction():
    required_fields = ['recipient', 'amount']

    if wallet.public_key == None:
        response = {
            'message': 'No wallet setup'
        }

        return jsonify(response), 400

    req_body = request.get_json()

    if ((not req_body) or (not all(field in req_body for field in required_fields))):
        response = {
            'message': 'Required data is missing'
        }

        return jsonify(response), 400

    sender = str(wallet.public_key).strip()
    recipient = req_body['recipient']
    amount = req_body['amount']

    signature = wallet.sign_transaction(sender, recipient, amount)
    if blockchain.add_transaction(recipient, sender, signature, amount):
        response = {
            'message': 'Transaction added',
            'transaction': {
                'sender': sender,
                'recipient': recipient,
                'amount': amount,
                'signature': signature
            },
            'funds': blockchain.get_balance()
        }

        return jsonify(response), 201
    else:
        response = {
            'message': 'Transaction failed'
        }

        return jsonify(response), 500


@app.route('/mine', methods=['POST'])
def mine():
    block = blockchain.mine_block()
    if block != None:
        dict_block = block.__dict__.copy()
        dict_block['transactions'] = [tx.__dict__.copy()
                                      for tx in dict_block['transactions']]

        response = {
            'message': 'Block added successfully',
            'block': dict_block,
            'funds': blockchain.get_balance()
        }

        return jsonify(response), 201
    else:
        response = {
            'message': 'Adding a block failed',
            'wallet_set_up': wallet.public_key != None
        }

        return jsonify(response), 500


@app.route('/', methods=['GET'])
def get_ui():
    return 'Praise the Lord'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
