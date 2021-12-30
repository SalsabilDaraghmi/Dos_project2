from flask import Flask, json, jsonify ,render_template
from flask import request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import requests
import os
from datetime import date
from datetime import datetime
import sqlite3
from flask_sqlalchemy.model import Model

#initial app
app = Flask(__name__)


############################### purchase ####################################
# if client send purchase with a specific book_id
#order server send to catalog server
catalog1="172.19.2.60:3000"
catalog2="172.19.2.60:4000"
catalog3="172.19.2.60:5000"
load_balance_catalog=0
@app.route('/purchase/<int:bookID>', methods=['PUT'])
def purchase_book(bookID):
    global load_balance_catalog
    if load_balance_catalog==0:
        load_balance_catalog+=1
        result=requests.put("http://"+catalog1+"/decrease_quantity/"+str(bookID),{'new_amount':1})
    if load_balance_catalog==1:
        load_balance_catalog+=1
        result=requests.put("http://"+catalog2+"/decrease_quantity/"+str(bookID),{'new_amount':1})
    if load_balance_catalog==2:
        load_balance_catalog=0
        result=requests.put("http://"+catalog3+"/decrease_quantity/"+str(bookID),{'new_amount':1})
    x=result.json()
    msg= str(x.get('msg'))
    print(msg,end=' , ')

    if msg == 'None'  or msg.find("enough")!=-1:
        print("hi")
        return(result.content)
    else: 
        global load_balance_catalog
        result2=''
        print("noo")
        if load_balance_catalog==0:
            load_balance_catalog+=1
            result2=requests.put("http://"+catalog1+"/info/"+str(bookID))
        if load_balance_catalog==1:
            load_balance_catalog+=1
            result2=requests.put("http://"+catalog2+"/info/"+str(bookID))
        if load_balance_catalog==2:
            load_balance_catalog=10
            result2=requests.put("http://"+catalog3+"/info/"+str(bookID))
        info=result2.json()
        return {"msg":f"bought book '{info.get('title')}'"}
      


#run
if __name__=="__main__":
    app.run(debug=True)
