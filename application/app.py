from flask import Flask, render_template, redirect, url_for, request, flash, Response, session, send_from_directory
# from main import app
# from applications.model import *
from datetime import datetime
from sqlalchemy import or_, and_, func
import io
import matplotlib.pyplot as plt
import matplotlib
import os
matplotlib.use('Agg')
from application.database import db

app = None

def create_app():
    app = Flask(__name__)
    app.debug = True
    app.config["SQLALCHEMY_DATABASE_URI"]= "sqlite:///ecard.sqlite3"
    db.init_app(app)
    app.app_context().push()#else runtime error
    return app


# app=create_app()
# from application.controller import *

app= create_app
from application.controllers import *


if __name__=="__main__":
    app.run()
