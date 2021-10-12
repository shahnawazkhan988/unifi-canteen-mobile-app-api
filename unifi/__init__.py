from flask import Flask
from .extensions import mongo
from .main import main#, auth


def create_app():
    app = Flask(__name__)

    #app.config.from_pyfile('settings.py')
    #mongo.init_app(app)
    #app = Flask(__name__)
    #app.config["MONGO_URI"] = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    #mongo = PyMongo(app)
    app.register_blueprint(main)
   # app.register_blueprint(auth)
    return app
