class Buy(object):
    def __init__(self, buyer, item, price, quantity, seller):
        self.buyer = buyer
        self.item = item
        self.price = price
        self.quantity = quantity
        self.seller = seller

    def __repr__(self):
        return self.buyer, self.item, self.price, self.quantity, self.seller

class Work(object):
    def __init__(self, person=None, org=None, title=None, location=None):
        self.person = person
        self.org = org
        self.title = title
        self.location = location

    def __repr__(self):
        return self.person, self.org, self.title, self.location

class Part(object):
    def __init__(self, location1, location2):
        self.location1 = location1
        self.location2 = location1

    def __repr__(self):
        return self.location1, self.location2