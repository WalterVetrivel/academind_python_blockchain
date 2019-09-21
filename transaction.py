from collections import OrderedDict

from utils.printable import Printable


class Transaction(Printable):
    """ A transaction which can be added to the blockchain

    Attributes:
        :sender: The sender of the coins
        :recipient: The recipient of the coins
        :signature: The signature of the transaction
        :amount: The amount of coins sent
    """

    def __init__(self, sender, recipient, signature, amount):
        self.sender = sender
        self.recipient = recipient
        self.signature = signature
        self.amount = amount

    def to_ordered_dict(self):
        return OrderedDict([('sender', self.sender), ('recipient', self.recipient), ('amount', self.amount)])
