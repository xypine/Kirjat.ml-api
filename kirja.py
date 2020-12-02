class kirja:
    image = ""
    price = 0
    name = "Ei Nimeä?
    prices = []
    conditions = []
    def __init__(self, name="", price=0, prices = [], conditions = [], image=""):
        self.name = name
        self.price = price
        self.prices = prices
        self.conditions = conditions
        self.image = image
    def __str__(self):
        return "Kirja(" + self.name + ":" + str(self.price) + ")"