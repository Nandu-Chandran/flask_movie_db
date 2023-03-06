from itertools import count
from os import name
import re

from pymongo import MongoClient, common
from flask import Flask, render_template, request, url_for, redirect
import pprint
app = Flask(__name__)

client = MongoClient('localhost', 27017)

review_db=client['review_db']
common_db=client['common_db']

movie_col = common_db['movie_db']

def calculate_rating(data_list,data_len):
    #print("data len",data_len)
    rating_tot=0
    count=0
    for data in data_list:
        rating=int(data['movie_rating'])
        #print(rating)
        rating_tot+=rating
        count=count+1
        if (count==data_len):
            avg_rating= rating_tot/count
            #print(avg_rating) 
            return avg_rating

def update_rating(collection_name,avg_rating):
    print(collection_name,avg_rating)
    
    #data= movie_col.find({},{"name":collection_name})
    movie_col.find_one_and_update({'name':collection_name},{ '$set': { "movie_rating" : avg_rating} })
    #print(list(movie_col.find({},{"movie_rating"} )))

def read_db():
    selected_db = review_db
    all_collection_names = selected_db.list_collection_names()
    
    for collection_name in all_collection_names:
        tmp_col=selected_db[collection_name]
        comment = [data for data in tmp_col.find(({'movie_rating':{"$ne":None}}))]
        data_len=(len(comment))
        avg_rating=calculate_rating(comment,data_len)
        print(comment)
        update_rating(collection_name,avg_rating)

read_db()
