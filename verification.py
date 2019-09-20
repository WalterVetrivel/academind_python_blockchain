from hash_util import hash_block, hash_string_256


class Verification:
    def verify_chain(self, blockchain):
        """ Verify the current blockchain """
        is_valid = True

        for index, block in enumerate(blockchain):
            if index == 0:
                continue
            # Checking previous hash
            elif block.previous_hash == hash_block(blockchain[index - 1]):
                continue
            # Checking proof of work
            elif not self.valid_proof(block.transactions[:-1], block.previous_hash, block.proof):
                is_valid = False
                break
            else:
                is_valid = False
                break

        return is_valid

    def verify_transaction(self, transaction, get_balance):
        """ Verifies whether the transaction is possible, i.e., the participant can afford the transaction

        Arguments:
            :transaction: The transaction to be verified
        """

        sender_balance = get_balance(transaction.sender)
        return sender_balance >= transaction.amount

    def verify_transactions(self, open_transactions, get_balance):
        return all([self.verify_transaction(tx, get_balance) for tx in open_transactions])

    def valid_proof(self, transactions, last_hash, proof):
        """ To check whether a given proof generates a valid hash or not for the given transactions 

        Arguments:
            :transactions: The list of transactions
            :last_hash: The hash of the previous block
            :proof: The number to check if it is a valid proof
        """

        guess = (str([tx.to_ordered_dict() for tx in transactions]) +
                 str(last_hash) + str(proof)).encode()
        guess_hash = hash_string_256(guess)

        return guess_hash[0: 2] == '00'
