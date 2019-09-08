# Initialising blockchain
MINING_REWARD = 10
genesis_block = {
    'previous_hash': '',
    'index': 0,
    'transactions': []
}
blockchain = [genesis_block]
open_transactions = []
owner = 'Walter'
participants = {'Walter'}


def hash_block(block):
    return '-'.join([str(block[key]) for key in block])


def get_balance(participant):
    tx_sender = [[tx['amount'] for tx in block['transactions']
                  if tx['sender'] == participant] for block in blockchain]
    open_tx_sender = [tx['amount']
                      for tx in open_transactions if tx['sender'] == participant]
    tx_sender.append(open_tx_sender)

    amount_sent = 0
    for tx in tx_sender:
        if(len(tx) > 0):
            amount_sent += tx[0]

    tx_recipient = [[tx['amount'] for tx in block['transactions']
                     if tx['recipient'] == participant] for block in blockchain]

    amount_received = 0
    for tx in tx_recipient:
        if(len(tx) > 0):
            amount_received += tx[0]

    return amount_received - amount_sent


def get_last_blockchain_value():
    """ Returns last value in the blockchain """
    if len(blockchain) <= 0:
        return genesis_block
    return blockchain[-1]


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
    transaction = {
        'sender': sender,
        'recipient': recipient,
        'amount': amount
    }
    if verify_transaction(transaction):
        open_transactions.append(transaction)
        participants.add(sender)
        participants.add(recipient)
        return True
    return False


def mine_block():
    last_block = get_last_blockchain_value()
    hashed_block = hash_block(last_block)
    reward_transaction = {
        'sender': 'MINING',
        'recipient': owner,
        'amount': MINING_REWARD
    }
    copied_transactions = open_transactions[:]
    copied_transactions.append(reward_transaction)
    block = {
        'previous_hash': hashed_block,
        'index': len(blockchain),
        'transactions': copied_transactions
    }
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
        elif block['previous_hash'] == hash_block(blockchain[index - 1]):
            continue
        else:
            is_valid = False
            break

    return is_valid


waiting_for_input = True

while waiting_for_input:
    print()
    print('Please choose'.upper())
    print('-' * 25)
    print('1. Add transaction')
    print('2. Mine block')
    print('3. Output blockchain')
    print('4. Output participants')
    print('h. Manipulate the chain')
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
    elif user_choice == '3':
        print_blockchain()
    elif user_choice == '4':
        print(participants)
    elif user_choice == 'h':
        if len(blockchain) >= 1:
            blockchain[0] = {
                'previous_hash': '',
                'index': 0,
                'transactions': [{'sender': 'A', 'recipient': 'Walter', 'amount': 100}]
            }
    elif user_choice == '0':
        waiting_for_input = False
    else:
        print('Invalid choice')
    if not verify_chain():
        print('Invalid chain')
        break
    print(get_balance(owner))
else:
    print('Goodbye')
