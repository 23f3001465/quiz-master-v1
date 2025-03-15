from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)  
    full_name = db.Column(db.String(30), nullable=False)
    qualification = db.Column(db.String(20), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    email = db.Column(db.String(30), unique=True, nullable=False)
    phone = db.Column(db.String(10), nullable=False)
    address = db.Column(db.String(25), nullable=False)
    status = db.Column(db.String(10), default='active')
    is_admin = db.Column(db.Boolean, default=False)
    scores = db.relationship('Scores', backref='user', lazy=True)

class Subject(db.Model):
    __tablename__ = 'subject'
    subject_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    description = db.Column(db.String(40))
    chapters = db.relationship('Chapter', backref='subject', lazy=True, cascade="all, delete-orphan")

class Chapter(db.Model):
    __tablename__ = 'chapter'
    chapter_id = db.Column(db.Integer, primary_key=True)
    chapter_name = db.Column(db.String(20), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.subject_id'), nullable=False)
    description = db.Column(db.String(40))
    quizzes = db.relationship('Quiz', backref='chapter', lazy=True, cascade="all, delete-orphan")

class Quiz(db.Model):
    __tablename__ = 'quiz'
    quiz_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.chapter_id'), nullable=False)
    date_of_quiz = db.Column(db.Date, nullable=False)
    time_duration = db.Column(db.Time, nullable=False)
    remarks = db.Column(db.String(40))
    questions = db.relationship('Question', backref='quiz', lazy=True, cascade="all, delete-orphan")
    scores = db.relationship('Scores', backref='quiz_ref', lazy=True)

class Question(db.Model):
    __tablename__ = 'question'
    question_id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(100), nullable=False)
    option1 = db.Column(db.String(50), nullable=False)
    option2 = db.Column(db.String(50), nullable=False)
    option3 = db.Column(db.String(50), nullable=False)
    option4 = db.Column(db.String(50), nullable=False)
    correct_option = db.Column(db.Integer, nullable=False)  
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.quiz_id'), nullable=False)
    time_duration = db.Column(db.Time, nullable=True)
    remarks = db.Column(db.String(40))

class Scores(db.Model):
    __tablename__ = 'scores'
    score_id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.quiz_id'), nullable=False)
    total_scored = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    timestamp_date_of_attempt = db.Column(db.Date, nullable=False)
    time_taken = db.Column(db.Time, nullable=False)
    time_stamp_of_attempt = db.Column(db.Time, nullable=False)
    remarks = db.Column(db.String(40))
