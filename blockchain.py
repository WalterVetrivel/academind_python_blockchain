from functools import reduce
from collections import OrderedDict
import json

from hash_util import hash_block, hash_string_256
from block import Block

# Initialising blockchain
MINING_REWARD = 10
genesis_block = Block(0, '', [], 100, 0)
blockchain = [genesis_block]
open_transactions = []

owner = 'Walter'
participants = {'Walter'}


def load_data():
    global blockchain
    global open_transactions
    try:
        with open('blockchain.txt', mode='r') as f:
            file_content = [json.loads(line.rstrip('\n'))
                            for line in f.readlines()]

            blockchain = [
                Block(
                    block['index'],
                    block['previous_hash'],
                    [
                        OrderedDict(
                            [
                                ('sender', tx['sender']),
                                ('recipient', tx['recipient']),
                                ('amount', tx['amount'])
                            ]
                        )
                        for tx in block['transactions']
                    ],
                    block['proof'],
                    block['timestamp'])
                for block in file_content[0]
            ]

            open_transactions = [
                OrderedDict(
                    [
                        ('sender', tx['sender']),
                        ('recipient', tx['recipient']),
                        ('amount', tx['amount'])
                    ]
                ) for tx in file_content[1]
            ]
    except (IOError, IndexError):
        genesis_block = Block(0, '', [], 100, 0)
        blockchain = [genesis_block]
        open_transactions = []


load_data()


def save_data():
    try:
        with open('blockchain.txt', mode='w') as f:
            saveable_chain = [block.__dict__ for block in blockchain]
            f.write(json.dumps(saveable_chain))
            f.write('\n')
            f.write(json.dumps(open_transactions))
    except IOError:
        print('Saving failed')


def get_last_blockchain_value():
    """ Returns last value in the blockchain """
    if len(blockchain) <= 0:
        return genesis_block
    return blockchain[-1]


def valid_proof(transactions, last_hash, proof):
    guess = (str(transactions) + str(last_hash) + str(proof)).encode()
    guess_hash = hash_string_256(guess)
    return guess_hash[0: 2] == '00'


def proof_of_work():
    last_block = get_last_blockchain_value()
    last_hash = hash_block(last_block)
    proof = 0
    while not valid_proof(open_transactions, last_hash, proof):
        proof += 1
    return proof


def get_balance(participant):
    # Getting all the amounts sent by the participant
    tx_sender = [[tx['amount'] for tx in block.transactions
                  if tx['sender'] == participant] for block in blockchain]
    open_tx_sender = [tx['amount']
                      for tx in open_transactions if tx['sender'] == participant]
    tx_sender.append(open_tx_sender)

    # Calculating the total amount sent
    amount_sent = reduce(
        lambda total, curr: total + sum(curr), tx_sender, 0)

    # Getting all the amounts received by the participant
    tx_recipient = [[tx['amount'] for tx in block.transactions
                     if tx['recipient'] == participant] for block in blockchain]

    # Calculating the total amount received
    amount_received = reduce(
        lambda total, curr: total + sum(curr), tx_recipient, 0)

    return amount_received - amount_sent


def verify_transaction(transaction):
    sender_balance = get_balance(transaction['sender'])
    return sender_balance >= transaction['amount']


def add_transaction(recipient, sender=owner, amount=1.0):
    """ Append a new transaction to the blockchain

    Arguments:
        :sender: The sender of the amount
        :recipient: The recipient of the amount
        :amount: The amount of coins sent (default = 1.0)
    """
    # Using OrderedDict so that the keys are always in the same order and the hash doesn't change
    transaction = OrderedDict(
        [('sender', sender), ('recipient', recipient), ('amount', amount)])
    if verify_transaction(transaction):
        open_transactions.append(transaction)
        participants.add(sender)
        participants.add(recipient)
        save_data()
        return True
    return False


def mine_block():
    last_block = get_last_blockchain_value()
    # Get hash of last (previous) block
    hashed_block = hash_block(last_block)
    # Calculate proof of work
    proof = proof_of_work()
    # Reward for mining
    # Using OrderedDict so that the order of keys doesn't change and the hash remains the same
    reward_transaction = OrderedDict(
        [('sender', 'MINING'), ('recipient', owner), ('amount', MINING_REWARD)])
    # Copying so that open transactions is not affected if something goes wrong
    copied_transactions = open_transactions[:]
    copied_transactions.append(reward_transaction)
    # Creating the new block
    block = Block(len(blockchain), hashed_block, copied_transactions, proof)
    # Adding the block to the chain
    blockchain.append(block)
    return True


def get_transaction_value():
    """ Returns the input of the user (a new transaction amount) as a float """
    recipient = input('Enter the recipient: ')
    amount = float(input('Enter the amount: '))
    return (recipient, amount)


def get_user_choice():
    return input('Please enter your choice: ')


def print_blockchain():
    for block in blockchain:
        print(block)


def verify_chain():
    """ Verify the current blockchain """
    is_valid = True

    for index, block in enumerate(blockchain):
        if index == 0:
            continue
        # Checking previous hash
        elif block.previous_hash == hash_block(blockchain[index - 1]):
            continue
        # Checking proof of work
        elif not valid_proof(block.transactions[:-1], block.previous_hash, block.proof):
            is_valid = False
            break
        else:
            is_valid = False
            break

    return is_valid


def verify_transactions():
    return all([verify_transaction(tx) for tx in open_transactions])


waiting_for_input = True

while waiting_for_input:
    print()
    print('Please choose'.upper())
    print('-' * 25)
    print('1. Add transaction')
    print('2. Mine block')
    print('3. Output blockchain')
    print('4. Output participants')
    print('5. Check transaction validity')
    print('0. Exit')
    print('-' * 25)
    user_choice = get_user_choice()

    if user_choice == '1':
        tx_data = get_transaction_value()
        recipient, amount = tx_data
        if add_transaction(recipient, amount=amount):
            print('Added transaction')
        else:
            print('Transaction failed')
        print(open_transactions)
    elif user_choice == '2':
        if mine_block():
            open_transactions = []
            save_data()
    elif user_choice == '3':
        print_blockchain()
    elif user_choice == '4':
        print(participants)
    elif user_choice == '5':
        verify_transactions()
    elif user_choice == '0':
        waiting_for_input = False
    else:
        print('Invalid choice')
    if not verify_chain():
        print('Invalid chain')
        break
    print('The balance of {} is {:6.2f}'.format(owner, get_balance(owner)))
else:
    print('Goodbye')
