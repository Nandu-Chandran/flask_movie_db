from os import name
from pymongo import MongoClient, collection
from flask import Flask, render_template, request, url_for, redirect,jsonify
import pprint
import re
from flask import request
import time
from datetime import datetime, date
from time import mktime as mktime
from werkzeug.utils import secure_filename
import os
from bson import json_util
import json

app = Flask(__name__)
client = MongoClient('localhost', 27017)

common_db=client['common_db']
review_db=client['review_db']
latest_comment_db=client['latest_comment_db']
theatre_col = common_db['theatre_db']
movie_col = common_db['movie_db']
review_col = review_db['review_db']
latest_comment_col=latest_comment_db['latest_comment_db']

def get_recent_comment():
    latest_comment_col= latest_comment_db['latest_comment']
    get_comment=latest_comment_col.find_one({})
    return get_comment


@app.route('/', methods=('GET', 'POST'))
def index():
    all_movie_data = movie_col.find({})
    print(type(all_movie_data))
    latest_comment=get_recent_comment()
    print(latest_comment)
    #return { "movie_data":all_movie_data,"latest_comment_data":latest_comment}
    #json.loads(json_util.dumps(all_movie_data))
    response= jsonify(json.loads(json_util.dumps(all_movie_data)))
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response 
if __name__ == '__main__':
    app.run(debug=True, port=8000, host='0.0.0.0')
