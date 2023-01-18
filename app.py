from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_restful import Api
from modelos import db
from vistas import VistaApuestas, VistaApuesta, VistaSignIn, VistaLogIn, VistaEventosUsuario, \
    VistaEvento, VistaTerminacionEvento, VistaReporte, VistaDinero
from vistas.vistas import VistaEventos, VistaUsuario

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///eporra.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'frase-secreta'
app.config['PROPAGATE_EXCEPTIONS'] = True

app_context = app.app_context()
app_context.push()

db.init_app(app)
db.create_all()

cors = CORS(app)

api = Api(app)
api.add_resource(VistaSignIn, '/signin')
api.add_resource(VistaLogIn, '/login')
api.add_resource(VistaEventosUsuario, '/usuario/<int:id_usuario>/eventos')
api.add_resource(VistaEvento, '/evento/<int:id_evento>')
api.add_resource(VistaApuestas, '/apuestas')
api.add_resource(VistaApuesta, '/apuesta/<int:id_apuesta>')
api.add_resource(VistaTerminacionEvento, '/evento/<int:id_competidor>/terminacion')
api.add_resource(VistaReporte, '/evento/<int:id_evento>/reporte')
api.add_resource(VistaDinero, '/usuario/<int:id_usuario>/dinero')
api.add_resource(VistaEventos, '/eventos')
api.add_resource(VistaUsuario, '/usuario/<int:id_usuario>' )

jwt = JWTManager(app)
