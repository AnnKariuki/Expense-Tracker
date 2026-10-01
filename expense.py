import datetime

class Expense:
    """class managing an expense"""
    def __init__(self, id, date, description, amount, category):
        self._id = id
        self.date = date
        self.description = description
        self.amount = amount
        self.category = category

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
        # we will have the date here remain a datetime object and we will not change it to a string. the conversion belongs in the persistence boundary where we store the value as a string and
        # when we load it we turn it back to a datetime object
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
        if not isinstance(value, float):
            raise ValueError("Amount must be a float")
        if value < 0:
            raise ValueError("Amount can not be a negative number")
        self._amount = value

    @property
    def category(self):
        return self._category

    @category.setter
    def category(self, value):
        if not isinstance(value, str):
            raise ValueError("Category must be a string")
        self._category = value.lower()

    # we are going to define this to customize how expense objects are compared for equality using the == operator. this will help in the way we write test where without this we would have to compare each attribute of different expense objects to determine is assertequal is true
    # When you write a == b, Python internally translates that expression into a method call: a.__eq__(b)
    # By default, custom user-defined classes inherit their __eq__ behavior from the base object class. This default implementation checks for object identity, meaning it only returns True if both variables point to the exact same object in memory (identical to using the is operator)
    # If you want two distinct object instances with identical attribute values to be considered equal, you must override __eq_
    def __eq__(self, other):
        return self._id == other._id and self.date == other.date and self.description == other.description and self.amount == other.amount and self.category == other.category
