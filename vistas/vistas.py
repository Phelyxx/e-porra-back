from webbrowser import get
from flask import request
from flask_jwt_extended import jwt_required, create_access_token
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from modelos import db, Apuesta, ApuestaSchema, Usuario, UsuarioSchema, Evento, EventoSchema, CompetidorSchema, \
    Competidor, ReporteSchema

apuesta_schema = ApuestaSchema()
evento_schema = EventoSchema()
competidor_schema = CompetidorSchema()
usuario_schema = UsuarioSchema()
reporte_schema = ReporteSchema()
evento_schema = EventoSchema()


class VistaSignIn(Resource):

    def post(self):
        usuario = Usuario.query.filter(Usuario.usuario == request.json["usuario"]).first()

        if not usuario is None:
            return "Ya existe un usuario con ese nombre.", 404
        else:
            nuevo_usuario = Usuario(usuario=request.json["usuario"], contrasena=request.json["contrasena"], admin=request.json["admin"])
            db.session.add(nuevo_usuario)
            db.session.commit()
            token_de_acceso = create_access_token(identity=nuevo_usuario.id)
            return {"mensaje": "usuario creado exitosamente", "token": token_de_acceso, "id": nuevo_usuario.id}

    def put(self, id_usuario):
        usuario = Usuario.query.get_or_404(id_usuario)
        usuario.contrasena = request.json.get("contrasena", usuario.contrasena)
        db.session.commit()
        return usuario_schema.dump(usuario)

    def delete(self, id_usuario):
        usuario = Usuario.query.get_or_404(id_usuario)
        db.session.delete(usuario)
        db.session.commit()
        return '', 204



class VistaLogIn(Resource):

    def post(self):
        usuario = Usuario.query.filter(Usuario.usuario == request.json["usuario"],
                                       Usuario.contrasena == request.json["contrasena"]).first()
        db.session.commit()
        if usuario is None:
            return "El usuario o contraseña es incorrecto.", 404
        else:
            token_de_acceso = create_access_token(identity=usuario.id)
            return {"mensaje": "Inicio de sesión exitoso", "token": token_de_acceso}


class VistaEventosUsuario(Resource):

    @jwt_required()
    def post(self, id_usuario):

        usuario = Usuario.query.get_or_404(id_usuario)
        admin = usuario.admin

        if admin:
            nuevo_evento = Evento(nombre=request.json["nombre"],
                                deporte = request.json["deporte"],
                                tipo = request.json["tipo"])
            probabilitySum = 0                    
            for item in request.json["competidores"]:
                probabilitySum += item["probabilidad"]
                cuota = round((item["probabilidad"] / (1 - item["probabilidad"])), 2)
                competidor = Competidor(nombre_competidor=item["competidor"],
                                        probabilidad=item["probabilidad"],
                                        cuota=cuota,
                                        id_evento=nuevo_evento.id)
                nuevo_evento.competidores.append(competidor)
            if(probabilitySum != 1):
                return "La suma de las probabilidades debe ser 1", 412
            usuario = Usuario.query.get_or_404(id_usuario)
            usuario.eventos.append(nuevo_evento)

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return 'El usuario ya tiene un evento con dicho nombre', 409

        return evento_schema.dump(nuevo_evento)

    @jwt_required()
    def get(self, id_usuario):
        usuario = Usuario.query.get_or_404(id_usuario)
        return [evento_schema.dump(evento) for evento in usuario.eventos]


class VistaEvento(Resource):

    @jwt_required()
    def get(self, id_evento):
        return evento_schema.dump(Evento.query.get_or_404(id_evento))

    @jwt_required()
    def put(self, id_evento):
        evento = Evento.query.get_or_404(id_evento)
        evento.nombre = request.json.get("nombre", evento.nombre)
        evento.tipo = request.json.get("tipo", evento.tipo)
        evento.deporte = request.json.get("deporte", evento.deporte)
        evento.competidores = []
        probabilitySum = 0     
        for item in request.json["competidores"]:
            probabilidad = float(item["probabilidad"])
            probabilitySum += probabilidad
            cuota = round((probabilidad / (1 - probabilidad)), 2)
            competidor = Competidor(nombre_competidor=item["competidor"],
                                    probabilidad=probabilidad,
                                    cuota=cuota,
                                    id_evento=evento.id)
            evento.competidores.append(competidor)
        if(probabilitySum != 1):
            return "La suma de las probabilidades debe ser 1", 412
        db.session.commit()
        return evento_schema.dump(evento)

    @jwt_required()
    def delete(self, id_evento):
        evento = Evento.query.get_or_404(id_evento)
        db.session.delete(evento)
        db.session.commit()
        return '', 204


class VistaApuestas(Resource):

    @jwt_required()
    def post(self):
        nueva_apuesta = Apuesta(valor_apostado=request.json["valor_apostado"],
                                nombre_apostador=request.json["nombre_apostador"],
                                id_competidor=request.json["id_competidor"], id_evento=request.json["id_evento"])
        db.session.add(nueva_apuesta)
        db.session.commit()
        return apuesta_schema.dump(nueva_apuesta)

    @jwt_required()
    def get(self):
        return [apuesta_schema.dump(ca) for ca in Apuesta.query.all()]


class VistaApuesta(Resource):

    @jwt_required()
    def get(self, id_apuesta):
        return apuesta_schema.dump(Apuesta.query.get_or_404(id_apuesta))

    @jwt_required()
    def put(self, id_apuesta):
        apuesta = Apuesta.query.get_or_404(id_apuesta)
        apuesta.valor_apostado = request.json.get("valor_apostado", apuesta.valor_apostado)
        apuesta.nombre_apostador = request.json.get("nombre_apostador", apuesta.nombre_apostador)
        apuesta.id_competidor = request.json.get("id_competidor", apuesta.id_competidor)
        apuesta.id_evento = request.json.get("id_evento", apuesta.id_evento)
        db.session.commit()
        return apuesta_schema.dump(apuesta)

    @jwt_required()
    def delete(self, id_apuesta):
        apuesta = Apuesta.query.get_or_404(id_apuesta)
        db.session.delete(apuesta)
        db.session.commit()
        return '', 204


class VistaTerminacionEvento(Resource):

    def put(self, id_competidor):
        competidor = Competidor.query.get_or_404(id_competidor)
        competidor.es_ganador = True
        evento = Evento.query.get_or_404(competidor.id_evento)
        evento.abierto = False

        for apuesta in evento.apuestas:
            if apuesta.id_competidor == competidor.id:
                apuesta.ganancia = apuesta.valor_apostado + (apuesta.valor_apostado/competidor.cuota)
            else:
                apuesta.ganancia = 0

        db.session.commit()
        return competidor_schema.dump(competidor)


class VistaReporte(Resource):

    @jwt_required()
    def get(self, id_evento):
        eventoReporte = Evento.query.get_or_404(id_evento)
        ganancia_casa_final = 0

        for apuesta in eventoReporte.apuestas:
            ganancia_casa_final = ganancia_casa_final + apuesta.valor_apostado - apuesta.ganancia

        reporte = dict(evento=eventoReporte, ganancia_casa=ganancia_casa_final)
        schema = ReporteSchema()
        return schema.dump(reporte)

class VistaEventos(Resource):

    @jwt_required()
    def get(self):
        return [evento_schema.dump(ca) for ca in Evento.query.all()]

# Vista que permite gestionar los competidores que participaran en un evento. Crea, actualiza y elimina los competidores de un evento registrado.
class VistaCompetidoresEvento(Resource):

    @jwt_required()
    def post(self, id_Evento):
        nuevo_competidor = Competidor(nombre_competidor=request.json["nombre_competidor"],
                            probabilidad = request.json["probabilidad"],
                            cuota = request.json["cuota"],
                            es_ganador = request.json["es_ganador"],
                            id_evento = request.json["id_evento"])
        evento = Evento.query.get_or_404(id_Evento)
        evento.competidores.append(nuevo_competidor)

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return 'El evento ya tiene un competidor con dicho nombre', 409

        return evento_schema.dump(nuevo_competidor)

    @jwt_required()
    def get(self, id_Evento):
        evento = Evento.query.get_or_404(id_Evento)
        return [competidor_schema.dump(competidor) for competidor in evento.competidores]

    @jwt_required()
    def delete(self, id_Evento, nombre_competidor):
        evento = Evento.query.get_or_404(id_Evento)
        competidor = Competidor.query.filter_by(nombre_competidor='nombre_competidor')
        evento.competidores.remove(competidor)
        return '', 200

class VistaCompetidor(Resource):

    @jwt_required()
    def get(self, id_competidor):
        return competidor_schema.dump(Competidor.query.get_or_404(id_competidor))

    @jwt_required()
    def put(self, id_competidor):
        competidor = Competidor.query.get_or_404(id_competidor)
        competidor.nombre_competidor = request.json.get("nombre_competidor", competidor.nombre_competidor)
        competidor.probabilidad = request.json.get("probabilidad", competidor.probabilidad)
        competidor.cuota = request.json.get("cuota", competidor.cuota)
        competidor.es_ganador = request.json.get("es_ganador", competidor.es_ganador)
        competidor.id_evento = request.json.get("id_evento", competidor.id_evento)
        db.session.commit()
        return competidor_schema.dump(competidor)

    @jwt_required()
    def delete(self, id_competidor):
        competidor = Competidor.query.get_or_404(id_competidor)
        db.session.delete(competidor)
        db.session.commit()
        return '', 204
        
class VistaUsuario(Resource):

    @jwt_required()
    def get(self, id_usuario):
        return usuario_schema.dump(Usuario.query.get_or_404(id_usuario))


class VistaDinero(Resource):
    @jwt_required()
    def put(self, id_usuario):
        usuario = Usuario.query.get_or_404(id_usuario)
        usuario.dinero = request.json.get("dinero", usuario.dinero)
        db.session.commit()
        return usuario_schema.dump(usuario)