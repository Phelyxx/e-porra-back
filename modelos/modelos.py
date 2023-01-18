from flask_sqlalchemy import SQLAlchemy
from marshmallow import fields, Schema
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
import enum

db = SQLAlchemy()


class Apuesta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    valor_apostado = db.Column(db.Numeric)
    ganancia = db.Column(db.Numeric, default=0)
    nombre_apostador = db.Column(db.String(128))
    id_competidor = db.Column(db.Integer, db.ForeignKey('competidor.id'))
    id_evento = db.Column(db.Integer, db.ForeignKey('evento.id'))

class TipoEvento(enum.Enum):
   CARRERA = 1
   MARCADOR = 2

class Evento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(128))
    tipo = db.Column(db.Enum(TipoEvento))
    abierto = db.Column(db.Boolean, default=True)
    deporte = db.Column(db.String(128))
    competidores = db.relationship('Competidor', cascade='all, delete, delete-orphan')
    apuestas = db.relationship('Apuesta', cascade='all, delete, delete-orphan')
    usuario = db.Column(db.Integer, db.ForeignKey("usuario.id"))


class Competidor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre_competidor = db.Column(db.String(128))
    probabilidad = db.Column(db.Numeric)
    cuota = db.Column(db.Numeric);
    es_ganador = db.Column(db.Boolean, default=False)
    id_evento = db.Column(db.Integer, db.ForeignKey('evento.id'))


class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(50))
    contrasena = db.Column(db.String(50))
    admin = db.Column(db.Boolean, default=False)
    dinero = db.Column(db.Numeric, default=0)
    eventos = db.relationship('Evento', cascade='all, delete, delete-orphan')
    

class ApuestaSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Apuesta
        include_relationships = True
        include_fk = True
        load_instance = True

    valor_apostado = fields.String()
    ganancia = fields.String()


class CompetidorSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Competidor
        include_relationships = True
        load_instance = True

    probabilidad = fields.String()
    cuota = fields.String()

class EnumADiccionario(fields.Field):
    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return None
        return {"llave": value.name, "valor": value.value}

class EventoSchema(SQLAlchemyAutoSchema):
    tipo = EnumADiccionario(attribute=("tipo"))
    class Meta:
        model = Evento
        include_relationships = True
        load_instance = True

    competidores = fields.List(fields.Nested(CompetidorSchema()))
    apuestas = fields.List(fields.Nested(ApuestaSchema()))
    ganancia_casa = fields.Float()


class UsuarioSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Usuario
        include_relationships = True
        load_instance = True
    dinero = fields.Number()

class ReporteSchema(Schema):
    evento = fields.Nested(EventoSchema())
    ganancia_casa = fields.Float()