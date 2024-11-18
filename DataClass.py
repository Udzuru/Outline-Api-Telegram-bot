import sqlite3
import texts
from datetime import datetime
from servermet import *
from BdLib import Model

date_time = datetime.now()

class User(Model):
    tel_id=0
    date_act=date_time.strftime("%m/%d/%Y, %H:%M:%S")
    days=0
    status="inactive"
class Server(Model):
    id=0
    url=""
    sha256=""
    country=""
class Keys(Model):
    user=0
    server=0
    key=""
    name=""
class Crypto_id(Model):
    id=0
    paid_id=""
    user=0
class Umani_id(Model):
    id=0
    paid_id=""
    user=0
class refs(Model):
    who=""
    whom=""
    status=""
