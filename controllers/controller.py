from flask import  render_template, request, redirect, url_for, flash, session
from datetime import datetime, date, time
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from flask import render_template, url_for, flash, redirect, request, jsonify, session
from datetime import datetime, date, time
import json
from sqlalchemy import extract, func
from app import app
from models.model import *

@app.route('/')
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        qualification = request.form.get('qualification')
        dob_str = request.form.get('dob')
        email = request.form.get('email')
        phone = request.form.get('phone')
        address = request.form.get('address')
        
        existing_user = db.User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            if existing_user.username == username:
                flash('Username already exists. Please choose a different one.', 'danger')
            else:
                flash('Email already exists. Please use a different email.', 'danger')
            return redirect(url_for('register'))
        
        dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
        
        hashed_password = generate_password_hash(password)
        
        new_user = User(
            username=username,
            password=hashed_password,
            full_name=full_name,
            qualification=qualification,
            dob=dob,
            email=email,
            phone=phone,
            address=address,
            status='active',
            is_admin=False
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.htm')


def current_user():
    user_id = session.get('user_id')
    if user_id:
        return User.query.get(user_id)
    return None


@app.context_processor
def inject_current_user():
    return dict(current_user=current_user())

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user():
            flash('Please log in first.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = current_user()
        if not user or not user.is_admin:
            flash('Admin access required.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.user_id
            session['username'] = user.username
            session['is_admin'] = user.is_admin
            
            flash('Logged in successfully!', 'success')
            return redirect(url_for('dashboard' if user.is_admin else 'user_dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.htm')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('login'))

@app.route('/dashboard')
@admin_required
def dashboard():
    subjects = Subject.query.all()
    return render_template('dashboard.htm', subjects=subjects)

@app.route('/subjects', methods=['GET', 'POST'])
@admin_required
def subjects():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        
        new_subject = Subject(name=name, description=description)
        db.session.add(new_subject)
        db.session.commit()
        
        flash('Subject added successfully!', 'success')
        return redirect(url_for('subjects'))
    
    subjects = Subject.query.all()
    return render_template('subjects.htm', subjects=subjects)

@app.route('/subjects/edit/<int:subject_id>', methods=['GET', 'POST'])
@admin_required
def edit_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    
    if request.method == 'POST':
        subject.name = request.form.get('name')
        subject.description = request.form.get('description')
        
        db.session.commit()
        flash('Subject updated successfully!', 'success')
        return redirect(url_for('subjects'))
    
    return render_template('edit_subject.htm', subject=subject)

@app.route('/subjects/delete/<int:subject_id>')
@admin_required
def delete_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    db.session.delete(subject)
    db.session.commit()
    
    flash('Subject deleted successfully!', 'success')
    return redirect(url_for('subjects'))

@app.route('/chapters/<int:subject_id>', methods=['GET', 'POST'])
@admin_required
def chapters(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    
    if request.method == 'POST':
        chapter_name = request.form.get('chapter_name')
        description = request.form.get('description')
        
        new_chapter = Chapter(chapter_name=chapter_name, description=description, subject_id=subject_id)
        db.session.add(new_chapter)
        db.session.commit()
        
        flash('Chapter added successfully!', 'success')
        return redirect(url_for('chapters', subject_id=subject_id))
    
    return render_template('chapters.htm', subject=subject, chapters=subject.chapters)

@app.route('/chapters/edit/<int:chapter_id>', methods=['GET', 'POST'])
@admin_required
def edit_chapter(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    
    if request.method == 'POST':
        chapter.chapter_name = request.form.get('chapter_name')
        chapter.description = request.form.get('description')
        
        db.session.commit()
        flash('Chapter updated successfully!', 'success')
        return redirect(url_for('chapters', subject_id=chapter.subject_id))
    
    return render_template('edit_chapter.htm', chapter=chapter)

@app.route('/chapters/delete/<int:chapter_id>')
@admin_required
def delete_chapter(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    subject_id = chapter.subject_id
    
    db.session.delete(chapter)
    db.session.commit()
    
    flash('Chapter deleted successfully!', 'success')
    return redirect(url_for('chapters', subject_id=subject_id))

@app.route('/quizzes')
@admin_required
def quizzes():
    quizzes = Quiz.query.all()
    return render_template('quizzes.htm', quizzes=quizzes)

@app.route('/quizzes/new', methods=['GET', 'POST'])
@admin_required
def add_quiz():
    chapters = Chapter.query.all()  # Fetch all chapters for dropdown

    if request.method == 'POST':
        name = request.form.get('name')
        chapter_id = request.form.get('chapter_id')
        date_str = request.form.get('date_of_quiz')
        time_str = request.form.get('time_duration')
        remarks = request.form.get('remarks')

        date_of_quiz = datetime.strptime(date_str, '%Y-%m-%d').date()
        time_duration = datetime.strptime(time_str, '%H:%M').time()

        new_quiz = Quiz(
            name=name,
            chapter_id=chapter_id,
            date_of_quiz=date_of_quiz,
            time_duration=time_duration,
            remarks=remarks
        )

        db.session.add(new_quiz)
        db.session.commit()

        flash('Quiz added successfully!', 'success')
        return redirect(url_for('quizzes'))  # Redirect back to the quizzes page

    return render_template('add_quiz.htm', chapters=chapters)

@app.route('/quizzes/<int:chapter_id>', methods=['GET', 'POST'])
@admin_required
def chapter_quizzes(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    
    if request.method == 'POST':
        name = request.form.get('name')
        date_str = request.form.get('date_of_quiz')
        time_str = request.form.get('time_duration')
        remarks = request.form.get('remarks')
        
        date_of_quiz = datetime.strptime(date_str, '%Y-%m-%d').date()
        time_duration = datetime.strptime(time_str, '%H:%M').time()
        
        new_quiz = Quiz(
            name=name,
            chapter_id=chapter_id,
            date_of_quiz=date_of_quiz,
            time_duration=time_duration,
            remarks=remarks
        )
        
        db.session.add(new_quiz)
        db.session.commit()
        
        flash('Quiz added successfully!', 'success')
        return redirect(url_for('chapter_quizzes', chapter_id=chapter_id))
    
    return render_template('chapter_quizzes.htm', chapter=chapter, quizzes=chapter.quizzes)

@app.route('/quizzes/edit/<int:quiz_id>', methods=['GET', 'POST'])
@admin_required
def edit_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    
    if request.method == 'POST':
        quiz.name = request.form.get('name')
        date_str = request.form.get('date_of_quiz')
        time_str = request.form.get('time_duration')
        quiz.remarks = request.form.get('remarks')
        
        quiz.date_of_quiz = datetime.strptime(date_str, '%Y-%m-%d').date()
        quiz.time_duration = datetime.strptime(time_str, '%H:%M').time()
        
        db.session.commit()
        flash('Quiz updated successfully!', 'success')
        return redirect(url_for('chapter_quizzes', chapter_id=quiz.chapter_id))
    
    return render_template('edit_quiz.htm', quiz=quiz)

@app.route('/quizzes/delete/<int:quiz_id>')
@admin_required
def delete_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    chapter_id = quiz.chapter_id
    
    db.session.delete(quiz)
    db.session.commit()
    
    flash('Quiz deleted successfully!', 'success')
    return redirect(url_for('chapter_quizzes', chapter_id=chapter_id))

@app.route('/questions/<int:quiz_id>', methods=['GET', 'POST'])
@admin_required
def questions(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    
    if request.method == 'POST':
        question_text = request.form.get('question')
        option1 = request.form.get('option1')
        option2 = request.form.get('option2')
        option3 = request.form.get('option3')
        option4 = request.form.get('option4')
        correct_option = int(request.form.get('correct_option'))
        time_str = request.form.get('time_duration') if request.form.get('time_duration') else "00:00"
        remarks = request.form.get('remarks')
        
        time_duration = datetime.strptime(time_str, '%H:%M').time()
        
        new_question = Question(
            question=question_text,
            option1=option1,
            option2=option2,
            option3=option3,
            option4=option4,
            correct_option=correct_option,
            quiz_id=quiz_id,
            time_duration=time_duration,
            remarks=remarks
        )
        
        db.session.add(new_question)
        db.session.commit()
        
        flash('Question added successfully!', 'success')
        return redirect(url_for('questions', quiz_id=quiz_id))
    
    return render_template('questions.htm', quiz=quiz, questions=quiz.questions)

@app.route('/questions/edit/<int:question_id>', methods=['GET', 'POST'])
@admin_required
def edit_question(question_id):
    question = Question.query.get_or_404(question_id)
    
    if request.method == 'POST':
        question.question = request.form.get('question')
        question.option1 = request.form.get('option1')
        question.option2 = request.form.get('option2')
        question.option3 = request.form.get('option3')
        question.option4 = request.form.get('option4')
        question.correct_option = int(request.form.get('correct_option'))
        time_str = request.form.get('time_duration')
        question.remarks = request.form.get('remarks')
        
        if time_str:
            question.time_duration = datetime.strptime(time_str, '%H:%M').time()
        
        db.session.commit()
        flash('Question updated successfully!', 'success')
        return redirect(url_for('questions', quiz_id=question.quiz_id))
    
    return render_template('edit_question.htm', question=question)

@app.route('/questions/delete/<int:question_id>')
@admin_required
def delete_question(question_id):
    question = Question.query.get_or_404(question_id)
    quiz_id = question.quiz_id
    
    db.session.delete(question)
    db.session.commit()
    
    flash('Question deleted successfully!', 'success')
    return redirect(url_for('questions', quiz_id=quiz_id))

@app.route('/search', methods=['GET', 'POST'])
@admin_required
def search():
    query = request.args.get('query', '')
    category = request.args.get('category', 'all')
    
    if not query:
        return render_template('search.htm', results=None, query=query, category=category)
    
    results = {}
    
    if category == 'all' or category == 'users':
        users = User.query.filter(
            (User.username.contains(query)) | 
            (User.full_name.contains(query)) | 
            (User.email.contains(query))
        ).all()
        results['users'] = users
    
    if category == 'all' or category == 'subjects':
        subjects = Subject.query.filter(
            (Subject.name.contains(query)) | 
            (Subject.description.contains(query))
        ).all()
        results['subjects'] = subjects
    
    if category == 'all' or category == 'quizzes':
        quizzes = Quiz.query.filter(
            (Quiz.name.contains(query)) | 
            (Quiz.remarks.contains(query))
        ).all()
        results['quizzes'] = quizzes
    
    return render_template('search.htm', results=results, query=query, category=category)


@app.route('/summary')
@login_required 
def summary():
    user_count = db.session.query(func.count(User.user_id)).scalar()
    subject_count = db.session.query(func.count(Subject.subject_id)).scalar()
    quiz_count = db.session.query(func.count(Quiz.quiz_id)).scalar()
    question_count = db.session.query(func.count(Question.question_id)).scalar()

    recent_quizzes = db.session.query(Quiz).order_by(Quiz.date_of_quiz.desc()).limit(5).all()

    quiz_scores = db.session.query(
        Quiz.name.label('quiz_name'),
        func.avg(Scores.total_scored).label('avg_score')
    ).outerjoin(Scores).group_by(Quiz.quiz_id).all()

    quiz_names = [quiz.quiz_name for quiz in quiz_scores]
    avg_scores = [round(quiz.avg_score, 2) if quiz.avg_score else 0 for quiz in quiz_scores]

    return render_template(
        'summaryad.htm',
        user_count=user_count,
        subject_count=subject_count,
        quiz_count=quiz_count,
        question_count=question_count,
        recent_quizzes=recent_quizzes,
        quiz_names=quiz_names,
        avg_scores=avg_scores
    )

def create_admin():
    with app.app_context():  
        db.create_all()

        admin = User.query.filter_by(username='admin').first()
        if not admin:
            hashed_password = generate_password_hash('admin123')
            admin = User(
                username='admin',
                password=hashed_password,
                full_name='Admin User',
                qualification='Administrator',
                dob=date(1990, 1, 1),
                email='admin@example.com',
                phone='1234567890',
                address='Admin Address',
                status='active',
                is_admin=True
            )

            db.session.add(admin)
            db.session.commit()
            print("Admin user created!")

create_admin()


@app.route('/user_dashboard')
@login_required
def user_dashboard():
    today = date.today()
    upcoming_quizzes = Quiz.query.filter(Quiz.date_of_quiz >= today).order_by(Quiz.date_of_quiz).all()
    
    upcoming_quiz_data = []
    for quiz in upcoming_quizzes:
        question_count = Question.query.filter_by(quiz_id=quiz.quiz_id).count()
        upcoming_quiz_data.append({
            'quiz': quiz,
            'question_count': question_count,
            'chapter_name': quiz.chapter.chapter_name,
            'subject_name': quiz.chapter.subject.name
        })
    
    return render_template('user/dashboard.htm', upcoming_quizzes=upcoming_quiz_data)

@app.route('/quiz/<int:quiz_id>/details')
@login_required
def quiz_details(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    question_count = Question.query.filter_by(quiz_id=quiz_id).count()
    
    previous_attempt = Scores.query.filter_by(user_id=current_user().user_id, quiz_id=quiz_id).first()
    
    return render_template('user/quiz_details.htm', 
                          quiz=quiz, 
                          question_count=question_count,
                          chapter=quiz.chapter,
                          subject=quiz.chapter.subject,
                          previous_attempt=previous_attempt)

@app.route('/quiz/<int:quiz_id>/start')
@login_required
def start_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    
    previous_attempt = Scores.query.filter_by(user_id=current_user().user_id, quiz_id=quiz_id).first()
    if previous_attempt:
        flash('You have already attempted this quiz!', 'warning')
        return redirect(url_for('user_dashboard'))
    
    session['start_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    session['current_question'] = 0
    session['answers'] = {}
    
    return render_template('user/quiz.htm', 
                          quiz=quiz,
                          questions=questions,
                          current_question=0,
                          total_questions=len(questions),
                          answers={})

@app.route('/quiz/<int:quiz_id>/save_answer', methods=['POST'])
@login_required
def save_answer(quiz_id):
    question_id = request.form.get('question_id')
    answer = request.form.get('answer')
    current_question = int(request.form.get('current_question'))
    total_questions = int(request.form.get('total_questions'))
    
    if 'answers' not in session:
        session['answers'] = {}
    
    session['answers'][question_id] = answer
    session.modified = True
    
    if current_question >= total_questions - 1:
        return redirect(url_for('submit_quiz', quiz_id=quiz_id))
    
    next_question = current_question + 1
    return redirect(url_for('display_question', quiz_id=quiz_id, question_number=next_question))

@app.route('/quiz/<int:quiz_id>/question/<int:question_number>')
@login_required
def display_question(quiz_id, question_number):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    
    if question_number >= len(questions):
        return redirect(url_for('submit_quiz', quiz_id=quiz_id))
    
    session['current_question'] = question_number
    
    return render_template('user/quiz.htm', 
                          quiz=quiz,
                          questions=questions,
                          current_question=question_number,
                          total_questions=len(questions),
                          answers=session.get('answers', {}))

@app.route('/quiz/<int:quiz_id>/submit', methods=['GET', 'POST'])
@login_required
def submit_quiz(quiz_id):
    if request.method == 'POST' or request.method == 'GET':
        quiz = Quiz.query.get_or_404(quiz_id)
        questions = Question.query.filter_by(quiz_id=quiz_id).all()
        
        total_score = 0
        for question in questions:
            if str(question.question_id) in session.get('answers', {}):
                user_answer = int(session['answers'][str(question.question_id)])
                if user_answer == question.correct_option:
                    total_score += 1
        
        start_time = datetime.strptime(session.get('start_time', datetime.now().strftime('%Y-%m-%d %H:%M:%S')), '%Y-%m-%d %H:%M:%S')
        end_time = datetime.now()
        time_taken = end_time - start_time
        time_taken_str = str(time_taken).split('.')[0]  # Format as hh:mm:ss
        
        new_score = Scores(
            quiz_id=quiz_id,
            total_scored=total_score,
            user_id=current_user().user_id,
            timestamp_date_of_attempt=date.today(),
            time_taken=time(hour=int(time_taken_str.split(':')[0]), 
                           minute=int(time_taken_str.split(':')[1]), 
                           second=int(time_taken_str.split(':')[2])),
            time_stamp_of_attempt=time(hour=end_time.hour, minute=end_time.minute, second=end_time.second),
            remarks=f"Completed {total_score}/{len(questions)} correct"
        )
        
        db.session.add(new_score)
        db.session.commit()
        
        if 'answers' in session:
            session.pop('answers')
        if 'start_time' in session:
            session.pop('start_time')
        if 'current_question' in session:
            session.pop('current_question')
        
        flash(f'Quiz submitted! You scored {total_score} out of {len(questions)}', 'success')
        return redirect(url_for('score_details', score_id=new_score.score_id))
    
    return redirect(url_for('dashboard'))

@app.route('/scores')
@login_required
def scores():
    user_scores = Scores.query.filter_by(user_id=current_user().user_id).order_by(Scores.timestamp_date_of_attempt.desc()).all()
    
    score_data = []
    for score in user_scores:
        quiz = Quiz.query.get(score.quiz_id)
        question_count = Question.query.filter_by(quiz_id=score.quiz_id).count()
        
        score_data.append({
            'score': score,
            'quiz': quiz,
            'chapter_name': quiz.chapter.chapter_name,
            'subject_name': quiz.chapter.subject.name,
            'question_count': question_count,
            'percentage': (score.total_scored / question_count) * 100 if question_count > 0 else 0
        })
    
    return render_template('user/scores.htm', scores=score_data)

@app.route('/score/<int:score_id>')
@login_required
def score_details(score_id):
    score = Scores.query.get_or_404(score_id)
    
    if score.user_id != current_user().user_id:
        flash('Access denied!', 'danger')
        return redirect(url_for('dashboard'))
    
    quiz = Quiz.query.get(score.quiz_id)
    questions = Question.query.filter_by(quiz_id=score.quiz_id).all()
    
    return render_template('user/score_details.htm', 
                          score=score,
                          quiz=quiz,
                          questions=questions,
                          chapter=quiz.chapter,
                          subject=quiz.chapter.subject)

@app.route('/user_summary')
@login_required
def user_summary():
    subject_summary = db.session.query(
        Subject.name.label('subject'),
        func.count(Scores.score_id).label('attempts'),
        func.avg(Scores.total_scored).label('avg_score')
    ).join(Chapter).join(Quiz).join(Scores) \
     .filter(Scores.user_id == current_user().user_id) \
     .group_by(Subject.subject_id).all()
    
    current_year = datetime.now().year
    month_summary = db.session.query(
        extract('month', Scores.timestamp_date_of_attempt).label('month'),
        func.count(Scores.score_id).label('attempts'),
        func.avg(Scores.total_scored).label('avg_score')
    ).filter(
        Scores.user_id == current_user().user_id,
        extract('year', Scores.timestamp_date_of_attempt) == current_year
    ).group_by(extract('month', Scores.timestamp_date_of_attempt)).all()
    
    months = ['January', 'February', 'March', 'April', 'May', 'June', 
              'July', 'August', 'September', 'October', 'November', 'December']
    month_data = []
    for month_num in range(1, 13):
        month_item = next((item for item in month_summary if item.month == month_num), None)
        if month_item:
            month_data.append({
                'month': months[month_num-1],
                'attempts': month_item.attempts,
                'avg_score': round(month_item.avg_score, 2)
            })
        else:
            month_data.append({
                'month': months[month_num-1],
                'attempts': 0,
                'avg_score': 0
            })
    
    recent_scores = Scores.query.filter_by(user_id=current_user().user_id) \
                         .order_by(Scores.timestamp_date_of_attempt.desc()) \
                         .limit(5).all()
    
    recent_activity = []
    for score in recent_scores:
        quiz = Quiz.query.get(score.quiz_id)
        question_count = Question.query.filter_by(quiz_id=score.quiz_id).count()
        
        recent_activity.append({
            'score': score,
            'quiz': quiz,
            'chapter_name': quiz.chapter.chapter_name,
            'subject_name': quiz.chapter.subject.name,
            'question_count': question_count,
            'percentage': (score.total_scored / question_count) * 100 if question_count > 0 else 0
        })
    
    return render_template('user/summary.htm', 
                          subject_summary=subject_summary,
                          month_data=json.dumps(month_data),
                          recent_activity=recent_activity)

@app.route('/profile')
@login_required
def profile():
    return render_template('user/profile.htm')

@app.route('/user_search')
@login_required
def user_search():
    query = request.args.get('q', '')
    if not query:
        return redirect(url_for('dashboard'))
    
    quizzes = Quiz.query.filter(Quiz.name.ilike(f'%{query}%')).all()
    
    subjects = Subject.query.filter(Subject.name.ilike(f'%{query}%')).all()
    
    chapters = Chapter.query.filter(Chapter.chapter_name.ilike(f'%{query}%')).all()
    
    return render_template('user/search_results.htm', 
                          query=query,
                          quizzes=quizzes,
                          subjects=subjects,
                          chapters=chapters)




if __name__ == '__main__':
    app.run(debug=True)



