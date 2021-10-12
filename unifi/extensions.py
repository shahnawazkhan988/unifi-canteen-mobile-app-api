from flask_pymongo import PyMongo
from flask import Flask


#app.config["MONGO_URI"] = "mongodb+srv://xxxxxxxxx"
#mongo = PyMongo(app)
app = Flask(__name__)




app.config['SECRET_KEY']='xxxxxxxxxxxx'
app.config["MONGO_URI"] = "mongodb+srv://xxxxxxxxxxx"
app.config["APPLICATION_ROOT"] = "/api/v1"
app.config["CORS_HEADERS"] = 'Content-Type'
app.config['CORS_ORIGINS'] = ['*']
sk = app
mongo = PyMongo(app)
