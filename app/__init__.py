from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api
from flask_cors import CORS

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    # Enable CORS for all routes
    CORS(app, resources={r"/*": {"origins": "*"}})

    db.init_app(app)

    from app.resources.query import QueryResource
    from app.resources.conversation import ConversationResource

    api = Api(app)
    api.add_resource(QueryResource, '/query')
    api.add_resource(ConversationResource, '/conversation', '/conversation/delete/<int:id>')

    return app
