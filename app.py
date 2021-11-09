import os
import json

from flask import Flask, render_template, request, redirect, url_for, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore, login_required, \
    UserMixin, RoleMixin, roles_required
from flask_security.utils import hash_password, logout_user
import sqlite3

app = Flask(__name__)
app.config['SECRET_KEY'] = 'thisisasecret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SECURITY_PASSWORD_SALT'] = 'thisisasecretsalt'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

roles_users = db.Table('roles_users',
                       db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                       db.Column('role_id', db.Integer, db.ForeignKey('role.id')))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean)
    confirmed_at = db.Column(db.DateTime)
    roles = db.relationship(
        'Role',
        secondary=roles_users,
        backref=db.backref('users', lazy='dynamic')
    )


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40))
    description = db.Column(db.String(255))


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(1000))


class Title(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(1000))


user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)


@app.before_first_request
def setup():
    # Recreate database each time for demo
    db.drop_all()
    db.create_all()
    with open('config.json') as f:
        config = json.load(f)
    user_datastore.create_role(**config['roles']['admin'])
    user_datastore.create_role(**config['roles']['user'])
    db.session.commit()

    users = config['users']
    user_datastore.create_user(
        email=users['admin']['email'],
        password=hash_password(users['admin']['password']),
        roles=['admin']
    )
    user_datastore.create_user(
        email=users['basic_user']['email'],
        password=hash_password(users['basic_user']['password']),
        roles=['user']
    )
    db.session.add(Title(text='Portal de Noticias Empresarial'))
    db.session.add(Post(text='El viernes 8 de Octubre es Feriado.'))
    db.session.add(Post(text='El aguinaldo de diciembre 2021 se pagará en 27 cuotas a partir de julio 2022.'))
    db.session.commit()


@app.route('/register', methods=['POST', 'GET'])
@login_required
@roles_required('admin')
def register():
    if request.method == 'POST':
        is_admin = request.form.get('is_admin')
        new_user_role = 'admin' if is_admin else 'user'
        user_datastore.create_user(
            email=request.form.get('email'),
            password=hash_password(request.form.get('password')),
            roles=[new_user_role]
        )
        db.session.commit()

        return redirect(url_for('profile'))

    return render_template('register.html')


@app.route('/')
def index():
    posible_titles = [post.text for post in Title.query.all()]

    return render_template('index.html', subtitle=posible_titles[0])


@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')


@app.route('/creacion_post', methods=['POST', 'GET'])
@login_required
@roles_required('admin')
def creacion_post():
    if request.method == 'POST':
        text = request.form.get('post_text_input')
        query = f"insert into post (text) values ('{text}')"
        conn = sqlite3.connect('db.sqlite3')
        conn.executescript(query)
        conn.commit()
    return render_template('creacion_post.html')


@app.route('/posts')
@login_required
def posts():
    posts_txt = [post.text for post in Post.query.all()]
    return render_template('posts.html', list_of_posts=posts_txt)


@app.route('/images')
@login_required
def images():
    image_name = request.args.get('image_name')
    if not image_name:
        return 404
    return send_file(os.path.join(os.getcwd(), image_name))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return render_template('index.html')


@app.errorhandler(Exception)
def handle_exception(e):
    return str(e), 500
