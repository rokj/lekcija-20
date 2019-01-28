from google.appengine.ext import ndb


# kolekcija == tabela
class Oseba(ndb.Model):
    ime = ndb.StringProperty()
    priimek = ndb.StringProperty()
    naslov = ndb.StringProperty()
    nastanek = ndb.DateTimeProperty(auto_now_add=True)
    izbrisan = ndb.BooleanProperty(default=False)


class Avto(ndb.Model):
    ime = ndb.StringProperty()
    model = ndb.StringProperty()
    lastnik_avtomobila = ndb.StringProperty()
