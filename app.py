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

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/movie_covr/' 
app.config['CAROUSAL_FOLDER'] = 'static/carousal/' 

client = MongoClient('localhost', 27017)

common_db=client['common_db']
review_db=client['review_db']
latest_comment_db=client['latest_comment_db']


theatre_col = common_db['theatre_db']
movie_col = common_db['movie_db']
review_col = review_db['review_db']
latest_comment_col=latest_comment_db['latest_comment_db']

def encode_database_name(dbname):
    if(len(dbname.split())>1):
        encodedName= dbname.replace(' ','_')
        return encodedName
    else:
        return dbname

def decode_database_name(dbname):
    decodedName= dbname.replace('_',' ')
    return decodedName

def get_recent_comment():
    latest_comment_col= latest_comment_db['latest_comment']
    get_comment=latest_comment_col.find_one({})
    return get_comment


def input_test_data(dbname):
    testdb=client[dbname]
    testcol=testdb['<EMPTY>']
    document = {"user_id": 0, "user": "test"}
    testcol.insert_one(document)

def create_movie_db():
    dbnames = client.list_database_names()
    print(dbnames)
    for theatre_name in theatre_col.find({},{"name"}):
        only_theatre_name=(theatre_name['name'])
        if only_theatre_name not in dbnames:
            # encoding db name without spaces
           theatre_name= encode_database_name(only_theatre_name)
           input_test_data(theatre_name) 


@app.route('/', methods=('GET', 'POST'))
def index():
    directory= app.config['CAROUSAL_FOLDER'] 
    carousal_images=[ os.path.join(directory, file) for file in os.listdir(directory)]
    print(carousal_images)
    all_movie_data = movie_col.find()
    print(type(all_movie_data))
    latest_comment=get_recent_comment()
    print(latest_comment)
    return render_template('index.html', full_data=all_movie_data,carousal_data=carousal_images,latest_comment_data=latest_comment)


@app.route('/theatre_update', methods=('GET', 'POST'))
def theatre_update():

    if request.method == 'POST':
        movie_name = request.form['name']
        movie_year= request.form['year']
        movie_star= request.form['cast']
        movie_creator= request.form['creator']

        movie_cover= request.files['file']
        print(movie_cover)
        file = movie_cover
        basedir = os.path.abspath(os.path.dirname(__file__))
        print("basedir",basedir)
        movie_cover_path=''
        if file :
            filename = secure_filename(file.filename)
            file.save(os.path.join(basedir, app.config['UPLOAD_FOLDER'], filename))
            movie_cover_path=(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        movie_col.insert_one({'name': movie_name, 'year': movie_year, 'cast': movie_star, 'creator': movie_creator, 'cover':movie_cover_path })

    return render_template('theatre_update.html')



@app.route('/theatre',methods=('GET', 'POST'))
def theatre():
    if request.method == 'POST':
        theatre_name = request.form['name']
        theatre_location= request.form['location']
        theatre_col.insert_one({'name': theatre_name, 'location': theatre_location})
    all_theatre_data=theatre_col.find() 
    create_movie_db()
    return render_template('theatre_home.html',theatre_data=all_theatre_data)

def create_movie_collection(theatre_name,movie_search_key):
    
    encoded_theatre_name=encode_database_name(theatre_name)
    theatre_name=encoded_theatre_name

    selected_db = client[theatre_name]
    all_collection_names = selected_db.list_collection_names()
    print("create_movie_collection fun---->",all_collection_names)
    print(movie_search_key) 
    if movie_search_key not in all_collection_names:
        tmp_db=client[theatre_name]
        tmp_col=tmp_db[(movie_search_key)]
        if movie_search_key not in tmp_db.list_collection_names():
            get_movie_db= movie_col.find_one({},{'name': movie_search_key})
            tmp_col.insert_one(get_movie_db)
            #deleting the <EMPTY> null values previously inserted
            try:
                tmp_db.drop_collection('<EMPTY>')
            except:
                pass
        
@app.route('/schedule',methods=('GET', 'POST'))
def schedule_movie():
    if request.method == 'POST':
        theatre_name= request.form['select2']
        movie_name = request.form['select1']
        print("from html",theatre_name,movie_name)
        # creating collection with name
        create_movie_collection(theatre_name,movie_name)
    all_movie_data=list(movie_col.find())
    all_theatre_data=list(theatre_col.find())
    data_dict={}
    print("To html",all_movie_data) 
    print("To html",all_theatre_data) 
    for theatre_name in theatre_col.find({},{'name'}):
        encodedName=encode_database_name(theatre_name['name'])
        #print("ENCO-->",encodedName)
        tmp_db=client[encodedName]
        data_dict.update({theatre_name['name']:tmp_db.list_collection_names()})
    #print("To schedule--->",data_dict)
    return render_template('theatre_scheduler.html',movieList=all_movie_data, theatreList= all_theatre_data, dataDict=data_dict)


def create_collection(db_name,movie_name,movie_review,username,movie_rating,theatre_choice,theatre_rating):
    selected_db = client[db_name]
    all_collection_names = selected_db.list_collection_names()

    current_datetime =datetime.today()
    datetime_epoch = mktime(current_datetime.timetuple())
    

    data={'comment':movie_review, 'username':username,'movie_rating':movie_rating,'theatre_choice':theatre_choice,'theatre_rating':theatre_rating,'datetime_epoc':datetime_epoch}    
    tmp_db=client[db_name]

    tmp_col_name= "".join(str(theatre_choice)+" "+str(movie_name))
    tmp_col=tmp_db[tmp_col_name]

    if movie_name not in all_collection_names:
        if movie_name not in tmp_db.list_collection_names():
            tmp_col.insert_one(data)
    else:
        tmp_col.insert_one(data)

def post_review(movie_name,review,username,movie_rating,theatre_choice,theatre_rating):
    db_name='review_db'
    create_collection(db_name,movie_name,review,username,movie_rating,theatre_choice,theatre_rating)
    
def get_review(movie_name):
    tmp_db=review_db
    col_list= tmp_db.list_collection_names()
    all_review=[]
    for each_col in col_list:
        if each_col.find(movie_name)!= -1:
            tmp_col=tmp_db[each_col]
            all_review.append(list(tmp_col.find()))
    return all_review


@app.route('/rating', methods=['GET','POST'])
def rating():
    all_names=review_db.list_collection_names() 
    clicked=None
    if request.method == "POST":
        clicked=request.form['data']
        clicked1=request.form['data1']
    return render_template('rating.html', collection_names= all_names)


@app.route('/process')
def process():
	#email = request.form['email']
	#name = request.form['name']
	#if name and email:
	#	newName = name[::-1]
	#	return jsonify({'name' : newName})
    return render_template('rating.html')


@app.route('/movies/<movie_name>',methods=('GET', 'POST'))
def movie_page(movie_name):
    movie_detail= movie_col.find_one({'name':movie_name})
    if request.method == 'POST':
        posted_review = request.form['movie_review']
        posted_user = request.form['username']
        posted_movie_rating = request.form['movie_rating']
        posted_theatre_selection= request.form['theatre_selection']
        posted_theatre_rating = request.form['theatre_rating']


        post_review(movie_name,posted_review,posted_user,posted_movie_rating,posted_theatre_selection,posted_theatre_rating)
        #create_collection(db_name,movie_name,posted_review,posted_user)

    all_review = get_review(movie_name)
    all_theatre_name= theatre_col.find({},{'name'})
    return render_template('movie_page.html',movieDetail=movie_detail, allReview=all_review,allTheatrename=all_theatre_name)


@app.route('/upload')
def upload_file():
   return render_template('upload.html')
	
@app.route('/uploader', methods = ['GET', 'POST'])
def uploader_file():
   if request.method == 'POST':
      f = request.files['file']
      f.save(secure_filename(f.filename))
      return 'file uploaded successfully'




if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')


