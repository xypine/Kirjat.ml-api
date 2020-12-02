class kirja:
    image = ""
    price = 0
    name = "Ei Nimeä?"
    prices = []
    conditions = []
    def __init__(self, name="", price=-1, prices = [], conditions = [], image=""):
        self.name = name
        self.price = price
        self.prices = prices
        self.conditions = conditions
        self.image = image
    def __str__(self):
        condition = "NA"
        if len(self.conditions) > 0:
            condition = self.conditions[-1]
        price = self.price
        if len(self.prices) > 0:
            price = self.prices[-1]
        return "Kirja(" + self.name + ":" + str(condition) + ":" + str(price) + ")"