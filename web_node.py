from flask import Flask, jsonify
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
        response = {
            'public_key': wallet.public_key,
            'private_key': wallet.private_key
        }
        global blockchain
        blockchain = Blockchain(wallet.public_key)
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
        response = {
            'public_key': wallet.public_key,
            'private_key': wallet.private_key
        }
        global blockchain
        blockchain = Blockchain(wallet.public_key)
    else:
        response = {
            'message': 'Saving the keys failed'
        }
        status_code = 500

    return jsonify(response), status_code


@app.route('/', methods=['GET'])
def get_ui():
    return 'Praise the Lord'


@app.route('/chain', methods=['GET'])
def get_chain():
    chain_snapshot = blockchain.chain
    dict_chain = [block.__dict__.copy() for block in chain_snapshot]

    for block in dict_chain:
        block['transactions'] = [tx.__dict__.copy()
                                 for tx in block['transactions']]

    return jsonify(dict_chain), 200


@app.route('/mine', methods=['POST'])
def mine():
    block = blockchain.mine_block()
    if block != None:
        dict_block = block.__dict__.copy()
        dict_block['transactions'] = [tx.__dict__.copy()
                                      for tx in dict_block['transactions']]

        response = {
            'message': 'Block added successfully',
            'block': dict_block
        }

        return jsonify(response), 201
    else:
        response = {
            'message': 'Adding a block failed',
            'wallet_set_up': wallet.public_key != None
        }

        return jsonify(response), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
