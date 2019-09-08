# Initialising blockchain
genesis_block = {
    'previous_hash': '',
    'index': 0,
    'transactions': []
}
blockchain = [genesis_block]
open_transactions = []
owner = 'Walter'


def hash_block(block):
    return '-'.join([str(block[key]) for key in block])


def get_last_blockchain_value():
    """ Returns last value in the blockchain """
    if len(blockchain) <= 0:
        return genesis_block
    return blockchain[-1]


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
        'amount:': amount
    }
    open_transactions.append(transaction)


def mine_block():
    last_block = get_last_blockchain_value()
    hashed_block = hash_block(last_block)
    print(hashed_block)
    block = {
        'previous_hash': hashed_block,
        'index': len(blockchain),
        'transactions': open_transactions
    }
    blockchain.append(block)


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
    print('h. Manipulate the chain')
    print('0. Exit')
    print('-' * 25)
    user_choice = get_user_choice()

    if user_choice == '1':
        tx_data = get_transaction_value()
        recipient, amount = tx_data
        add_transaction(recipient, amount=amount)
        print(open_transactions)
    elif user_choice == '2':
        mine_block()
    elif user_choice == '3':
        print_blockchain()
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
else:
    print('Goodbye')
