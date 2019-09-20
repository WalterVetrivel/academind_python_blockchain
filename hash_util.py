from hashlib import sha256
from json import dumps


def hash_string_256(string):
    return sha256(string).hexdigest()


def hash_block(block):
    """ Generates a hash of the block by converting the block to 
    an utf-8 JSON string and hashing the string using sha256

    Arguments:
        :block: The block that should be hashed
    """
    hashable_block = block.__dict__.copy()
    # sort_keys ensures that the keys are always sorted and hence the hash never changes for the same block
    return sha256(dumps(hashable_block, sort_keys=True).encode()).hexdigest()
