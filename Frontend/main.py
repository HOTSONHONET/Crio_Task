"""


Here, I am importing all the necessary modules.
>I'm importing flask because I'm using flask to build the app
>I'm using requests to make API calls
>I'm using json to convert client data into Json format and 
also to read my config file
>I'm using math package to perform pagination 
>I'm importing exc from sqlalchemy to collect the error that happens 
with the database



"""




from flask import Flask, render_template, request, redirect, flash
from sqlalchemy import exc
import json
import math
import requests


app = Flask(__name__)


# Opening my config file

"""

    Here, I'm reading my config file
    It contains, all the neccessary paths
    and values which I will be needing in
    developing the app

"""

with open("config.json", "r") as file:
    params = json.load(file)['params']


app.secret_key = params['secret_key']

# Routing the flask app to render the homepage
"""

Here, I am creating a route to for my homepage.
This route is responsible for fetching all the memes 
from the database via the API and displaying them
by rendering index.html


Idea for Pagination:
>First page:
    >> prevPage : #
    >> currentPage : 1
    >> nextPage : currentPage + 1
>Intermediate page:
    >> prevPage : currentPage - 1 
    >> currentPage : some calculated value
    >> nextPage : currentPage + 1
>Last page:
    >> prevPage : currentPage - 1
    >> currentPage : lastpage index
    >> nextPage : #

While rendering index.html, I'm using params 
which stores config elements that enables the 
page to get its elements like css, images, js files etc

"""
@app.route("/")
def index():
    m_getUrl = "http://localhost:8081/memes"
    get_posts = requests.get(m_getUrl)
    posts = get_posts.json()
    # To get the recent post first we will reverse the list of posts
    posts = posts[::-1]
    total_posts = len(posts)
    last = math.ceil(len(posts)/params["postsPerPage"])
    page = request.args.get('page')
    
    if(not str(page).isnumeric()):
        page = 1
    page = int(page)
    posts = posts[(page-1)*int(params["postsPerPage"]):(page-1)*params["postsPerPage"] + params["postsPerPage"]]

    if(len(posts) == 0):
        return redirect("/")

    if (page == 1):
        prev_ = "#"
        if(total_posts//int(params["postsPerPage"]) > 1):
            print()
            print(len(posts))
            print()
            next_ = f"/?page={page+1}"
        else:
            next_ = "#"
        msg = f"You are on 1st page"
    elif (page == last):
        prev_ = f"/?page={page-1}"
        next_ = "#"
        msg = "This is the last page"
    else:
        prev_ = f"/?page={page-1}"
        next_ = f"/?page={page+1}"
        msg = f"Current Page# {page}"
    
    flash(msg, "warning")
    return render_template('index.html', params = params, posts = posts, prev_ = prev_, next_ = next_)




# Routing the flask app for catching POST requests
# Saving the POSTED meme along with name and caption in the database
"""

Here, I am making a post request to the API, 
by sending the client given data. But, before that I'm 
converting the data into json format so that the API can
read the data and make the neccessary action.

If the returned response from the API is 200 then and 
only then it is redirecting to the HomePage.

And if someone tries to create a duplicate MEME,
then it will redirect them to a error page


"""

@app.route("/post-meme", methods = ["GET", "POST"])
def post_meme():
    if(request.method == "POST"):
        name = request.form.get('name')
        caption = request.form.get('caption')
        url = request.form.get('url')

        try:     
            data = {
                "name":name,
                "caption":caption,
                "url":url,
                }   
            data = json.dumps(data)
            new_entry = requests.post(url="http://localhost:8081/memes", data = data)
            print()
            print(new_entry.status_code)
            print()
            if(new_entry.status_code == 200):
                return redirect("/")
            if (new_entry.status_code == 409):
                return redirect("/error")
            else:
                return redirect("/error")
        
        except exc.IntegrityError:
            return redirect("/")

    return redirect("/")

# To edit posted memes
"""

This endpoint is responsible for editing
the existing meme. It first make a get request
for collecting the attributes for the selected meme.
Then it makes a patch request to the api for updating the caption 
and url. But, before that the form data is converted to json format
and then it is send to the API.

If the API sends a Response status of 200 then and only then it 
redirects to the page again, Otherwise it redirects to /error 
route

I have ensured that, the user shouldn't be able to
edit the name, date and id attributes for the meme.

"""

@app.route('/editMeme/<string:sno>', methods = ["GET", "POST"])
def editMemes(sno):
    print(sno)
    print()
    m_getUrl = f"http://localhost:8081/memes/{sno}"
    get_posts = requests.get(m_getUrl)
    post = get_posts.json()
    
    if (request.method == "POST") : 
        img_sno = post["id"]
        name = post['name']
        caption = request.form.get('caption')
        url = request.form.get('url')
        

        if (len(caption) == 0):
            caption = post.caption
        if(len(url) == 0):
            url=  post.url

        try:     
            data = {
                "id":sno,
                "name":name,
                "caption":caption,
                "url":url
                }   
            data = json.dumps(data)
            edit_entry = requests.patch(url=f"http://localhost:8081/memes/{sno}", data = data)
            
            if(edit_entry.status_code == 200):
                return redirect(f"/editMeme/{img_sno}")
            else:
                return redirect("/error")

            
        except exc.IntegrityError:            
            return redirect(f"/editMeme/{img_sno}")



    return render_template('editMeme.html', params = params, post = post)


# To delete posted memes
"""

This route is responsible for deleting the MEMES
from the database. It simply preforms a get request
to collect the attributes of the MEME and then it 
sends a patch request to thet API for deleting the meme.

"""

@app.route("/deleteMeme/<string:sno>", methods = ["GET", "POST"])
def deleteMeme(sno):
    m_getUrl = f"http://localhost:8081/memes/{sno}"
    get_posts = requests.get(m_getUrl)
    post = get_posts.json()
    
    
    try:     
        data = json.dumps(post)
        edit_entry = requests.patch(url="http://localhost:8081/deleteMemes", data = data)
        print()
        print(edit_entry.status_code)
        print()
        if(edit_entry.status_code == 200):
            return redirect("/")
        else:
            return redirect("/error")

        
    except exc.IntegrityError:            
        return redirect("/")

"""

This route handles all the error
and simply renders a HTML. 

"""
@app.errorhandler(500)
@app.errorhandler(404)
@app.errorhandler(409)
@app.route("/error")
def error(e):
    return render_template("error.html", params = params), 404


    
if __name__ == "__main__":
    app.run(port=8082, debug=True)