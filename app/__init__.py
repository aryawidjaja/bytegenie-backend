from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    db.init_app(app)

    from app.resources.query import QueryResource

    api = Api(app)
    api.add_resource(QueryResource, '/query')

    return app
