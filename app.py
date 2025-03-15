from flask import Flask, render_template
from models.model import db
import os

app = None

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] =  "your_secret_key"
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz_master.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    try:
        with app.app_context():
            db.create_all()
            print("Database initialized successfully.")
    except Exception as e:
        print(f"Error {e}")
   
    return app




app= create_app     
from application.controllers import *


if __name__=="__main__":
    app.run()


@app.route('/')
def homepage():
    return render_template('register.htm')

if __name__ == '__main__':
    from controllers.controller import *
    app.run(debug=True)