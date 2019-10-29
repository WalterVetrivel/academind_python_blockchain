from functools import reduce
import json
import requests

from utils.hash_util import hash_block, hash_string_256
from utils.verification import Verification
from block import Block
from transaction import Transaction
from wallet import Wallet

MINING_REWARD = 10


class Blockchain:
    def __init__(self, public_key, node_id):
        # Initialising blockchain
        genesis_block = Block(0, '', [], 100, 0)
        self.chain = [genesis_block]
        self.__open_transactions = []
        self.__peer_nodes = set()
        self.public_key = public_key
        self.node_id = node_id
        self.resolve_conflicts = False
        self.load_data()

    @property
    def chain(self):
        return self.__chain[:]

    @chain.setter
    def chain(self, val):
        self.__chain = val

    def get_open_transactions(self):
        return self.__open_transactions[:]

    def load_data(self):
        """ Loads the blockchain and open transactions from file """

        try:
            with open(f'blockchain-{self.node_id}.txt', mode='r') as f:
                file_content = [json.loads(line.rstrip('\n'))
                                for line in f.readlines()]

                self.chain = [
                    Block(
                        block['index'],
                        block['previous_hash'],
                        [
                            Transaction(
                                tx['sender'],
                                tx['recipient'],
                                tx['signature'],
                                tx['amount']
                            )
                            for tx in block['transactions']
                        ],
                        block['proof'],
                        block['timestamp'])
                    for block in file_content[0]
                ]

                self.__open_transactions = [
                    Transaction(
                        tx['sender'],
                        tx['recipient'],
                        tx['signature'],
                        tx['amount']
                    ) for tx in file_content[1]
                ]

                peer_nodes = file_content[2]
                self.__peer_nodes = set(peer_nodes)
        except (IOError, IndexError):
            pass

    def save_data(self):
        """ Saves the blockchain and open transactions to a file """

        try:
            with open(f'blockchain-{self.node_id}.txt', mode='w') as f:
                saveable_chain = [
                    block.__dict__
                    for block in
                    [
                        Block(
                            block.index,
                            block.previous_hash,
                            [
                                tx.__dict__ for tx in block.transactions],
                            block.proof,
                            block.timestamp
                        ) for block in self.__chain
                    ]
                ]

                f.write(json.dumps(saveable_chain))
                f.write('\n')
                saveable_transactions = [
                    tx.__dict__ for tx in self.__open_transactions]
                f.write(json.dumps(saveable_transactions))
                f.write('\n')
                f.write(json.dumps(list(self.__peer_nodes)))
        except IOError:
            print('Saving failed')

    def get_last_blockchain_value(self):
        """ Returns last value in the blockchain """

        return self.__chain[-1]

    def proof_of_work(self):
        """ Calculates proof of work for mining a new block """

        last_block = self.get_last_blockchain_value()
        last_hash = hash_block(last_block)

        proof = 0
        while not Verification.valid_proof(self.__open_transactions, last_hash, proof):
            proof += 1

        return proof

    def get_balance(self, sender=None):
        """ Get the balance of a participant

        Arguments:
            :sender: The sender of the transaction
        """
        if sender == None:
            if self.public_key == None:
                return None

            participant = self.public_key
        else:
            participant = sender

        # Getting all the amounts sent by the participant
        tx_sender = [[tx.amount for tx in block.transactions
                      if tx.sender == participant] for block in self.__chain]
        open_tx_sender = [tx.amount
                          for tx in self.__open_transactions if tx.sender == participant]
        tx_sender.append(open_tx_sender)

        # Calculating the total amount sent
        amount_sent = reduce(
            lambda total, curr: total + sum(curr), tx_sender, 0)

        # Getting all the amounts received by the participant
        tx_recipient = [[tx.amount for tx in block.transactions
                         if tx.recipient == participant] for block in self.__chain]

        # Calculating the total amount received
        amount_received = reduce(
            lambda total, curr: total + sum(curr), tx_recipient, 0)

        return amount_received - amount_sent

    def add_transaction(self, recipient, sender, signature, amount=1.0, is_receiving=False):
        """ Append a new transaction to the blockchain

        Arguments:
            :sender: The sender of the amount
            :recipient: The recipient of the amount
            :amount: The amount of coins sent (default = 1.0)
        """

        # if self.public_key == None:
        #     return False

        transaction = Transaction(sender, recipient, signature, amount)

        if Verification.verify_transaction(transaction, self.get_balance):
            self.__open_transactions.append(transaction)
            self.save_data()
            if not is_receiving:
                for node in self.__peer_nodes:
                    url = f'http://{node}/broadcast-transaction'
                    try:
                        response = requests.post(url, json={
                            'sender': sender, 'recipient': recipient, 'amount': amount, 'signature': signature})
                        if response.status_code == 400 or response.status_code == 500:
                            print('Transaction declined')
                            return False
                    except requests.exceptions.ConnectionError:
                        continue

            return True
        return False

    def mine_block(self):
        """ To mine a new block """

        if self.public_key == None:
            return None

        last_block = self.get_last_blockchain_value()

        # Get hash of last (previous) block
        hashed_block = hash_block(last_block)

        # Calculate proof of work
        proof = self.proof_of_work()

        # Reward for mining
        reward_transaction = Transaction(
            'MINING', self.public_key, '', MINING_REWARD)

        # Copying so that open transactions is not affected if something goes wrong
        copied_transactions = self.__open_transactions[:]

        # Verifying each transaction
        for tx in copied_transactions:
            if not Wallet.verify_transaction(tx):
                return None

        # Adding the reward transaction
        copied_transactions.append(reward_transaction)

        # Creating the new block
        block = Block(len(self.__chain), hashed_block,
                      copied_transactions, proof)

        # Adding the block to the chain
        self.__chain.append(block)
        self.__open_transactions = []
        self.save_data()

        for node in self.__peer_nodes:
            url = f'http://{node}/broadcast-block'
            converted_block = block.__dict__.copy()
            converted_block['transactions'] = [tx.__dict__.copy()
                                               for tx in converted_block['transactions']]

            try:
                response = requests.post(url, json={'block': converted_block})
                if response.status_code == 400 or response.status_code == 500:
                    print('Block declined')
                if response.status_code == 409:
                    self.resolve_conflicts = True
            except requests.exceptions.ConnectionError:
                continue

        return block

    def add_block(self, block):
        transactions = [Transaction(
            tx['sender'], tx['recipient'], tx['signature'], tx['amount']) for tx in block['transactions']]

        # We shouldn't pass in the last transaction, i.e., the minig reward to verify proof of work
        proof_is_valid = Verification.valid_proof(
            transactions[:-1], block['previous_hash'], block['proof'])

        hashes_match = hash_block(self.chain[-1]) == block['previous_hash']

        if not proof_is_valid or not hashes_match:
            return False

        converted_block = Block(
            block['index'], block['previous_hash'], transactions, block['proof'], block['timestamp'])
        self.__chain.append(converted_block)
        stored_transactions = self.__open_transactions[:]
        for itx in block['transactions']:
            for opentx in stored_transactions:
                if opentx.sender == itx['sender'] and opentx.recipient == itx['recipient'] and opentx.amount == itx['amount'] and opentx.signature == itx['signature']:
                    try:
                        self.__open_transactions.remove(opentx)
                    except ValueError:
                        print('Transaction already removed')

        self.save_data()
        return True

    def resolve(self):
        winner_chain = self.chain
        replace = False
        for node in self.__peer_nodes:
            url = f'http://{node}/chain'
            try:
                response = requests.get(url)
                node_chain = response.json()
                node_chain = [Block(block['index'], block['previous_hash'], block['transactions'],
                                    block['proof'], block['timestamp']) for block in node_chain]
                for block in node_chain:
                    block.transactions = [Transaction(
                        tx['sender'], tx['recipient'], tx['signature'], tx['amount']) for tx in block.transactions]

                node_chain_length = len(node_chain)
                winner_chain_length = len(winner_chain)

                if node_chain_length > winner_chain_length and Verification.verify_chain(node_chain):
                    winner_chain = node_chain
                    replace = True

            except requests.exceptions.ConnectionError:
                continue

        self.resolve_conflicts = False
        self.chain = winner_chain
        if replace:
            self.__open_transactions = []
        self.save_data()
        return replace

    def add_peer_node(self, node):
        """ Adds a new node to the peer node set.

        Arguments:
            :node: The node URL which should be added.
        """
        self.__peer_nodes.add(node)
        self.save_data()

    def remove_peer_node(self, node):
        """ Removes a node from the peer node set.

        Arguments:
            :node: The node URL which should be removed.
        """
        self.__peer_nodes.discard(node)
        self.save_data()

    def get_peer_nodes(self):
        """ Return list of all connected peer nodes """
        return list(self.__peer_nodes)
