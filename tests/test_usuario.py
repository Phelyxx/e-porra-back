from cmath import log

import json
from unittest import TestCase

from faker import Faker
from faker.generator import random

from app import app

class TestUsuario(TestCase):

    def setUp(self):
        self.data_factory = Faker()
        self.client = app.test_client()

        nuevo_usuario = {
            "usuario": self.data_factory.name(),
            "contrasena": self.data_factory.word(),
            "admin": True
        }

        solicitud_nuevo_usuario = self.client.post("/signin",
                                                   data=json.dumps(nuevo_usuario),
                                                   headers={'Content-Type': 'application/json'})

        respuesta_al_crear_usuario = json.loads(solicitud_nuevo_usuario.get_data())

        self.token = respuesta_al_crear_usuario["token"]
        self.usuario_code = respuesta_al_crear_usuario["id"]

    def test_signin(self):
        self.client = app.test_client()

        nuevo_usuario = {
            "usuario": "Usuario X",
            "contrasena": "contrasena",
            "admin": True
        }

        solicitud_nuevo_usuario = self.client.post("/signin",
                                                   data=json.dumps(nuevo_usuario),
                                                   headers={'Content-Type': 'application/json'})

        respuesta_al_crear_usuario = json.loads(solicitud_nuevo_usuario.get_data())

        self.token = respuesta_al_crear_usuario["token"]
        self.usuario_code = respuesta_al_crear_usuario["id"]    

    def test_login(self):
        
        self.client = app.test_client()
        
        usuario_registrado = {
            "usuario": "Usuario Y",
            "contrasena": "contrasena"
        }

        solicitud_login_usuario = self.client.post("/login",
                                                   data=json.dumps(usuario_registrado),
                                                   headers={'Content-Type': 'application/json'})

        respuesta_al_logear_usuario = json.loads(solicitud_login_usuario.get_data())

        self.token = respuesta_al_logear_usuario["token"]

    def test_update_dinero(self):
        endpoint_dinero = "/usuario/{}/dinero".format(str(self.usuario_code))
        headers = {'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}

        data = {
            "dinero": 20
        }

        solicitud_update_dinero = self.client.put(endpoint_dinero,
                                                   data=json.dumps(data),
                                                   headers=headers)

        respuesta_update_dinero = json.loads(solicitud_update_dinero.get_data())


        endpoint_usuario = "/usuario/{}".format(str(self.usuario_code))
        get_usuario = self.client.get(endpoint_usuario,
                            headers=headers)

        respuesta_get_usuario = json.loads(get_usuario.get_data())

        self.assertEqual(solicitud_update_dinero.status_code, 200)
        self.assertEqual(respuesta_update_dinero['dinero'], respuesta_get_usuario['dinero'])

