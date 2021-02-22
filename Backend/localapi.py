from flask import Flask, render_template, request, redirect, Response
from datetime import datetime
from flask.helpers import send_from_directory
from flask.json import jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exc
import json


app = Flask(__name__)


# Opening my config file

with open("config.json", "r") as file:
    params = json.load(file)['params']

# Setting connection between app and database
db = SQLAlchemy(app)

app.config["SQLALCHEMY_DATABASE_URI"] = params["local_uri"]

# Setting up a secret key so that we can delete and update posts (Flask required)
app.secret_key = params['secret_key']


# Creating a database
class Users(db.Model):
    """

    Here, we are creating a class which will be responsible for 
    building and managing our DataBase. I have created an additional 
    Column i.e Date, to store the latest time in which the meme was posted 
    or updated. For, id I have used a simle INTEGER type data format and I have set it to primary.
    List of COlumns:
    >sno (or ID)
    >name
    >caption
    >link
    >date

    """

    __tablename__ = "XMEMES"
    sno = db.Column(db.INTEGER, primary_key = True)
    name = db.Column(db.String(50), nullable = False)
    caption = db.Column(db.String(120), nullable = False)
    link = db.Column(db.String(5000), nullable = False)
    date = db.Column(db.String(50), nullable = False)

    def __init__(self, name, caption, link, date):
        self.name = name
        self.caption = caption
        self.link = link
        self.date = date

    def ___repr__(self):
        return '<Users %r>' % self.name


# Creating the GET api end point
@app.route('/memes/<string:id>', methods = ["GET", "POST", "PATCH"])
@app.route('/memes', methods = ["GET", "POST", "PATCH"])
def memes(id = ""):


    """

    This is the main endpoint of my api and it allows the following methods
    >GET
    >POST
    >PATCH

    ====================================================================================
    GET

    You can see I have used a slug point '<string:id>' which help me to fetch the 
    xmeme with the corresponding ID or return a 404 response, if a xmeme with the
    asked ID is not in the DataBase
    ====================================================================================



    ====================================================================================
    POST

    For the post request, I am get_json() method inside request sub-module of 
    flask. It is helping in parsing the given data in json or dict format(in python).
    Whenever, I am getting a Post request, I'm linear over all the existing posts
    in the database. If any post is found a mirror version of the given request,
    I am feteching a response of 409. Otherwise, I'm inserting the posted xmeme.
    And, if any other error occurs I'm returning a response with status code 400

    Note: Matching is checked only for name, caption and url 
    ====================================================================================




    ====================================================================================
    PATCH

    Similar to POST method, it is collecting the request data in json format.
    This method is used to update/edit the existing xmemes. It performs a linear
    search to get the xmeme with corresponding id (since id is unique for every xmeme)
    and then it simply update the parameters of the old post with new data, finally it 
    commit all the changes to the database.

    Note: It is not updating name and id
    ====================================================================================


    """



    if (request.method == "GET"):
        posts = Users.query.filter_by().all()
        if(id == ""):
            response = []
            for post in posts:
                response.append({
                    "id" : post.sno,
                    "name" : post.name,
                    "caption":post.caption,
                    "url":post.link,
                    "date":post.date
                    })

            return jsonify(response)

        else:
            response = 0
            for post in posts:
                if (post.sno == int(id)):
                    response = {
                        "id":post.sno,
                        "name":post.name,
                        "caption" : post.caption,
                        "url": post.link,
                        "date":post.date
                    }
            if(response == 0):
                return Response(status=404)
            return jsonify(response)

    if(request.method == "POST"):

        """

            Here the raw request data is in bytes format
            So, we have to decode it as per UTF-8 and then 
            convert into a python dictionary or Json object format

        """
        data_ = request.get_json(force=True) 
        print()
        print(data_)
        print()


        try:   
    
            name = data_["name"]
            caption = data_["caption"]
            link = data_["url"]
            date = datetime.now()

            posts = Users.query.filter_by().all()

            # To check if the post already exist
            for post in posts:
                if (post.name == name and post.caption == caption and post.link == link) :
                    status_code = Response(status=409)
                    return status_code
            



            entry = Users(name = name, caption = caption, link = link, date = date)
            db.session.add(entry)
            db.session.commit()
            status_code = Response(status=200)
            return status_code

        
        except:
            return Response(status = 400)
    
    if (request.method == "PATCH"):

        """

            Here the raw request data is in bytes format
            So, we have to decode it as per UTF-8 and then 
            convert into a python dictionary or Json object format

        """
        data = request.get_json(force=True)        
        
        # id = data["id"]
        # name = data['name']
        caption = data['caption']
        link = data['url']
        date = datetime.now()

        post = Users.query.filter_by(sno=int(id)).first()
        try:   
            post.sno = id
            post.caption = caption
            post.link = link
            post.date = date

            db.session.commit()
            status_code = Response(status=200)
            return status_code

        
        except exc.IntegrityError:
            return Response(status = 400)

@app.route("/deleteMemes", methods = ["PATCH"])
def deleteMemes():
    """

        This route controls deletion of posts.
        First, it collects the request data attribute in json format.
        With the help of id atribute, it filter out the existing post
        and then performs deletion operation. After, successful deletion
        it returns a response with status code 200. Otherwise, it returns
        a 400 response.
        

    """
    
    data = request.get_json(force=True)        
    id = data["id"]
    post = Users.query.filter_by(sno=int(id)).first()

    if(post is not None):
        db.session.delete(post)
        db.session.commit()
        return Response(status=200)
    return Response(status=400)




if __name__ == "__main__":
    app.run(port=8081, debug=True)