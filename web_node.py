from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

from wallet import Wallet
from blockchain import Blockchain


app = Flask(__name__)
CORS(app)


@app.route('/wallet', methods=['POST'])
def create_keys():
    wallet.create_keys()

    response = None
    status_code = 201

    if wallet.save_keys():
        global blockchain
        blockchain = Blockchain(wallet.public_key, port)

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
        blockchain = Blockchain(wallet.public_key, port)

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


@app.route('/broadcast-transaction', methods=['POST'])
def broadcast_transaction():
    values = request.get_json()
    if not values:
        response = {'message': 'No data'}
        return jsonify(response), 400

    required = ['sender', 'recipient', 'amount', 'signature']
    if not all(key in values for key in required):
        response = {'message': 'Some data is missing'}
        return jsonify(response), 400

    success = blockchain.add_transaction(
        values['recipient'], values['sender'], values['signature'], values['amount'], is_receiving=True)

    if success:
        response = {
            'message': 'Transaction added',
            'transaction': {
                'sender': values['sender'],
                'recipient': values['recipient'],
                'amount': values['amount'],
                'signature': values['signature']
            }
        }

        return jsonify(response), 201
    else:
        response = {
            'message': 'Transaction failed'
        }

        return jsonify(response), 500


@app.route('/broadcast-block', methods=['POST'])
def broadcast_block():
    values = request.get_json()
    if not values:
        response = {'message': 'No data'}
        return jsonify(response), 400

    if 'block' not in values:
        response = {'message': 'Some data is missing'}
        return jsonify(response), 400

    block = values['block']
    if block['index'] == blockchain.chain[-1].index + 1:
        if blockchain.add_block(block):
            response = {'message': 'Block added'}
            return jsonify(response), 201
        else:
            response = {'message': 'Block invalid'}
            return jsonify(response), 500
    elif block['index'] > blockchain.chain[-1].index:
        pass
    else:
        response = {
            'message': 'Blockchain seems to be shorter, block not added'}
        return jsonify(response), 409


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


@app.route('/node', methods=['POST'])
def add_node():
    values = request.get_json()
    if not values:
        response = {
            'message': 'No data'
        }
        return jsonify(response), 400
    if not 'node' in values:
        response = {
            'message': 'No node found'
        }
        return jsonify(response), 400
    node = values['node']
    blockchain.add_peer_node(node)
    response = {
        'message': 'Node added susccessfully',
        'all_nodes': blockchain.get_peer_nodes()
    }
    return jsonify(response), 201


@app.route('/node/<node_url>', methods=['DELETE'])
def remove_node(node_url):
    if node_url == '' or node_url == None:
        response = {
            'message': 'Node not found'
        }
        return jsonify(response), 400

    print(node_url)
    blockchain.remove_peer_node(node_url)
    response = {
        'message': 'Node removed',
        'all_nodes': blockchain.get_peer_nodes()
    }
    return jsonify(response), 200


@app.route('/node', methods=['GET'])
def get_nodes():
    response = {
        'all_nodes': blockchain.get_peer_nodes()
    }
    return jsonify(response), 200


@app.route('/network', methods=['GET'])
def get_network_ui():
    return send_from_directory('ui', 'network.html')


@app.route('/', methods=['GET'])
def get_node_ui():
    return send_from_directory('ui', 'node.html')


if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', type=int, default=5000)
    args = parser.parse_args()
    port = args.port
    wallet = Wallet(port)
    blockchain = Blockchain(wallet.public_key, port)
    app.run(host='0.0.0.0', port=port)
