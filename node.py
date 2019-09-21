from uuid import uuid4

from blockchain import Blockchain
from utils.verification import Verification


class Node:
    def __init__(self):
        # self.id = str(uuid4())
        self.id = 'Walter'
        self.blockchain = Blockchain(self.id)

    def get_transaction_value(self):
        """ Returns the input of the user (a new transaction amount) as a float """

        recipient = input('Enter the recipient: ')
        amount = float(input('Enter the amount: '))
        return (recipient, amount)

    def get_user_choice(self):
        return input('Please enter your choice: ')

    def print_blockchain(self):
        for block in self.blockchain.chain:
            print(block)

    def listen_for_input(self):
        waiting_for_input = True

        while waiting_for_input:
            print()
            print('Please choose'.upper())
            print('-' * 25)
            print('1. Add transaction')
            print('2. Mine block')
            print('3. Output blockchain')
            print('4. Check transaction validity')
            print('0. Exit')
            print('-' * 25)
            user_choice = self.get_user_choice()

            if user_choice == '1':
                tx_data = self.get_transaction_value()
                recipient, amount = tx_data

                if self.blockchain.add_transaction(recipient, self.id, amount):
                    print('Added transaction')
                else:
                    print('Transaction failed')
                print(self.blockchain.get_open_transactions())
            elif user_choice == '2':
                self.blockchain.mine_block()
            elif user_choice == '3':
                self.print_blockchain()
            elif user_choice == '4':
                Verification.verify_transactions(
                    self.blockchain.get_open_transactions(), self.blockchain.get_balance)
            elif user_choice == '0':
                waiting_for_input = False
            else:
                print('Invalid choice')
            if not Verification.verify_chain(self.blockchain.chain):
                print('Invalid chain')
                break
            print('The balance of {} is {:6.2f}'.format(
                self.id, self.blockchain.get_balance()))

        else:
            print('Goodbye')


# Check execution context using __name__ and only execute if it is '__main__'
# This prevents the following code from execution if node is imported and used somewhere else
if __name__ == '__main__':
    node = Node()
    node.listen_for_input()
