from flask import Blueprint, Flask, request, jsonify, Response
from .extensions import mongo, sk
#from __init__ import create_app
# from flask_restful import Resource, Api
# from flask_httpauth import HTTPBasicAuth
from bson.json_util import dumps, loads
import json
import jwt
from datetime import date
import datetime
from .auth import api
import pymongo
from SimpleDump import var_dump, dd, dump
from bson import encode
from bson.raw_bson import RawBSONDocument
import ast
from bson.objectid import ObjectId
import numpy as np
from collections import Counter
from flask_cors import CORS, cross_origin


main = Blueprint('main', __name__)
#bp = Blueprint('main', __name__, url_prefix='/main')
# auth = Blueprint('auth', __name__)

app = Flask(__name__)
CORS(app)

cors = CORS(app, resources={
    r"/*": {
        "origins": "*"
    }
})
token = None

# @main.route('/')
# def index():
#     user_collection = mongo.db.user
#     user_collection.insert({'user_id': '1', 'matricola' : '756', 'pass' : '123456', 'role': '1', 'active' : '1'})
#     return 'added'

@main.route('/test' , methods=['GET'])
@cross_origin()
def index2():
    return Response(dumps({
        'content': 'hello world'
    }), mimetype='text/json')
    


# user login api
@main.route('/login', methods=['POST'])
@cross_origin()
def selectt():
    
    #print(sk.config['APPLICATION_ROOT'])
    print (request.is_json)
    content = ast.literal_eval(json.dumps(request.get_json()))
    myquery = { "matricola":  content['matricola'], "pass": content['pass']}
    #print (myquery)
    # print (content['value'])
    # print (content['timestamp'])
    #return 'JSON posted'
    # myquery = { "matricola":  content['matricola']}
    user_collection = mongo.db.user
    mydoc = user_collection.find(myquery)
    
            
    #result = []
    #result.append(mydoc)
    # for x in mydoc:
    #     print(x)
    list_cur = list(mydoc)
    if len(list_cur) != 0:
    # Converting to the JSON
        json_data = dumps(list_cur, indent =0).replace("\n","").replace(" ", "") 
    #print (jsonify({'users': json_data}))
        obj = json.loads(json_data) 
        #token = {'user_id': obj[0]['matricola'], 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY']
        token = jwt.encode({'user_id': obj[0]['matricola'], 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=3000)}, sk.config['SECRET_KEY'])  
        #print (type(token))
        # if(obj != ''): 
        #     print (type(obj[0]))
        
        #user_token start
        # first check in user_token user entry if its already mention then only update token
        # other wise insert user data
        usertoken_collection = mongo.db.user_token
        myquery = { "matricola":  obj[0]['matricola']}
        findUserToken = usertoken_collection.find(myquery)
        list_user_token = list(findUserToken)

        # if condition 

        if len(list_user_token) !=0:
            user_token_json_data = dumps(list_user_token, indent =0).replace("\n","").replace(" ", "") 
            obj2 = json.loads(user_token_json_data)
            myquery = { "token": obj2[0]['token'] }
            newvalues = { "$set": { "token": token } }

            usertoken_collection.update_one(myquery, newvalues)
        else:
            usertoken_collection.insert({'user_id': obj[0]['user_id'], 'matricola' : obj[0]['matricola'], 'token' : token, 'active' : 'Y'})
        #user_token end

        return {'Status': '200', 'data': obj[0], 'token': token}
        #return {'Status': '200', 'data': obj[0], 'token' : token.decode('UTF-8')}
    else:
        return {'Status': '404', 'data': '', 'token' : ''}
    #return json.dumps({'users': json_data})
    #return jsonify({'list_of_authors' : result})


# add category
@main.route('/addcat', methods=['POST'])
@cross_origin()
def addcat():
    token = request.headers.get('token')
    matricola = request.headers.get('matricola')

    #print(token, matricola)

    # print(request.get_json())
    # content = ast.literal_eval(json.dumps(request.get_json()))
    content = request.get_json()
    print(content[0]['_id'])
    myquery = { "matricola":  matricola, "token": token}
    user_token_collection = mongo.db.user_token
    mydoc = user_token_collection.find(myquery)
   
    list_cur = list(mydoc)
    #print(type(list_cur))
    if len(list_cur) != 0:
        menu_collection = mongo.db.menu_category
        d = menu_collection.find({}).sort( "cat_id", -1).limit(1)
        f = dumps(list(d), indent =0).replace("\n","").replace(" ", "") 
        parsed = json.loads(f)
        print(parsed[0]['cat_id']+1)
        try:
            #menu_collection.create_index([("cat_name", 1)], unique=True)
            menu_collection.insert({'_id': content[0]['_id'] , 'cat_id': content[0]['cat_id'], 'cat_name' : content[0]['cat_name'], 'cat_description' : content[0]['cat_description']})
            # menu_collection.insert_one({'cat_id': parsed[0]['cat_id']+1, 'cat_name' : content['cat_name'], 'cat_description' : content['cat_description']})
            return {'Status' : '200', 'data' : 'Category successfully added', 'token': ''}
        except pymongo.errors.DuplicateKeyError as e:
            return {'Status' : '404', 'data' : 'Duplicate data not allowed, Category name must be unique', 'token': ''}
    else:
        return {'Status' : '404', 'data' : 'Your session has been expired', 'token': ''}

#Fetch Category name all or id wise
@main.route('/getcat', methods=['POST', 'GET'])
@cross_origin()
def getcat():
    token = request.headers.get('token')
    matricola = request.headers.get('matricola')
    # print(matricola)
    # print(token)
    # print (request.is_json)
    # print(request.args.get('id'))
    getCatId = request.args.get('id')
    # content = ast.literal_eval(json.dumps(request.get_json()))
    # content = request.get_json()
    # print(content['id'])
    # print(type(content))
    myquery = { "matricola":  matricola, "token": token}
    user_token_collection = mongo.db.user_token
    mydoc = user_token_collection.find(myquery)
   
    list_cur = list(mydoc)
    #print(type(list_cur))
    if len(list_cur) != 0:
        # print('aya')
        menu_collection = mongo.db.menu_category
        #content = request.get_json()
        # if len(content) !=0:
        # if(content['id'] != ''):
        if(getCatId != ''):
            #content = request.get_json()
            myquery = { "_id":  ObjectId(getCatId)}
            print(myquery)
            # print(type(content))
            print(len(myquery))
            mydoc = menu_collection.find(myquery)
        else:
            mydoc = menu_collection.find()
        list_menu_collection = list(mydoc)
        if len(list_menu_collection) != 0:
            menu_collection_json_data = dumps(list_menu_collection, indent =0).replace("\n","").replace(" ", "") 
            obj2 = json.loads(menu_collection_json_data)
            #print(obj2[0]['_id']['$oid'])
            return {'Status': '200', 'data': obj2, 'token': ''}
        else:
            return {'Status': '404', 'data': 'No Data Found', 'token': ''}
    else:
        return {'Status': '404', 'data': 'Your session has been expired', 'token': ''}

#add menu item
@main.route('/addmenu', methods=['POST'])
@cross_origin()
def addmenu():
    token = request.headers.get('token')
    matricola = request.headers.get('matricola')
    #content = ast.literal_eval(json.dumps(request.get_json()))
    content = request.get_json()
    #print(type(content))
    
    myquery = { "matricola":  matricola, "token": token}
    user_token_collection = mongo.db.user_token
    mydoc = user_token_collection.find(myquery)
    
    list_cur = list(mydoc)
    #print(type(list_cur))
    if len(list_cur) != 0:
        menu_collection = mongo.db.menu
        d = menu_collection.find({}).sort( "cat_id", -1).limit(1)
        f = dumps(list(d), indent =0).replace("\n","").replace(" ", "") 
        parsed = json.loads(f)
        #print(parsed[0]['menu_id']+1)

        # check duplicate record start
        uniqueDataCount = 0
        uniqueData = []
        getDuplicateData = []
        showDuplicateMenuName = []
        #count = 0
        #for idx, val in enumerate(content):
        for doc in content:
            menuraw = menu_collection.find({'cat_id': doc['cat_id'], 'menu_name' : doc['menu_name']})
            checkMenu = list(menuraw)
            menu_collection_json_data = dumps(checkMenu, indent =0).replace("\n","").replace(" ", "") 
            obj2 = json.loads(menu_collection_json_data)
            if len(obj2) > 0:
                getDuplicateData.append(obj2)
            else:
                uniqueDataCount +=1
                uniqueData = menu_collection.insert(doc)
        for i, val in enumerate(getDuplicateData):
            for k, v in enumerate(val):
                showDuplicateMenuName.append(v['menu_name'])
                #print (k, ",",v['menu_name'])
        # print('----------------------------------')
        print(showDuplicateMenuName)
        if(len(getDuplicateData) > 0 and uniqueDataCount > 0):
            return{'Status' : '200', 'data' : 'Menu item register successfully but these data already register with same category', 'duplicate_data' : showDuplicateMenuName , 'token': ''}
        elif(len(getDuplicateData) > 0 and uniqueDataCount == 0):
            return{'Status' : '404', 'data' : 'Duplicate data not allowed, Menu name must be unique, these data already register with same category', 'duplicate_data' : showDuplicateMenuName , 'token': ''}
        elif(len(getDuplicateData) == 0 and uniqueDataCount > 0):
            return{'Status' : '200', 'data' : 'Menu item register successfully', 'duplicate_data' : '' , 'token': ''}
    else:
        return {'Status' : '404', 'data' : 'Your session has been expired', 'duplicate_data' : '', 'token': ''}

#Fetch Menu name all or id wise
@main.route('/getmenu', methods=['POST', 'GET'])
@cross_origin()
def getmenu():
    token = request.headers.get('token')
    matricola = request.headers.get('matricola')
    # content = ast.literal_eval(json.dumps(request.get_json()))
    getCatId = int(request.args.get('cat_id'))
    myquery = { "matricola":  matricola, "token": token}
    user_token_collection = mongo.db.user_token
    mydoc = user_token_collection.find(myquery)
    list_menu_collection = ''
    list_cur = list(mydoc)
    #print(type(list_cur))
    if len(list_cur) != 0:
        menu_collection = mongo.db.menu
        #content = request.get_json()
        # if len(getCatId) !=0:
        # #if(content != ''):
        #     #content = ast.literal_eval(json.dumps(request.get_json()))
        #     myquerys = []
        #     for i in getCatId:
        #         myquery = { i:  getCatId[i]}
        #         myquerys.append(myquery)
        #     print(myquerys)
        #     #print(content.values())
        #     #print(type(content))
        #     #print(len(myquery))
        #     mydoc = menu_collection.find({"$and": myquerys})
        #     list_menu_collection = list(mydoc)
        #     print(mydoc)
        if(getCatId != ''):
            #content = request.get_json()
            myquery = { "cat_id":  getCatId}
            # print(myquery)
            # print(type(content))
            # print(len(myquery))
            mydoc = menu_collection.find(myquery)
            list_menu_collection = list(mydoc)
            # print(list_menu_collection)
        else:
            mydoc = menu_collection.find()
            list_menu_collection = list(mydoc)
        if len(list_menu_collection) != 0:
            menu_collection_json_data = dumps(list_menu_collection, indent =0).replace("\n","").replace(" ", "") 
            obj2 = json.loads(menu_collection_json_data)
            return {'Status': '200', 'data': obj2, 'token': ''}
        else:
            return {'Status': '404', 'data': 'No Data Found', 'token': ''}
    else:
        return {'Status': '404', 'data': 'Your session has been expired', 'token': ''}

# canteen resigtration
@main.route('/canteenreg', methods=['POST'])
@cross_origin()
def canteenreg():
    token = request.headers.get('token')
    matricola = request.headers.get('matricola')
    content = ast.literal_eval(json.dumps(request.get_json()))
    print(content)
    #content = request.get_json()
    myquery = { "matricola":  matricola, "token": token}

    #load user_token collection
    user_token_collection = mongo.db.user_token
    mydoc = user_token_collection.find(myquery)

    #load Cateen_reg collection
    canteen_reg_collection = mongo.db.canteen_reg
    # mongo_docs = []
    # mongo_docs += [content]
    #print(type(mongo_docs['cat_name']))



    list_cur = list(mydoc)
    #print(list_cur)
    if len(list_cur) != 0:

        # find user role 1 for student 2 for cateen person 3 for admin code start

        user_collection = mongo.db.user
        mydoc = user_collection.find({"matricola":  matricola})
        userDetail = list(mydoc)

        getUser_role_json_data = dumps(userDetail, indent =0).replace("\n","").replace(" ", "") 
        userRole = json.loads(getUser_role_json_data)
         # find user role 1 for student 2 for cateen person 3 for admin code end
        #dd(userRole[0])
        if (userRole[0]['role']) == 3:
            try:
                #canteen_reg_collection.create_index([("can_name", 1)], unique=True)
                #canteen_reg_collection.insert ( {"_id": "canteenId" , "seq": 0 } )
                # def getNextSequence(seq):
                #     ret = canteen_reg_collection.find_and_modify
                #     ({ "query": { "_id": seq },
                #                 "update": { "$inc": { "seq": 1 } },
                #                 "new": True
                #             }
                #     )
                #     return ret.seq
                # canteen_reg_collection.insert ( {"_id": getNextSequence("canteenId") , "seq": 0 } )
                #menu_collection = mongo.db.menu
                # d = canteen_reg_collection.find({}).sort( "can_id", -1).limit(1)
                # f = dumps(list(d), indent =0).replace("\n","").replace(" ", "") 
                # parsed = json.loads(f)
                # myquerys = []
                # for i in content:
                #     myquery = { i:  content[i]}
                #     myquerys.append(myquery)
                # print(myquerys)
                # print(len(content))
                canteen_reg_collection.insert(content)
                return {'Status' : '200', 'data' : 'Canteen register successfully', 'token': ''}
            except pymongo.errors.DuplicateKeyError as e:
                return {'Status' : '404', 'data' : 'Duplicate data not allowed, Canteen name must be unique', 'token': ''}
        else:
            return{'Status': '404', 'data': 'Only admin has been right to register new canteen', 'token': ''}
    else:
        return {'Status': '404', 'data': 'Your session has been expired', 'token': ''}


#Fetch canteen list name all or id wise
@main.route('/getcanteenlist', methods=['POST', 'GET'])
@cross_origin()
def getcanteenlist():
    token = request.headers.get('token')
    matricola = request.headers.get('matricola')
    # print(matricola)
    # print(token)
    # print (request.is_json)
    getCanId = request.args.get('can_id')
    # content = ast.literal_eval(json.dumps(request.get_json()))
    # content = request.get_json()
    # print(content['id'])
    # print(type(content))
    myquery = { "matricola":  matricola, "token": token}
    user_token_collection = mongo.db.user_token
    mydoc = user_token_collection.find(myquery)
   
    list_cur = list(mydoc)
    #print(type(list_cur))
    if len(list_cur) != 0:
        # print('aya')
        canteen_reg_collection = mongo.db.canteen_reg
        #content = request.get_json()
        # if len(content) !=0:
        if(getCanId != ''):
            #content = request.get_json()
            myquery = { "_id":  ObjectId(getCanId)}
            # print(myquery)
            # print(type(content))
            # print(len(myquery))
            mydoc = canteen_reg_collection.find(myquery)
        else:
            mydoc = canteen_reg_collection.find()
        list_canteen_reg_collection = list(mydoc)
        if len(list_canteen_reg_collection) != 0:
            canteen_collection_json_data = dumps(list_canteen_reg_collection, indent =0).replace("\n","") 
            
            obj2 = json.loads(canteen_collection_json_data)
            #print(obj2[0]['_id']['$oid'])
            return {'Status': '200', 'data': obj2, 'token': ''}
        else:
            return {'Status': '404', 'data': 'No Data Found', 'token': ''}
    else:
        return {'Status': '404', 'data': 'Your session has been expired', 'token': ''}



# dine_take_away resigtration
@main.route('/dintake', methods=['POST'])
@cross_origin()
def dintake():
    token = request.headers.get('token')
    matricola = request.headers.get('matricola')
    content = ast.literal_eval(json.dumps(request.get_json()))
    dumps(content)
    #content = request.get_json()
    myquery = { "matricola":  matricola, "token": token}

    #load user_token collection
    user_token_collection = mongo.db.user_token
    mydoc = user_token_collection.find(myquery)

    #load dine_take_away collection
    dine_take_away_collection = mongo.db.dine_take_away

    list_cur = list(mydoc)
    #print(list_cur)
    if len(list_cur) != 0:

         # find user role 1 for student 2 for cateen person 3 for admin code start

        user_collection = mongo.db.user
        mydoc = user_collection.find({"matricola":  matricola})
        userDetail = list(mydoc)

        getUser_role_json_data = dumps(userDetail, indent =0).replace("\n","").replace(" ", "") 
        userRole = json.loads(getUser_role_json_data)

         # find user role 1 for student 2 for cateen person 3 for admin code end
        #dd(userRole[0])
        if (userRole[0]['role']) == 3:
            try:
                dine_take_away_collection.create_index([("din_name", 1)], unique=True)
                dine_take_away_collection.insert(content)
                return {'Status' : '200', 'data' : 'Dine / Take away register successfully', 'token': ''}
            except pymongo.errors.DuplicateKeyError as e:
                return {'Status' : '404', 'data' : 'Duplicate data not allowed, Dine / Take away must be unique', 'token': ''}
        else:
            return{'Status': '404', 'data': 'Only admin has been right to register new Dine / Take away', 'token': ''}
    else:
        return {'Status': '404', 'data': 'Your session has been expired', 'token': ''}


#add today menu
@main.route('/addtodaymenu', methods=['POST'])
@cross_origin()
def addtodaymenu():
    token = request.headers.get('token')
    matricola = request.headers.get('matricola')
    can_id = request.headers.get('can_id')
    role = request.headers.get('role')
    #content = ast.literal_eval(json.dumps(request.get_json()))
    content = request.get_json()
    print(content)
    
    myquery = { "matricola":  matricola, "token": token}
    user_token_collection = mongo.db.user_token
    mydoc = user_token_collection.find(myquery)
    
    list_cur = list(mydoc)
    print(type(role))
    #print(type(list_cur))
    if len(list_cur) != 0:
        if(role == "2"):
            today_menu_collection = mongo.db.today_menu

            # check duplicate record start
            uniqueDataCount = 0
            uniqueData = []
            getDuplicateData = []
            showDuplicateMenuName = []
            #count = 0
            #for idx, val in enumerate(content):
            for doc in content:
                menuraw = today_menu_collection.find({'cat_id': doc['cat_id'],'canteen_id': doc['canteen_id'], 'menu_id' : doc['menu_id'], 'date' : doc['date']})
                checkMenu = list(menuraw)
                menu_collection_json_data = dumps(checkMenu, indent =0).replace("\n","").replace(" ", "") 
                obj2 = json.loads(menu_collection_json_data)
                if len(obj2) > 0:
                    getDuplicateData.append(obj2)
                else:
                    uniqueDataCount +=1
                    uniqueData = today_menu_collection.insert(doc)
            for i, val in enumerate(getDuplicateData):
                for k, v in enumerate(val):
                    showDuplicateMenuName.append(v['menu_id'])
                    #print (k, ",",v['menu_name'])
            # print('----------------------------------')
            print(showDuplicateMenuName)
            if(len(getDuplicateData) > 0 and uniqueDataCount > 0):
                return{'Status' : '200', 'data' : 'Today menu insert successfully', 'duplicate_data' : showDuplicateMenuName , 'token': ''}
            elif(len(getDuplicateData) > 0 and uniqueDataCount == 0):
                return{'Status' : '404', 'data' : 'Duplicate data not allowed, Menu name must be unique, these menu already insert today menu with same category', 'duplicate_data' : showDuplicateMenuName , 'token': ''}
            elif(len(getDuplicateData) == 0 and uniqueDataCount > 0):
                return{'Status' : '200', 'data' : 'Today menu insert successfully', 'duplicate_data' : '' , 'token': ''}
            
        else:
            print(role)
            return {'Status': '404', 'data': 'You have no access'}
        # print(today_menu_collection)
    else:
        return {'Status': '404', 'data': 'Your session has been expired'}
   
    # else:
    #     return {'Status' : '404', 'data' : 'Your session has been expired', 'duplicate_data' : '', 'token': ''}
    #         today_menu_collection.insert(content)        
    #         print(type(content))
    #         print(content)
    #         


#Fetch TodayMenu canteen wise 
@main.route('/gettodaymenu', methods=['POST', 'GET'])
@cross_origin()
def gettodaymenu():
    token = request.headers.get('token')
    matricola = request.headers.get('matricola')
    getCanId = int(request.args.get('can_id'))
    # print(getCanId)
    myquery = { "matricola":  matricola, "token": token}
    user_token_collection = mongo.db.user_token
    mydoc = user_token_collection.find(myquery)
    # print(mydoc)
    
    # get today date and day
    tDate = date.today()
    currentDate = tDate.strftime("%d/%m/%Y")
    now = datetime.datetime.now()
    currentDay = now.strftime("%A")

    # print("today date", currentDate.strftime("%d/%m/%Y"), 'day name', currentDay)
    # print(datetime.datetime.today().weekday())


    list_cur = list(mydoc)
    #print(type(list_cur))
    if len(list_cur) != 0:
        # today_menu_collection = mongo.db.today_menu
        # if(getCanId != ''):
        #     myquery = [{ "canteen_id":  getCanId, "date" : currentDate}]
        #     # print(myquery)
        #     mydoc = today_menu_collection.find({"$and": myquery})
        #     # print(list(mydoc))
        # else:
        #     mydoc = today_menu_collection.find()
        # list_today_menu_collection = list(mydoc)
        # # print(type(list_today_menu_collection))
        # # print(list_today_menu_collection)
        # if len(list_today_menu_collection) != 0:
        # print('here')
        cur1 = mongo.db.today_menu.aggregate([
                    {
                        '$match': { "canteen_id":  getCanId, "date" : currentDate},
                    },
                    {
                        '$lookup': {
                            'from': "menu",
                            'localField': "menu_id",
                            'foreignField': "_id",
                            'as': "MenuName"
                        }
                    }
                    ,
                    { '$unwind': "$MenuName" },
                    {
                        '$lookup': {
                            'from': "canteen_reg",
                            'localField': "canteen_id",
                            'foreignField': "_id",
                            'as': "CanteenName"
                        }
                    },
                    { '$unwind': "$CanteenName" },
                    {
                        '$lookup': {
                            'from': "menu_category",
                            'localField': "cat_id",
                            'foreignField': "_id",
                            'as': "CategoryName"
                        }
                    },
                    { '$unwind': "$CategoryName" },
                    {
                        '$project': {
                                            
                            'menuId': "$MenuName.menu_id",
                            'menuName': "$MenuName.menu_name",
                            'catId': "$CategoryName.cat_id",
                            'catName': "$CategoryName.cat_name",
                            'canteenId' : "$CanteenName.canteen_id",
                            'canteenName':"$CanteenName.can_name"
                        }
                    }
                ],)

        list_cur1 = list(cur1)
        todyMenuJson =list_cur1
            # return jsonify(TodayMenu=list_cur1)
        if len(list_cur1) != 0:
            return {'Status': '200', 'data': todyMenuJson, 'Repeat': '', 'token': ''}
            # return jsonify(TodayMenu=list_cur1)
        # else:
        #     cur1 = mongo.db.today_menu.aggregate([
        #                 {
        #                     '$match': { "canteen_id":  getCanId, "day" : currentDay},
        #                 },
        #                 {
        #                     '$lookup': {
        #                         'from': "menu",
        #                         'localField': "menu_id",
        #                         'foreignField': "_id",
        #                         'as': "MenuName"
        #                     }
        #                 }
        #                 ,
        #                 { '$unwind': "$MenuName" },
        #                 {
        #                     '$lookup': {
        #                         'from': "canteen_reg",
        #                         'localField': "canteen_id",
        #                         'foreignField': "_id",
        #                         'as': "CanteenName"
        #                     }
        #                 },
        #                 { '$unwind': "$CanteenName" },
        #                 {
        #                     '$lookup': {
        #                         'from': "menu_category",
        #                         'localField': "cat_id",
        #                         'foreignField': "_id",
        #                         'as': "CategoryName"
        #                     }
        #                 },
        #                 { '$unwind': "$CategoryName" }
        #                 ,
        #                 {
        #                     '$project': {
                                                
        #                         'menuId': "$MenuName.menu_id",
        #                         'menuName': "$MenuName.menu_name",
        #                         'catId': "$CategoryName.cat_id",
        #                         'catName': "$CategoryName.cat_name",
        #                         'canteenId' : "$CanteenName.canteen_id",
        #                         'canteenName':"$CanteenName.can_name"
        #                     }
        #                 }
        #             ],)
        #     list_cur1 = list(cur1)
        #     # print(list_cur1)
        #     todyMenuJson = list_cur1
        #     if len(list_cur1) != 0:
        #         return {'Status': '200', 'data': todyMenuJson, 'Repeat': 'Last ' + currentDay + ' menu has been repeated' ,'token': ''}
        else:
            return {'Status': '404', 'data': 'No Data Found', 'token': ''}
    else:
        return {'Status': '404', 'data': 'Your session has been expired', 'token': ''}    
















#         #     # print('here1', list_today_menu_collection)
#         #     # print(len(list_today_menu_collection))
#         #     today_menu_collection_json_data = dumps(list_today_menu_collection, indent =0).replace("\n","").replace(" ", "") 
#         #     # print('data', today_menu_collection_json_data)
#         #     obj2 = json.loads(today_menu_collection_json_data)
#         #     print(obj2[0]['_id']['$oid'])
#         #     print(obj2[0]['canteen_id'])
#         #     return {'Status': '200', 'data': obj2, 'Repeat': '', 'token': ''}
#         # # if len(list_today_menu_collection) != 1:
#         # #     return{"here"}
#         # else:
#         #     myquery = [{ "canteen_id":  getCanId, "day" : currentDay}]
#         #     mydoc = today_menu_collection.find({"$and": myquery})
#         #     list_today_menu_collection = list(mydoc)
#         #     if len(list_today_menu_collection) != 0:
#         #         today_menu_collection_json_data = dumps(list_today_menu_collection, indent =0).replace("\n","").replace(" ", "") 
#         #         # print('data', today_menu_collection_json_data)
#         #         obj2 = json.loads(today_menu_collection_json_data)
#         #         #print(obj2[0]['_id']['$oid'])
#         #         return {'Status': '200', 'data': obj2, 'Repeat': 'Last ' + currentDay + ' menu has been repeated' ,'token': ''}
#         #     else:
#         #         return {'Status': '404', 'data': 'No Data Found', 'token': ''}
#     else:
#         return {'Status': '404', 'data': 'Your session has been expired', 'token': ''}



#Fetch TodayMenu canteen wise 
# @main.route('/gettodaymenu', methods=['POST', 'GET'])
# @cross_origin()
# def gettodaymenu():
#     token = request.headers.get('token')
#     matricola = request.headers.get('matricola')
#     getCanId = request.args.get('can_id')
#     # print(getCanId)
#     myquery = { "matricola":  matricola, "token": token}
#     user_token_collection = mongo.db.user_token
#     mydoc = user_token_collection.find(myquery)
#     # print(mydoc)
    
#     # get today date and day
#     tDate = date.today()
#     currentDate = tDate.strftime("%d/%m/%Y")
#     now = datetime.datetime.now()
#     currentDay = now.strftime("%A")

#     # print("today date", currentDate.strftime("%d/%m/%Y"), 'day name', currentDay)
#     # print(datetime.datetime.today().weekday())


#     list_cur = list(mydoc)
#     #print(type(list_cur))
#     if len(list_cur) != 0:
#         today_menu_collection = mongo.db.today_menu
#         if(getCanId != ''):
#             myquery = [{ "canteen_id":  getCanId, "date" : currentDate}]
#             # print(myquery)
#             mydoc = today_menu_collection.find({"$and": myquery})
#             # print(list(mydoc))
#         else:
#             mydoc = today_menu_collection.find()
#         list_today_menu_collection = list(mydoc)
#         # print(type(list_today_menu_collection))
#         if len(list_today_menu_collection) != 0:
#             # print('here1', list_today_menu_collection)
#             # print(len(list_today_menu_collection))
#             today_menu_collection_json_data = dumps(list_today_menu_collection, indent =0).replace("\n","").replace(" ", "") 
#             # print('data', today_menu_collection_json_data)
#             obj2 = json.loads(today_menu_collection_json_data)
#             # print(obj2[0]['_id']['$oid'])
#             # print(obj2[0]['canteen_id'])
#             return {'Status': '200', 'data': obj2, 'Repeat': '', 'token': ''}
#         # if len(list_today_menu_collection) != 1:
#         #     return{"here"}
#         else:
#             myquery = [{ "canteen_id":  getCanId, "day" : currentDay}]
#             mydoc = today_menu_collection.find({"$and": myquery})
#             list_today_menu_collection = list(mydoc)
#             if len(list_today_menu_collection) != 0:
#                 today_menu_collection_json_data = dumps(list_today_menu_collection, indent =0).replace("\n","").replace(" ", "") 
#                 # print('data', today_menu_collection_json_data)
#                 obj2 = json.loads(today_menu_collection_json_data)
#                 #print(obj2[0]['_id']['$oid'])
#                 return {'Status': '200', 'data': obj2, 'Repeat': 'Last ' + currentDay + ' menu has been repeated' ,'token': ''}
#             else:
#                 return {'Status': '404', 'data': 'No Data Found', 'token': ''}
#     else:
#         return {'Status': '404', 'data': 'Your session has been expired', 'token': ''}
