from flask import Flask, request, jsonify, Response
import pymongo

app = Flask(__name__)
app.config['MONGO_URI'] = 'mongo://localhost:27017/'

mongo = pymongo(app)


@app.route('/', method=['GET'])
def retrieve_all():
    holder = list()
    current_collection = mongo.db.favInfo
    for i in current_collection.find():
        holder.append({'name': i['name']})
    return jsonify(holder)


if __name__ == '__main__':
    app.run(debug=True)
