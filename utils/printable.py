""" A base class with repr method to print the object as a dictionary """


class Printable:
    def __repr__(self):
        return str(self.__dict__)
