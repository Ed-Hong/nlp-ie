class Buy(object):
    def __init__(self, buyer, item, price, quantity, seller):
        self.buyer = buyer
        self.item = item
        self.price = price
        self.quantity = quantity
        self.seller = seller

    def __repr__(self):
        return self.buyer, self.item, self.price, self.quantity, self.seller

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

class Work(object):
    def __init__(self, person=None, org=None, title=None, location=None):
        self.person = person
        self.org = org
        self.title = title
        self.location = location

    def __repr__(self):
        return self.person, self.org, self.title, self.location

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

class Part(object):
    def __init__(self, part=None, whole=None):
        self.part = part
        self.whole = whole

    def __repr__(self):
        return self.part, self.whole

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False