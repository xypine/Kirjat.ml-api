class kirja:
    image = ""
    price = 0
    name = "Ei Nimeä?"
    prices = []
    conditions = []
    id = ""
    link = ""
    def __init__(self, name="", price=-1, prices = [], conditions = [], id = -1, image="", link = ""):
        self.name = name
        self.price = price
        self.prices = prices
        self.conditions = conditions
        self.id = id
        self.image = image
        self.link = link
    def __str__(self):
        condition = "NA"
        if len(self.conditions) > 0:
            condition = self.conditions[-1]
        price = self.price
        if len(self.prices) > 0:
            price = self.prices[-1]
        return "Kirja(" + str(self.id) + "|" + self.name + "|" + str(condition) + "|" + str(price) + ")"
    def price_to_e(self, price):
        if len(str(price)) < 4:
            return str(price)
        p = str(price)
        return p[:len(p)-2] + "," + p[-2:]
    def my_price_to_e(self):
        return self.price_to_e(self.price)

    def to_dict(self):
        return {"image": self.image,
                "price" : self.price,
                "name" : self.name,
                "prices" : self.prices,
                "conditions" : self.conditions,
                "id" : self.id,
                "link" : self.link,
                }
