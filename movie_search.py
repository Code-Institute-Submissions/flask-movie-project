from flask import Flask, flash, Blueprint, render_template, request, redirect, url_for, Response, session, abort
import requests
import tmdbsimple as tmdb, requests
from forms import SearchForm, MovieForm
from bson.objectid import ObjectId
from database import mongo
import os
if os.path.exists("env.py"):
    import env

# Blueprint for this file
movie_search = Blueprint("movie_search", __name__, static_folder="static", template_folder="templates")
# Get api key from env.py
tmdb.API_KEY = os.environ.get("TMDB_KEY")
# Default language for imports 
tmdb.language = "en"
# Request session
tmdb.REQUESTS_SESSION = requests.Session()

search = tmdb.Search()

@movie_search.route("/home", methods=["POST", "GET"])
def home():
    # Fetch all information about all movies from the movies database in order to display it in the html
    home_movies = mongo.db.movies.find({}, {'movie_id': 1, 'movie_title': 1, 'movie_overview': 1, 'poster_path': 1, '_id': 0})
    form = SearchForm()
    if form.validate_on_submit():
        # Setting user input to string
        string = request.form["search"]
        # Display what user is searching for
        flash(f"Searching for {string}...")
        # Search for movie with user input from html form
        movies = search.movie(query=string)
        for res in search.results:
            print(res['title']) 
            print(res['id']) 
            print(res['overview']) 
            print(res['poster_path'])
        return render_template('home.html', movies=movies, search=search, home_movies=list(home_movies), form=form)
    return render_template('home.html', search=search, home_movies=list(home_movies), form=form)


@movie_search.route("/review/<movie_id>", methods=["POST", "GET"])
def review(movie_id):
    form = MovieForm()
    # Get currrent user 
    user = mongo.db.users.find_one(
    {"username": session["user"]})["username"].capitalize()
    # Create veriables for title, overview and post path.
    movie = tmdb.Movies(movie_id)
    response = movie.info()
    
    movie_title = movie.title
    movie_id = movie.id
    movie_overview = movie.overview
    poster_path = movie.poster_path
    # Fetch all information about all movies from the movies database in order to display it in the html
    reviews = mongo.db.reviews.find({}, {'movie_id': 1, 'movie_title': 1, 'username': 1, 'review_text': 1, '_id': 1})
    # If the user press create and if the movie does not exist in the database 
    if form.create.data and request.method == 'POST':
        # Information about the movie to send to the database
        movie_info = {
            "movie_id": movie_id,
            "movie_title": movie_title,
            "movie_overview": movie_overview,
            "poster_path": poster_path
        }
        # Insert movie informationin the database
        mongo.db.movies.insert_one(movie_info)
        print(movie_info)
    # Send information from the review form to the database 
    if form.review.data and request.method == 'POST':
        review_info = {
            "movie_id": movie_id,
            "movie_title": movie_title,
            "username": user,
            "review_text": request.form.get("review")
        }
        mongo.db.reviews.insert_one(review_info)
        print(review_info)
    if form.delete.data and request.method == 'POST':
            delete_id = request.form.get("delete")
            mongo.db.reviews.remove( {"_id": ObjectId(delete_id) });
    return render_template('review.html', form=form, reviews=list(reviews), movie_id=movie_id, movie_title=movie_title, movie_overview=movie_overview, poster_path=poster_path, user=user)