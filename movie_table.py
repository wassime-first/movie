from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, Column, String, INTEGER, FLOAT

import os
from dotenv import load_dotenv
from flask_login import UserMixin, LoginManager

load_dotenv()
URI = os.getenv("URI")

login_manager = LoginManager()

engine = create_engine(URI)
Base = declarative_base()


class User(UserMixin, Base):
    __tablename__ = 'users-movie'
    id = Column(INTEGER, primary_key=True)
    username = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    password = Column(String(1000), nullable=False)
    movies = relationship("Movie", back_populates="user", cascade="all, delete, save-update")
    likes = relationship('Like', backref='user', lazy=True)

    def like_count(self):
        return len(self.likes)


class Like(UserMixin, Base):
    __tablename__ = 'likes'
    id = Column(INTEGER, primary_key=True)
    liked_user_id = Column(INTEGER, nullable=False)
    user_id = Column(INTEGER, ForeignKey('users-movie.id'), nullable=False)


class Movie(UserMixin, Base):
    __tablename__ = 'movies'
    id = Column(INTEGER, primary_key=True)
    title = Column(String(250), nullable=False)
    year = Column(INTEGER, nullable=False)
    description = Column(String(1000), nullable=False)
    rating = Column(FLOAT, nullable=False)
    ranking = Column(INTEGER, nullable=False)
    review = Column(String(1000), nullable=False)
    img_url = Column(String(20000), nullable=False)
    user_id = Column(INTEGER, ForeignKey('users-movie.id'))
    user = relationship("User", back_populates="movies")


Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()


def add_movie(user: int, title: str, year: int, description: str, rating: float, ranking: int, review: str,
              img_url: str):
    movie = Movie(title=title, year=year, description=description, rating=rating, ranking=ranking, review=review,
                  img_url=img_url, user_id=user)
    session.add(movie)
    session.commit()
    print(f"Added movie: {title}")


def delete_movie_by_id(user: int, id: int):
    movie = session.query(Movie).filter_by(user_id=user).filter_by(id=id).first()
    if movie:
        session.delete(movie)
        session.commit()
        print(f"Deleted movie with id: {id}")
    else:
        print(f"No movie found with id: {id}")


def update_movie_ranking(user: int, id: int, ranking: int):
    movie = session.query(Movie).filter_by(user_id=user).filter_by(id=id).first()
    if movie:
        movie.ranking = ranking
        session.commit()
        print(f"Updated ranking for movie with id: {id}")
    else:
        print(f"No movie found with id: {id}")


def update_movie(user: int, id: int, rating: float, review: str):
    movie = session.query(Movie).filter_by(user_id=user).filter_by(id=id).first()
    if movie:
        movie.rating = rating
        movie.review = review
        session.commit()
        print(f"Updated movie with id: {id}")
    else:
        print(f"No movie found with id: {id}")


def all_movies():
    return session.query(Movie).all()


def all_users():
    return session.query(User).all()


def add_user(username, email, password):
    new = User(username=username, email=email, password=password)
    session.add(new)
    session.commit()
    print(f"Added user: {username}")
    return new


def like(liker_id):
    existing_like = User.query.filter(User.likes.liked_user_id == liker_id).first()

    if existing_like:
        # If it exists, remove the like
        session.delete(existing_like)
        session.commit()
    else:
        # If it doesn't exist, create a new like
        new_like = Like(liked_user_id=liker_id)
        session.add(new_like)
        session.commit()

# 'https://www.shortlist.com/media/images/2019/05/the-30-coolest-alternative-movie-posters-ever-2-1556670563-K61a-column-width-inline.jpg'
