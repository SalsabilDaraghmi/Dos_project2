from datetime import time
import re
from flask import request
from flask.sessions import NullSession
from flask import Flask, json, jsonify ,render_template
from flask import request
import requests
from flask_sqlalchemy import SQLAlchemy

#initial app
app = Flask(__name__)

#For Database "BooksInfo_DB" we filled it by terminal 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///CacheBooksInfo_DB.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

MAX_SIZE=1000
count_size=0


#calss for creating Database table
class Cache_Server_DB(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(500))
    quantity = db.Column(db.Integer)
    price = db.Column(db.Float)
    topic = db.Column(db.String(500))
    time = db.Column(db.Integer)
    req =db.Column(db.Integer)
     
    def __init__(self,id,title,quantity,price,topic,time,req):
        self.id=id
        self.title=title
        self.quantity=quantity
        self.price=price
        self.topic=topic
        self.time=time
        self.req=req



#============================= 1- Add new book to the cache ====================================
@app.route('/addBook/', methods=['POST'])
def add_book():
    print("hhhhhhhhhhhhhhhhhhh")
    print(request.form.get('id'))
    book = Cache_Server_DB.query.get(request.form.get('id'))
    if book:
        print("============== exisit book==================")

        book.req = book.req + 1
        books= Cache_Server_DB.query.all()
        for b in books:
            b.time = b.time + 1
        db.session.commit()
        return jsonify({request.form.get('title'):" is in cache " })
    else:
        print("============== adding book==================")
        global count_size
        if count_size>1000:
            req_Priority={}
            time_Priority={}
            books = Cache_Server_DB.query.with_entities(Cache_Server_DB.id,Cache_Server_DB.req,Cache_Server_DB.time).all()
            for b in books:
                req_Priority[b[0]]=b[1]
                time_Priority[b[0]]=b[2]
                
            
            mid = min(req_Priority, key=req_Priority.get)
            for key in time_Priority:
                if req_Priority[key] == req_Priority[mid]:
                    if time_Priority[key] > time_Priority[mid] :
                        mid=key

            
            db.query.filter_by(id=mid).delete()
            db.session.commit()
            count_size -= 1 

        newBook=Cache_Server_DB(request.form.get('id'),request.form.get('title'),request.form.get('quantity'),request.form.get('price'),request.form.get('topic'),1,1)
        db.session.add(newBook)
        db.session.commit()
        count_size += 1
        return jsonify({request.form.get('title'):" Added to cache successfully" })

# books = dbSchema(many=True)
# ============================ get book from cache ==================================
@app.route("/info/<bookID>", methods=['GET'])
def get_info_forID(bookID):
    book = Cache_Server_DB.query.with_entities(Cache_Server_DB.title,Cache_Server_DB.quantity,Cache_Server_DB.price,Cache_Server_DB.topic,Cache_Server_DB.req,Cache_Server_DB.time).filter_by(id = bookID).first()
    if book :
        book2={'title':book[0],'quantity':book[1],'price':book[2],'topic':book[3]}
        print("================== exisit============================")
        result = json.dumps(book2,indent=4)
        books= Cache_Server_DB.query.all()
        for b in books:
            if b.id== bookID:
                b.id += 1 
            b.time = b.time + 1
        db.session.commit()
        return (result)
    else: 
        print("================== not exisit else============================")
        return jsonify({'msg':" id dose not exisit" })

# ============================= Delete book from cache =================================
@app.route("/invalidate/<int:bookID>", methods=['DELETE'])
def invalidate_Book(bookID):
    global order_counter
    book = Cache_Server_DB.query.get(bookID)
    if book:
        db.session.delete(book)
        db.session.commit()
        return jsonify({bookID :"Deleteed successfully"})
    else:
        return jsonify({'msg':"this id does not exist"})
  

# ======================== search by topic =================================================
@app.route("/search/<topic>", methods=['GET'])
def search_by_topic(topic):
    book = Cache_Server_DB.query.with_entities(Cache_Server_DB.id,Cache_Server_DB.title).filter_by(topic=topic.replace("%20"," ")).all()
    books={}
    for b in book:
        print(b)
        books[b[0]]={'id':b[0],'title':b[1]}
    
    res=json.dumps(books)
    print(res)
    return (res)


if __name__=="__main__":
    app.run(debug=True)

