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
@app.route('/purchase/<int:bookID>', methods=['PUT'])
def purchase_book(bookID):
    result=requests.put("http://192.168.1.60:5000/decrease_quantity/"+str(bookID),{'new_amount':1})
    x=result.json()
    msg= str(x.get('msg'))
    print(msg,end=' , ')

    if msg == 'None'  or msg.find("enough")!=-1:
        print("hi")
        return(result.content)
    else: 
        print("noo")
        result2=requests.get("http://192.168.1.60:5000/info/"+str(bookID))
        info=result2.json()
        return {"msg":f"bought book '{info.get('title')}'"}
      


#run
if __name__=="__main__":
    app.run(debug=True)