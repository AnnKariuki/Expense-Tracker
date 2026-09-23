import datetime

class Expense:
    """class managing an expense"""
    def __init__(self, id, date, description, amount):
        self._id = id
        self.date = date
        self.description = description
        self.amount = amount

    # we have id with a getter only no setter. we set it when we initialize only then after that when someone tries to set it with exp.id it won't work. it fails with
    # AttributeError: property 'id' of 'Expense' object has no setter hence making our id property read only. publically readable not publically settable
    # a consumer of this class could hypothetically use exp._id when setting the value but this is bad practice as it is known that _ indicates attribute is private and should be used 
    # in the class only
    @property
    def id(self):
        return self._id

    @property
    def date(self):
        return self._date

    @date.setter
    def date(self, value):
        if not isinstance(value, datetime.datetime):
            raise ValueError("date must be a datetime object")
        self._date = value

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        if not isinstance(value, str):
            raise ValueError("Description must be a string")
        self._description = value

    @property
    def amount(self):
        return self._amount

    @amount.setter
    def amount(self, value):
        if not isinstance(value, (int, float)):
            raise ValueError("Amount must be an integer or a float")
        if value <= 0:
            raise ValueError("Amount can not be a negative number or equal 0")
        self._amount = value


exp = Expense(1, datetime.datetime.now(), description = "new", amount=4.0)
print(exp.id)
print(exp.date)
print(exp.description)
print(exp.amount)
exp.amount = 3