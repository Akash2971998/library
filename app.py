
from flask import Flask,request,jsonify,make_response
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import models, jwt
from flask_restful import marshal_with, fields
from functools import wraps

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = True

app.config['SECRET_KEY'] = '12345678'
db = SQLAlchemy(app)

showUser = {
    'username': fields.String
}

showBook = {
    'id': fields.Integer,
    'bookname': fields.String,
    'bookissuer': fields.String
}


@marshal_with(showUser)
def showResponse(data):
    return data

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers.get('x-access-token')
        
        if not token:
            return jsonify({'message': 'token is missing'})
        
        try:
            # decoding the payload to fetch the stored details
            data = jwt.decode(token, app.config['SECRET_KEY'],algorithms=["HS256"])
            current_user = models.Admin.query.filter_by(username=data['username']).first()


        except Exception as e:
            return jsonify({
                'message' : 'e'
            }), 401
        # returns the current logged in users contex to the routes
        return  f(current_user, *args, **kwargs)
  
    return decorated



@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data['username']
    password = data['password']

    users = models.Admin.query.all()

    for i in users:
        if username == i.username:
            return jsonify({"message" : "username already exists"})

    user = models.Admin(username=username, password=password) 
    db.session.add(user)
    db.session.commit()

    return 'Signup Success!'

@app.route('/getalluser', methods=['GET'])
def getalluser():
    user = models.Admin.query.all()
    
    output=[]

    for i in user:
        output.append({'username': i.username})
    
    return jsonify({'user': output})

@app.route('/getuser', methods=['GET'])
def getuser():
    data = request.get_json()
    username = data['username']
    password = data['password']

    if not data or not username or not password:
        return jsonify({'error': 'Incorrect Username/Password'})

    user = models.Admin.query.filter_by(username=username).first()

    if not user:
        return jsonify({'error': 'could not verify'})
    
    if user.password == password:
        token = jwt.encode({
            "username": user.username
        },key=app.config['SECRET_KEY'])

        resp = make_response()
        resp.headers['x-auth-token'] = token
        return token 

    return make_response({'error': 'could not verify'})

@app.route('/getuserlogin', methods=['GET'])
@token_required
def get_one_user(current_user):

    resp = make_response(showResponse(current_user), 200)

    return resp

@app.route('/getallbooks', methods=['GET'])
def get_all_books():

    data = models.Book.query.all()

    if not data:
        return jsonify({'error': 'no books found'})
    
    output =[]
    for book in data:
        output.append({
            'bookname': book.bookname,  
            'bookissuer': book.bookissuer
        })

    return jsonify({'book': output})
    
@app.route('/getbook', methods=['POST'])
def enterbook():
    data = request.get_json()
    bookname = data.get('bookname')
    bookissuer = data.get('bookissuer')

    book = models.Book(bookname=bookname, bookissuer=bookissuer)
    db.session.add(book)
    db.session.commit()

    return "success"

@app.route('/getbook', methods=['PUT'])
def update_books():
    data = request.get_json()
    bookname = data['bookname']
    bookissuer = data['bookissuer']

    book = models.Book.query.filter_by(bookname=bookname).first()
    if not book:
        return jsonify({'error': 'no books found'})
    
    book.bookissuer = bookissuer    
    db.session.commit()

    return "successfull update"

@app.route('/getbook', methods=['DELETE'])
def delete_books():
    data = request.get_json()
    bookname = data['bookname']

    book = models.Book.query.filter_by(bookname=bookname).first()

    if not book:
        return jsonify({'error': 'no books found'})
    
    db.session.delete(book)
    db.session.commit()

    return "success full delete",200
    

if __name__ == "__main__":
    app.run(debug=True)

