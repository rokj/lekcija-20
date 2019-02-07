#!/usr/bin/env python
import os
import jinja2
import webapp2
import logging
import json

from models import Oseba, Avto
from google.appengine.api import users
from google.appengine.api import urlfetch


template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=False)


class BaseHandler(webapp2.RequestHandler):

    def write(self, *a, **kw):
        return self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        return self.write(self.render_str(template, **kw))

    def render_template(self, view_filename, params=None):
        if params is None:
            params = {}
        template = jinja_env.get_template(view_filename)
        return self.response.out.write(template.render(params))


class MainHandler(BaseHandler):
    def get(self):
        user = users.get_current_user()

        logging.info("tukaj sem")
        logging.info(user)

        login_url = False
        logout_url = False

        if not user:
            login_url = users.create_login_url('/')
        else:
            logout_url = users.create_logout_url('/')

        params = {
            'user': user,
            'login_url': login_url,
            'logout_url': logout_url
        }

        return self.render_template("home.html", params=params)

class BlogHandler(BaseHandler):
    def post(self):
        tisto_kar_sem_vnesel = self.request.get("vnos")

        logging.info("tukaj sem 1")

        dodatne_stvari = {
            "sporocilo": "Uspesno si vnesel komentar",
            "tisto_kar_sem_vnesel_plus_nekaj": tisto_kar_sem_vnesel + " dodatno besedilo"
        }

        logging.info("tukaj sem 2 " + tisto_kar_sem_vnesel)

        return self.render_template("blog.html", params=dodatne_stvari)

    def get(self):
        dodatne_stvari = {
            "ime": "Janez",
            # "priimek": "Novak"
        }

        return self.render_template("blog.html", params=dodatne_stvari)

class FakebookHandler(BaseHandler):
    def get(self):
        return self.render_template("fakebook1.html")


class VnosHandler(BaseHandler):
    def post(self):
        vnos = self.request.get("vnos")
        ime = self.request.get("ime")
        skrita_stevilka = self.request.get("skrita_stevilka")

        logging.info("ime: " + ime)
        logging.info("skrtita stevilka:" + skrita_stevilka)

        return self.render_template("vnos.html")


class KalkulatorHandler(BaseHandler):
    def get(self):
        return self.render_template("kalkulator.html")

    def post(self):
        prva_stevilka = self.request.get("prva_stevilka")
        druga_stevilka = self.request.get("druga_stevilka")
        akcija = self.request.get("akcija")

        if akcija == "+":
            vsota = int(prva_stevilka) + int(druga_stevilka)
        elif akcija == "-":
            vsota = int(prva_stevilka) - int(druga_stevilka)
        params = {
            "vsota": vsota
        }

        return self.render_template("kalkulator.html", params=params)


class SeznamOsebHandler(BaseHandler):
    def get(self):
        seznam = Oseba.query(Oseba.izbrisan==False).fetch()

        params = {
            'seznam': seznam
        }

        return self.render_template("seznam-oseb.html", params=params)


class VnosOsebeHandler(BaseHandler):
    def get(self):
        return self.render_template("vnos-osebe.html")

    def post(self):
        vneseno_ime = self.request.get("ime")
        vnesen_priimek = self.request.get("priimek")
        vnesen_naslov = self.request.get("naslov")

        oseba = Oseba(
            ime=vneseno_ime,
            priimek=vnesen_priimek,
            naslov=vnesen_naslov
        )
        # save v bazo
        oseba.put()

        avto = Avto(
            ime="Alfa",
            model="S1",
            lastnik_avtomobila=str(oseba.key.id())
        )
        avto.put()

        params = {
            "sporocilo": "Uspesno sem vnesel podatke!"
        }

        return self.render_template("vnos-osebe.html", params=params)


class OsebaHandler(BaseHandler):
    def get(self, oseba_id):
        oseba = Oseba.get_by_id(int(oseba_id))

        params = {
            'oseba': oseba
        }

        return self.render_template("oseba.html", params=params)

class UrediOsebaHandler(BaseHandler):
    def get(self, oseba_id):
        oseba = Oseba.get_by_id(int(oseba_id))

        params = {
            'oseba': oseba
        }

        return self.render_template("uredi-oseba.html", params=params)

    def post(self, oseba_id):
        # pridobili osebo iz baze
        oseba = Oseba.get_by_id(int(oseba_id))

        # posodobi podatke v objektu
        oseba.ime = self.request.get("ime")
        oseba.priimek = self.request.get("priimek")
        oseba.naslov = self.request.get("naslov")

        # shrani nazaj v bazo
        oseba.put()

        params = {
            'oseba': oseba,
            'sporocilo': 'Uspesno si posodil podatke'
        }

        return self.render_template("uredi-oseba.html", params=params)


class IzbrisiOsebaHandler(BaseHandler):
    def get(self, oseba_id):
        oseba = Oseba.get_by_id(int(oseba_id))

        params = {
            'oseba': oseba
        }

        return self.render_template("izbrisi-oseba.html", params=params)

    def post(self, oseba_id):
        # pridobili osebo iz baze
        oseba = Oseba.get_by_id(int(oseba_id))

        # izbrise iz baze
        # oseba.key.delete()
        oseba.izbrisan = True
        oseba.put()

        params = {
            'sporocilo': 'Uspesno si izbrisal osebo'
        }

        return self.render_template("izbrisi-oseba.html", params=params)


class PeoplesHandler(BaseHandler):
    def get(self):

        data = open("people.json", "r").read() # preberemo podatke iz datoteke

        json_data = json.loads(data) # spremenimo vse podatke iz datoteke, ki so v stringu
        # v python dictionary

        logging.info(json_data) # izpisemo v log

        params = {
            'peoples': json_data
        }

        return self.render_template("peoples.html", params=params)

class WeatherHandler(BaseHandler):
    def get(self):
        url = "https://api.openweathermap.org/data/2.5/find?q=Ljubljana&units=metric&appid=e7208c603e1c0961db13207af0ba8901"
        result = urlfetch.fetch(url) # to je v json stringu

        json_data = json.loads(result.content) # spremenimo vse podatke iz datoteke, ki so v stringu
        # v python dictionary

        logging.info(json_data) # izpisemo v log

        params = {
            'data': json_data
        }

        return self.render_template("weather.html", params=params)




app = webapp2.WSGIApplication([
    webapp2.Route('/', MainHandler),
    webapp2.Route('/blog', BlogHandler),
    webapp2.Route('/fakebook', FakebookHandler),
    webapp2.Route('/vnos-komentarja', VnosHandler),
    webapp2.Route('/kalkulator', KalkulatorHandler),
    webapp2.Route('/seznam-oseb', SeznamOsebHandler),
    webapp2.Route('/vnos-osebe', VnosOsebeHandler),
    webapp2.Route('/oseba/<oseba_id:\d+>', OsebaHandler),
    webapp2.Route('/oseba/<oseba_id:\d+>/uredi', UrediOsebaHandler),
    webapp2.Route('/oseba/<oseba_id:\d+>/izbrisi', IzbrisiOsebaHandler),

    webapp2.Route('/peoples', PeoplesHandler),
    webapp2.Route('/weather', WeatherHandler),
], debug=True)
