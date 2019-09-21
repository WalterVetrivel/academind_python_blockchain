from functools import reduce
import json

from utils.hash_util import hash_block, hash_string_256
from utils.verification import Verification
from block import Block
from transaction import Transaction
from wallet import Wallet

MINING_REWARD = 10


class Blockchain:
    def __init__(self, hosting_node_id):
        # Initialising blockchain
        genesis_block = Block(0, '', [], 100, 0)
        self.chain = [genesis_block]
        self.__open_transactions = []
        self.load_data()
        self.hosting_node = hosting_node_id

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
            with open('blockchain.txt', mode='r') as f:
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
        except (IOError, IndexError):
            pass

    def save_data(self):
        """ Saves the blockchain and open transactions to a file """

        try:
            with open('blockchain.txt', mode='w') as f:
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

    def get_balance(self):
        """ Get the balance of a participant

        Arguments:
            :participant: A participant in the blockchain
        """

        participant = self.hosting_node

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

    def add_transaction(self, recipient, sender, signature, amount=1.0):
        """ Append a new transaction to the blockchain

        Arguments:
            :sender: The sender of the amount
            :recipient: The recipient of the amount
            :amount: The amount of coins sent (default = 1.0)
        """

        if self.hosting_node == None:
            return False

        transaction = Transaction(sender, recipient, signature, amount)

        if Verification.verify_transaction(transaction, self.get_balance):
            self.__open_transactions.append(transaction)
            self.save_data()
            return True

        return False

    def mine_block(self):
        """ To mine a new block """

        if self.hosting_node == None:
            return False

        last_block = self.get_last_blockchain_value()

        # Get hash of last (previous) block
        hashed_block = hash_block(last_block)

        # Calculate proof of work
        proof = self.proof_of_work()

        # Reward for mining
        reward_transaction = Transaction(
            'MINING', self.hosting_node, '', MINING_REWARD)

        # Copying so that open transactions is not affected if something goes wrong
        copied_transactions = self.__open_transactions[:]

        # Verifying each transaction
        for tx in copied_transactions:
            if not Wallet.verify_transaction(tx):
                return False

        # Adding the reward transaction
        copied_transactions.append(reward_transaction)

        # Creating the new block
        block = Block(len(self.__chain), hashed_block,
                      copied_transactions, proof)

        # Adding the block to the chain
        self.__chain.append(block)
        self.__open_transactions = []
        self.save_data()
        return True
