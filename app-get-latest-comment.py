from os import name
from pymongo import MongoClient, collection
from flask import Flask, render_template, request, url_for, redirect,jsonify
import pprint
import re
from flask import request
app = Flask(__name__)
from datetime import datetime
from time import mktime as mktime
import time
from datetime import datetime, date


client = MongoClient('localhost', 27017)

review_db=client['review_db']
comment_db=client['latest_comment_db']
latest_comment_col= comment_db['latest_comment']
key_field="datetime_epoc"

def check_if_field_exists():
    all_collection_names=review_db.list_collection_names()
    for collection in all_collection_names:
        data_in_collection = review_db[collection]
        field = data_in_collection.find({'datetime_epoc':{"$exists":True}})
        #cursor = db.data_in_collection.find(field)
        #print(cursor)
        if field:
            print("found")


def update_latest_comment(latest_review):
    reviewer=latest_review['username']
    review=latest_review['comment']
    newvalues = { "$set": { 'comment': review } }
    all_collection_names= comment_db.list_collection_names()
    if 'latest_comment' not in all_collection_names:
        comment_db.latest_comment.insert_one({'name':'latest','comment':review,'username':reviewer})
    else:
        filter = { 'name': 'latest' }
        newvalues = { "$set": { 'comment': review, 'username': reviewer } }
        latest_comment_col.update_one(filter,newvalues,upsert=True)
    
    print(latest_comment_col.find())
    #latest_comment_col.insert_one('latest comment':''

def get_collection_from_db():
    all_collection_names=review_db.list_collection_names()
    comment_dict={}
    for collection in all_collection_names:
        data_in_collection = review_db[collection]
        comments_per_collection = data_in_collection.find().sort([(key_field,1)]).limit(1)
        for i in range(comments_per_collection):
            print(i)
        #print(sorted_data.next())
        
        if len(comment_dict)== 0:
            comment_dict['latest']=comments_per_collection[0]

        recent_comment_in_movie=comments_per_collection[0]
            
        recent_comment_in_comment_list=comment_dict['latest']
        epoch_recent_comment_in_list=recent_comment_in_comment_list[key_field]
        epoch_recent_comment_in_movie=recent_comment_in_movie[key_field]

        if epoch_recent_comment_in_movie >= epoch_recent_comment_in_list : 
            comment_dict['latest']= recent_comment_in_movie 



           #print("No field found with key_field specified")
    print(comment_dict['latest'])
    update_latest_comment(comment_dict['latest'])

def time():
    current_datetime =datetime.today()
    unixtime = mktime(current_datetime.timetuple())
    print("Timestamp of now: ", unixtime)
    
    timestamp = datetime.fromtimestamp(unixtime)
    print("Date =", timestamp)
#time()
#check_if_field_exists()
get_collection_from_db()
