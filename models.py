from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = True
db = SQLAlchemy(app)

class Admin(db.Model):
    __tablename__ = 'admin'

    username = db.Column(db.String(), primary_key =True, nullable=False, unique=True)
    password = db.Column(db.String(), nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.password = password

class Book(db.Model):
    __tablename__ = 'book'

    bookname = db.Column(db.String(),primary_key=True ,nullable=False)
    bookissuer = db.Column(db.String(), nullable=False)
    
    def __init__(self,bookname, bookissuer):
        self.bookname = bookname
        self.bookissuer = bookissuer



if __name__ == "__main__":
    db.create_all()
    