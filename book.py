from crypt import methods
from json import dumps
from datetime import datetime
import mimetypes
import re
from unicodedata import category
from urllib import response
from flask import Flask,jsonify,Response,request
import pymongo
import json
from bson.objectid import ObjectId

app = Flask(__name__)

try:
    mongo = pymongo.MongoClient(
        host='localhost', 
        port=27017,
        username='akhilesh1', 
        password='akhilesh'    
        )
    db = mongo.test

except Exception as ex1:
    print(ex1)

@app.route('/',methods=['GET'])
def helloWorls():
    return "hello World"

@app.route('/book',methods=['GET','POST'])
def createOrFindBook():
    if request.method=='POST':
        try: 
            book = request.get_json()

            dbResponse = db.books.insert_one(book)
            print(dbResponse.inserted_id)
            return Response(
                response=json.dumps(
                    {
                        "message":"book added"
                    }
                ),
                mimetype="application/json"
            )
            
        except Exception as ex:
            print(ex)
    
    elif request.method=='GET':
        try: 
            name = request.args.get('name')
            rent_upper_bound = request.args.get('rent_upper_bound') or "5"
            rent_lower_bound = request.args.get('rent_lower_bound') or "0"
            category = request.args.get('category')

            if name is not None and rent_upper_bound is None and rent_lower_bound is None and category is None :
                data = list(db.books.find({{ "name" : {'$regex' : ".*" + name + ".*"}}}))
                for book in data:
                    book["_id"] = str(book["_id"])
                print(data)
                return Response(
                    response=json.dumps(data)
                )
            elif (name is not None and rent_upper_bound is not None and rent_lower_bound is not None and category is None): 
                data1 = list(db.books.find({ '$and' : [{ "name" : {'$regex' : ".*" + name + ".*"}},{ "rent per day" :{'$gte' : int(rent_lower_bound)}},{ "rent per day" :{'$lte' : int(rent_upper_bound)}}]}))
                for book in data1:
                    book["_id"] = str(book["_id"])
                print(data1)
                return Response(
                    response=json.dumps(data1)
                )
            elif (name is None and rent_upper_bound is not None and rent_lower_bound is not None and category is None): 
                data2 = list(db.books.find({ '$and' : [{ "rent per day" :{'$gte' : int(rent_lower_bound)}},{ "rent per day" :{'$lte' : int(rent_upper_bound)}}]}))
                for book in data2:
                    book["_id"] = str(book["_id"])
                print(data2)
                return Response(
                    response=json.dumps(data2)
                )
            elif (name is not None and rent_upper_bound is not None and rent_lower_bound is not None and category is not None): 
                data3 = list(db.books.find({ '$and' : [{ "name" : {'$regex' : ".*" + name + ".*"}},{ "rent per day" :{'$gte' : int(rent_lower_bound)}},{ "rent per day" :{'$lte' : int(rent_upper_bound)}},{"category" : category}]}))
                for book in data3:
                    book["_id"] = str(book["_id"])
                print(data3)
                return Response(
                    response=json.dumps(data3)
                )

        except Exception as ex:
            print(ex)

@app.route('/transaction',methods=['GET','PATCH'])
def createOrFindTransaction():
    if request.method=='PATCH':
        try:
            book_name = request.form.get('book_name')
            person_name = request.form.get('person_name')
            issue_date = request.form.get('issue_date')
            return_date = request.form.get('return_date')

            if issue_date is not None:
                data = db.transactions.update_one({"book_name" : book_name,"person_name" : person_name},{'$set' : {"issue_date" : datetime.strptime(issue_date, '%d/%m/%y %H:%M:%S')}},upsert=True)
                return Response(
                    response="issue date is updated"
                )
            elif return_date is not None:
                data = db.transactions.update_one({"book_name" : book_name,"person_name" : person_name},{'$set' : {"return_date" : datetime.strptime(return_date, '%d/%m/%y %H:%M:%S')}},upsert=True)
                return Response(
                    response="return date is updated"
                )
        except Exception as ex:
            print(ex)
    
    elif request.method=='GET':
        try:
            book_name = request.args.get('book_name')
            person_name = request.args.get('person_name')
            date_upper_bound = request.args.get('date_upper_bound')
            date_lower_bound = request.args.get('date_lower_bound')
            
            if book_name is not None:
                data = list(db.transactions.find({"book_name" : book_name}))
                for book in data:
                        book["_id"] = str(book["_id"])
                        book["issue_date"] = str(book["issue_date"])
                        book["return_date"] = str(book["return_date"])
                return Response(
                        response=json.dumps(data)
                    )
            elif person_name is not None:
                data = list(db.transactions.find({"person_name" : person_name}))
                for person in data:
                        person["_id"] = str(person["_id"])
                        person["issue_date"] = str(person["issue_date"])
                        person["return_date"] = str(person["return_date"])
                return Response(
                        response=json.dumps(data)
                    )
            elif (date_upper_bound is not None and date_lower_bound):
                data = list(db.transactions.find({'$and' : [{'issue_date' : {'$lte' : datetime.strptime(date_upper_bound, '%d/%m/%y %H:%M:%S')}},{'issue_date' : {'$gt' : datetime.strptime(date_lower_bound, '%d/%m/%y %H:%M:%S')}}]}))
                for person in data:
                        person["_id"] = str(person["_id"])
                        person["issue_date"] = str(person["issue_date"])
                        person["return_date"] = str(person["return_date"])
                return Response(
                        response=json.dumps(data)
                    )

        except Exception as ex:
            print(ex)


@app.route('/rent/<book_name>',methods=['GET'])
def calculateRent(book_name):
    try:
        print(book_name)
        data = list(db.transactions.find({ '$and' : [{"book_name" : book_name}, {"return_date" : {'$ne' : None}}]}))
        days = 0
        for person in data:
            if (person["return_date"] is not 'return_date'):
                days = days + ((person["return_date"] - person["issue_date"]).days) 
                    
        data2 = list(db.books.find({"name" : book_name}))
        for book in data2:
            rent_per_day = book["rent per day"]
        

        total_rent = days * rent_per_day
        return Response(
            response=json.dumps(total_rent)
        )

    except Exception as ex:
        print(ex)