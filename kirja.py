class kirja:
    image = ""
    price = 0
    name = "Ei Nimeä?"
    def __init__(self, name="", price=0, image=""):
        self.name = name
        self.price = price
        self.image = image
    def __str__(self):
        return "Kirja(" + self.name + ":" + self.price