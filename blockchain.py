# Initialising blockchain list
blockchain = []


def get_last_blockchain_value():
    """ Returns last value in the blockchain """
    if len(blockchain) <= 0:
        return None
    return blockchain[-1]


def add_transaction(transaction_amount, last_transaction=[1]):
    """ Append a new transaction to the blockchain 

    Arguments:
        :transaction_amount: The amount that should be added
        :last_transaction: The last blockchain transaction (default [1])
    """
    if (last_transaction == None):
        last_transaction = [1]
    blockchain.append([last_transaction, transaction_amount])


def get_transaction_value():
    """ Returns the input of the user (a new transaction amount) as a float """
    return float(input('Please enter your transaction amount: '))


def get_user_choice():
    return input('Please enter your choice: ')


def print_blockchain():
    for block in blockchain:
        print(block)


def verify_chain():
    is_valid = True

    for block_index in range(len(blockchain)):
        if block_index == 0:
            continue
        elif blockchain[block_index][0] == blockchain[block_index - 1]:
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
    print('1. Add transaction value')
    print('2. Output blockchain')
    print('h. Manipulate the chain')
    print('0. Exit')
    print('-' * 25)
    user_choice = get_user_choice()

    if user_choice == '1':
        tx_amount = get_transaction_value()
        add_transaction(tx_amount, get_last_blockchain_value())
    elif user_choice == '2':
        print_blockchain()
    elif user_choice == 'h':
        if len(blockchain) >= 1:
            blockchain[0] = 2
    elif user_choice == '0':
        waiting_for_input = False
    else:
        print('Invalid choice')
    if not verify_chain():
        print('Invalid chain')
        break
else:
    print('Goodbye')
