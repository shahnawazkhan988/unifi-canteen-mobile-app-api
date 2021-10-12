from flask import Blueprint
from .extensions import mongo
#from __init__ import create_app
main = Blueprint('main', __name__)

@main.route('/')
def index():
    user_collection = mongo.db.user
    user_collection.insert({'user_id': '1', 'matricola' : '756', 'pass' : '123456', 'role': '1', 'active' : '1'})
    return 'added'