import numpy as np
import pandas as pd

from flask import render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_user, login_required, logout_user, current_user
from sqlalchemy.orm import sessionmaker
from werkzeug.security import check_password_hash, generate_password_hash

from task_2.my_app import app, db
from task_2.my_app.models import User, Data

from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")


@app.route('/', methods=['GET'])
def hello_world():
    return render_template('index.html')


@app.route('/main', methods=['GET'])
@login_required
def main():
    return render_template('main.html')


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    login = request.form.get('login')
    password = request.form.get('password')

    if login and password:
        user = User.query.filter_by(login=login).first()

        if user and check_password_hash(user.password, password):
            app.logger.info('User logged in')
            login_user(user)
            return redirect(url_for('main'))
        else:
            flash('Login or password is not correct')
    else:
        flash('Please fill login and password fields')

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    login = request.form.get('login')
    password = request.form.get('password')
    password2 = request.form.get('password2')
    email = request.form.get('email')
    existing_user = User.query.filter_by(login=login).first()
    user_with_same_email = User.query.filter_by(email=email).first()
    if user_with_same_email:
        flash('User with this email already exists!')
        return render_template('register.html')
    if existing_user:
        flash('User with this login already exists!')
        return render_template('register.html')
    if request.method == 'POST':
        if not (login and password and password2):
            flash('Please, fill all fields!')
        elif password != password2:
            flash('Passwords are not equal!')
        elif not email:
            flash('Please fill email!')
        else:
            app.logger.info('New user registered')
            hash_pwd = generate_password_hash(password)
            new_user = User(login=login, password=hash_pwd, email=email)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for('main'))

    return render_template('register.html')


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    app.logger.info('User logged out')
    logout_user()
    return redirect(url_for('hello_world'))


@app.route('/load', methods=['GET'])
@login_required
def load_data():
    return render_template("load_data.html")


@app.route('/process_data', methods=['POST'])
@login_required
def process_data():
    file = request.files['file']
    try:
        data = pd.read_csv(file)
        for _, row in data.iterrows():
            text = row['text']
            embedding = model.encode([text])[0]
            embedding_binary = np.array(embedding, dtype=np.float32).tobytes()
            data_entry = Data(text=text, embedding=embedding_binary)
            db.session.add(data_entry)
        db.session.commit()
        return jsonify({'success': 'successfully loading'}), 200
    except Exception as e:
        app.logger.error(f"Error reading CSV file: {e}")
        flash('Please upload a valid CSV file')
        return jsonify({'error': 'Invalid CSV file'}), 400


@app.route('/search_data', methods=['POST'])
@login_required
def search_query_endpoint():
    try:
        data = request.get_json()
        query = data.get('query', '')
        if not query:
            return jsonify({"error": "Query cannot be empty"}), 400
        query_embedding = model.encode([query])[0]
        query_embedding = query_embedding.tolist()
        session = sessionmaker(bind=db.engine)()

        results = []
        data_entries = session.query(Data).all()

        for entry in data_entries:
            db_embedding = np.frombuffer(entry.embedding, dtype=np.float32)
            similarity = model.similarity(query_embedding, db_embedding).tolist()[0]
            results.append({
                'text': entry.text,
                'similarity': similarity[0]
            })

        results.sort(key=lambda x: x['similarity'], reverse=True)
        return jsonify({'results': results[:5]}, 200)

    except Exception as e:
        app.logger.error(f"Error in search_query: {e}")
        return jsonify({"error": "An error occurred while processing the request"}), 500


@app.after_request
def redirect_to_signin(response):
    if response.status_code == 401:
        return redirect(url_for('login_page') + '?next=' + request.url)

    return response
