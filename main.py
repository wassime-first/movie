from flask import Flask, render_template, request, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, Column, String, INTEGER, FLOAT, desc
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField, PasswordField
from wtforms.validators import DataRequired, Email
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
import requests
import movie_table
import api
from dotenv import load_dotenv
import os

load_dotenv()
SECRET_KEY = os.getenv('SECRET_KEY')
IMG = os.getenv('IMG')

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
Bootstrap(app)


class LoginForm(FlaskForm):
    email = StringField("email", validators=[DataRequired(), Email(granular_message=True)])
    password = PasswordField("password", validators=[DataRequired()])
    submit = SubmitField("sign in")


class RegisterForm(FlaskForm):
    username = StringField("username", validators=[DataRequired()])
    email = StringField("email", validators=[DataRequired(), Email(granular_message=True)])
    password = PasswordField("password", validators=[DataRequired()])
    submit = SubmitField("sign up")


class AddForm(FlaskForm):
    movie = StringField("movie", validators=[(DataRequired())])
    submit = SubmitField("ADD MOVIE")


class UpdateForm(FlaskForm):
    rating = FloatField('rating', validators=[DataRequired()])
    review = StringField("review", validators=[DataRequired()])
    submit = SubmitField("DONE")


Movie = movie_table.Movie
User = movie_table.User
Like = movie_table.Like
Base = movie_table.Base
engine = movie_table.engine
Session = sessionmaker(bind=engine)
session = Session()

login_manager = movie_table.login_manager
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return session.query(User).get(user_id)


@app.route("/")
def home():
    all_users = movie_table.all_users()
    return render_template("explore.html", users=all_users, logged_in=current_user.is_authenticated)


@app.route("/explore/<int:id>")
def explore(id):
    user = movie_table.find_user_by_id(id)
    return render_template("view.html", user=user, logged_in=current_user.is_authenticated)


@app.route("/mymovies", methods=["POST", "GET"])
@login_required
def my_movies():
    movies = session.query(Movie).filter_by(user=current_user).order_by(Movie.rating).all()
    movies.reverse()
    n = 1
    for movie in movies:
        movie_table.update_movie_ranking(current_user.id, movie.id, n)
        n += 1

    return render_template("index.html", movies=movies, logged_in=current_user.is_authenticated)


@app.route("/register", methods=["POST", "GET"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = session.query(User).filter_by(email=form.email.data).first()

        if user:
            flash("user already exists")
            return redirect(url_for("login"))
        else:
            username = form.username.data
            email = form.email.data
            password = form.password.data
            new_user = User(username=username, email=email, password=generate_password_hash(password, salt_length=8))
            session.add(new_user)
            session.commit()
            login_user(new_user)
            return redirect(url_for("home"))
    return render_template("register.html", form=form, logged_in=current_user.is_authenticated)


@app.route("/login", methods=["POST", "GET"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = session.query(User).filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("my_movies"))
        else:
            flash("invalid email or password")
            return redirect(url_for("login"))
    return render_template("login.html", form=form, logged_in=current_user.is_authenticated)


@app.route("/edit", methods=["POST", "GET"])
@login_required
def edit():
    form = UpdateForm()
    id = request.args.get('id')
    movie = session.query(Movie).filter_by(id=id).first()

    if form.validate_on_submit():
        if request.args.get("ids"):
            movie_id = request.args.get("ids")
            data = api.movie_data(movie_id)
            title = data[0]
            release_date = data[1]
            release_date = release_date.split("-")
            if release_date[0] == "" or release_date == None:
                release_date = 2000
            else:
                release_date = int(release_date[0])
            if data[2] == "" or data[2] == None:
                overview = "No overview available"
            else:
                overview = data[2]
            img_url = data[3]
            if img_url == "" or img_url == None:
                img_url = IMG
            movie_table.add_movie(user=current_user.id, year=release_date, description=overview, title=title,
                                  rating=form.rating.data,
                                  review=form.review.data, ranking=10, img_url=img_url)
            return redirect(url_for("my_movies"))
        else:
            movie_table.update_movie(current_user.id, id, form.rating.data, form.review.data)
            return redirect(url_for("my_movies"))

    return render_template("edit.html", form=form, movie=movie, id=id, logged_in=current_user.is_authenticated)


@app.route("/delete", methods=["POST", "GET"])
@login_required
def delete():
    id = request.args.get('id')
    movie_table.delete_movie_by_id(current_user.id, id)
    return redirect(url_for("my_movies"))


@app.route("/select", methods=["POST", "GET"])
@login_required
def select():
    if request.args.get("id"):
        movie_id = request.args.get("id")
        data = api.movie_data(movie_id)
        title = data[0]
        release_date = data[1]
        release_date = release_date.split("-")
        release_date = int(release_date[0])
        print(release_date)
        overview = data[2]
        img_url = data[3]
        if current_user.movies < 10:
            movie_table.add_movie(user=current_user.id, year=release_date, description=overview, title=title,
                                  img_url=img_url, rating=0, review="")
        return redirect(url_for("home"))
    return render_template("select.html", logged_in=current_user.is_authenticated)


@app.route("/add", methods=["POST", "GET"])
@login_required
def add():
    form = AddForm()
    if form.validate_on_submit():
        movie_title = form.movie.data
        titles = api.search_movies(movie_title)
        return render_template("select.html", titles=titles)

    return render_template("add.html", form=form, logged_in=current_user.is_authenticated)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route("/like/<int:id>", methods=["POST", "GET"])
@login_required
def like(id):
    if request.method == "POST":
        user_id = current_user.id
        user_beain_liked = session.query(User).filter_by(id=id).first()
        all_likes = session.query(Like).filter_by(user_id=user_id).all()
        l = False
        likee = None
        for like in all_likes:
            if like.liked_user_id == user_beain_liked.id:
                l = True
                likee = like
                break
        if not l:
            like = Like(user_id=id, liked_user_id=user_id)
            session.add(like)
            session.commit()
        else:
            session.delete(likee)
            session.commit()

        return redirect(url_for("home"))
    else:
        return redirect(url_for("home"))


if __name__ == '__main__':
    Base.metadata.create_all(engine)
    app.run()
