from flask import Flask, json
from flask import request
from flask import jsonify
from flask.sessions import NullSession
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow.fields import Integer
from marshmallow import Schema
import requests
#init app
app = Flask(__name__)
#init marshmallow
ma = Marshmallow(app)

#For Database "BooksInfo_DB" we filled it by terminal 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///BooksInfo_DB.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

#calss for creating Database table
class Catalog_Server_DB(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(500))
    quantity = db.Column(db.Integer)
    price = db.Column(db.Float)
    topic = db.Column(db.String(500))
     

    def __init__(self,id,title,quantity,price,topic):
        self.id=id
        self.title=title
        self.quantity=quantity
        self.price=price
        self.topic=topic
#dectionary
book={}
#catlog1="172.19.2.60:3000"
#catlog2="172.19.2.60:4000"
#catlog3="172.19.2.60:5000"
#front  ="172.19.2.182:5000"
catlog1="172.19.77.60:3000"
catlog2="172.19.77.60:4000"
#catlog3="172.19.2.60:5000"
front  ="172.19.77.125:5000"
#==================== frontend operations   =====================================================

#==================== 1- search operation =====================================
#get all books that have spicific topic
@app.route("/search/<topic>", methods=['GET'])
def search_by_topic(topic):
    book = Catalog_Server_DB.query.with_entities(Catalog_Server_DB.id,Catalog_Server_DB.title).filter_by(topic=topic.replace("%20"," ")).all()
    if len(book)!=0:
        result = json.dumps(book,indent=2)
        return (result)
    else: 
        return jsonify({topic: "this topic does not exist please try another topic"})

#==================== 2- info operation =====================================
#get all information about spicific book (by id)
@app.route("/info/<bookID>", methods=['GET'])
def get_info_forID(bookID):
    book = Catalog_Server_DB.query.with_entities(Catalog_Server_DB.title,Catalog_Server_DB.topic,Catalog_Server_DB.quantity,Catalog_Server_DB.price).filter_by(id = bookID).first()
    if book!= NullSession:
        result = json.dumps(book,indent=5)
        return (result)
    else: 
        return jsonify({bookID: "this id does not exist please try another id"})


#==================== 3- update price ==============================================

#updating the book price 
#this also to be used by the admin
@app.route("/update_price/<bookID>",methods=['PUT'])
def update_book_price(bookID):
    getbook = Catalog_Server_DB.query.get(bookID)
    if getbook:
        price = request.form.get('price') #get the price that read in frontend
        getbook.price = price 
        db.session.commit() #commit the update IN DATABASE
        book={}
        book['id']=getbook.id
        book['title']=getbook.title
        book['topic']=getbook.topic
        book['price']=getbook.price
        book['quantity']=getbook.quantity
        result = json.dumps(book,indent=5)
        requests.put("http://"+catlog1+"/update_price_/"+str(bookID),data={'price':price})
        #requests.put("http://"+catlog3+"/update_price_/"+str(bookID),data={'price':price})

        requests.delete("http://"+front+"/invalidate/"+str(bookID))


        return (result)
    else:
        return jsonify({bookID: "this id does not exist please try another id"})

#==================== 4- update quantity ==============================================

#==================== increase quantity ==============================================
@app.route("/increase_quantity/<bookID>",methods=['PUT'])
def increase_book_quantity(bookID):
    getbook = Catalog_Server_DB.query.get(bookID)
    if getbook:
        new_amount = int(request.form.get('new_amount'))
        getbook.quantity = getbook.quantity + new_amount 
        db.session.commit()
        requests.put("http://"+catlog1+"/increase_quantity_/"+str(bookID),data={'new_amount':new_amount})
        #requests.put("http://"+catlog3+"/increase_quantity_/"+str(bookID),data={'new_amount':new_amount})
        requests.delete("http://"+front+"/invalidate/"+str(bookID))
        return jsonify({"msg" : f"increaseing number of book '{getbook.title}' done succesfully. old quantity is {getbook.quantity-new_amount}, and the new quantity is {getbook.quantity}"})

    else:
        return jsonify({bookID: "this id does not exist please try another id"})


#==================== decrease quantity ==============================================
@app.route("/decrease_quantity/<bookID>",methods=['PUT'])
def decrease_book_quantity(bookID):
    getbook = Catalog_Server_DB.query.get(bookID)
    if getbook:
        new_amount = int(request.form.get('new_amount'))
        x= getbook.quantity - new_amount 
        if x < 0:
            return jsonify({"msg":f"no books enough ,the number of remaining books is {getbook.quantity}"})
        else :
            getbook.quantity = x
            db.session.commit()
        requests.put("http://"+catlog1+"/decrease_quantity_/"+str(bookID),data={'new_amount':new_amount})
        #requests.put("http://"+catlog3+"/decrease_quantity_/"+str(bookID),data={'new_amount':new_amount})
        requests.delete("http://"+front+"/invalidate/"+str(bookID))
        
        return jsonify({"msg" : f"decreaseing number of book : '{getbook.title}' done succesfully. old quantity is {getbook.quantity+new_amount}, and the new quantity is {getbook.quantity}"})
    else:  return jsonify({bookID : "this id does not exist"})



#==================== decrease quantity ==============================================
@app.route("/decrease_quantity_/<bookID>",methods=['PUT'])
def decrease_book_quantity_(bookID):
    getbook = Catalog_Server_DB.query.get(bookID)
    if getbook:
        new_amount = int(request.form.get('new_amount'))
        x= getbook.quantity - new_amount 
        if x < 0:
            return jsonify({"msg":f"no books enough ,the number of remaining books is {getbook.quantity}"})
        else :
            getbook.quantity = x
            db.session.commit()
        return jsonify({"msg" : f"decreaseing number of book : '{getbook.title}' done succesfully. old quantity is {getbook.quantity+new_amount}, and the new quantity is {getbook.quantity}"})
    else:  return jsonify({bookID : "this id does not exist"})


@app.route("/increase_quantity_/<bookID>",methods=['PUT'])
def increase_book_quantity_(bookID):
    getbook = Catalog_Server_DB.query.get(bookID)
    if getbook:
        new_amount = int(request.form.get('new_amount'))
        getbook.quantity = getbook.quantity + new_amount 
        db.session.commit()
        return jsonify({"msg" : f"increaseing number of book '{getbook.title}' done succesfully. old quantity is {getbook.quantity-new_amount}, and the new quantity is {getbook.quantity}"})

    else:
        return jsonify({bookID: "this id does not exist please try another id"})


@app.route("/update_price_/<bookID>",methods=['PUT'])
def update_book_price_(bookID):
    getbook = Catalog_Server_DB.query.get(bookID)
    if getbook:
        price = request.form.get('price') #get the price that read in frontend
        getbook.price = price 
        db.session.commit() #commit the update IN DATABASE
        book={}
        book['id']=getbook.id
        book['title']=getbook.title
        book['topic']=getbook.topic
        book['price']=getbook.price
        book['quantity']=getbook.quantity
        result = json.dumps(book,indent=5)

        return (result)
    else:
        return jsonify({bookID: "this id does not exist please try another id"})


#=====================================================
if __name__ == '___main__':
    app.run(debug=True)
