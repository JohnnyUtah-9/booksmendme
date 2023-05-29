from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email
import os
import requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users/johnnyutah/PycharmProjects/bookmendmetest/Sqllite.db'
db = SQLAlchemy(app)

app.config['SECRET_KEY'] = os.urandom(24)

# This is your model definition
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=False)
    phone = db.Column(db.String(20), nullable=False)
    favorite_book = db.Column(db.String(100)) # new column for Favorite Book
    # more columns...

with app.app_context():
    db.create_all()

class UserForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone', validators=[DataRequired()])
    favorite_book = StringField('Favorite Book', validators=[DataRequired()]) # new field for Favorite Book
    submit = SubmitField('Submit')

def get_book_genre(book_title):
    book_title = book_title.replace(' ', '+')
    response = requests.get(f'https://www.googleapis.com/books/v1/volumes?q=intitle:{book_title}')
    data = response.json()
    genres = data['items'][0]['volumeInfo'].get('categories', None)
    return genres

def recommend_books(genre):
    genre = genre.replace(' ', '+')
    response = requests.get(f'https://www.googleapis.com/books/v1/volumes?q=subject:{genre}&maxResults=10')
    data = response.json()
    book_titles = [item['volumeInfo']['title'] for item in data['items']]
    return book_titles

def create_amazon_link(book_title):
    search_terms = book_title.replace(' ', '+')
    url = f'https://www.amazon.com/s?k={search_terms}'
    return url

@app.route('/', methods=['GET', 'POST'])
def index():
    form = UserForm()
    recommendations =[]
    if form.validate_on_submit():
        user = User(name=form.name.data, email=form.email.data, phone=form.phone.data, favorite_book=form.favorite_book.data)
        db.session.add(user)
        db.session.commit()
        genres = get_book_genre(form.favorite_book.data)
        if genres:
            for genre in genres:
                genre_recommendations = recommend_books(genre)
                for book in genre_recommendations:
                    recommendations.append({
                        "title": book,
                        "amazon_link": create_amazon_link(book)
                    })
    return render_template('index.html', form=form, recommendations=recommendations)

if __name__ == '__main__':
    app.run(debug=True)
