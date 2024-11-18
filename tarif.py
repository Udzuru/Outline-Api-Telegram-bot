class Tarif:
    days=0
    price=0
    text=""
    def __init__(self,d,p,t):
        self.days=d
        self.price=p
        self.text=t
class Tarifs:
    text=""
    kb=[]
    def __init__(self,text,lll):
        self.text=text
        self.kb=lll
    