from flask import Flask,url_for,render_template,request,session,redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
from langdetect import detect

import datetime
import spacy
import enum
from spacy import displacy
import json

HTML_WRAPPER = """<div style="overflow-x: auto; border: 1px solid #e6e9ef; border-radius: 0.25rem; padding: 1rem">{}</div>"""

from flaskext.markdown import Markdown

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ner.db'
app.config['SECRET_KEY'] = 'thisisasecretkey'
Markdown(app)
bcrypt = Bcrypt(app)
db = SQLAlchemy(app)



login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(30), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)

class LangType(enum.Enum):
    en = "en"
    fr = "fr"
    ja = "ja"
    nl = "nl"
    es = "es"

class Sentence(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text(), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    lang_type = db.Column(db.Enum(LangType), nullable=False, default=LangType.en)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

db.create_all()
class RegisterForm(FlaskForm):
	name = StringField(validators=[
        InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Name"})
    
	email = EmailField(validators=[InputRequired()], render_kw={"placeholder": "Email"})

	password = PasswordField(validators=[
        InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

	submit = SubmitField('Register')

	def validate_email(self, email):
		existing_user_email = User.query.filter_by(
            email=email.data).first()
		if existing_user_email:
			raise ValidationError(
                'That username already exists. Please choose a different one.')


class LoginForm(FlaskForm):
    email = StringField(validators=[
                           InputRequired()], render_kw={"placeholder": "Email"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Submit')



@app.route('/')
@login_required
def index():
	# raw_text = "Bill Gates is An American Computer Scientist since 1986"
	# docx = nlp(raw_text)
	# html = displacy.render(docx,style="ent")
	# html = html.replace("\n\n","\n")
	# result = HTML_WRAPPER.format(html)

	return render_template('index.html')


@app.route('/extract',methods=["GET","POST"])
@login_required
def extract():
    if request.method == 'POST':
        raw_text = request.form['rawtext']
        lang = request.form['lang']

        if raw_text.isspace() == True or lang == "":
            return redirect(url_for("index"))

        if lang not in ["en","fr","ja","nl","es"]:
            lang = "en"
             
        
        sentence = Sentence(content=raw_text, user_id=current_user.id, lang_type=lang)
        db.session.add(sentence)
        db.session.commit()

    all_sentence =  Sentence.query.filter_by(user_id=current_user.id)
    english_sent = []
    if request.args.get('lang') == 'en':
        en_sentences = all_sentence.filter_by(lang_type="en").all()
        nlp = spacy.load('en_core_web_lg')
        for i in en_sentences:
            docx = nlp(i.content)
            html = displacy.render(docx,style="ent")
            html = html.replace("\n\n","\n")
            result = HTML_WRAPPER.format(html)
            english_sent.append((i.content, result))
    elif request.args.get('lang') == 'fr':
        en_sentences = all_sentence.filter_by(lang_type="fr").all()
        nlp = spacy.load('fr_core_news_lg')
        for i in en_sentences:
            docx = nlp(i.content)
            html = displacy.render(docx,style="ent")
            html = html.replace("\n\n","\n")
            result = HTML_WRAPPER.format(html)
            english_sent.append((i.content, result))
    elif request.args.get('lang') == 'es':
        en_sentences = all_sentence.filter_by(lang_type="es").all()
        nlp = spacy.load('es_core_news_lg')
        for i in en_sentences:
            docx = nlp(i.content)
            html = displacy.render(docx,style="ent")
            html = html.replace("\n\n","\n")
            result = HTML_WRAPPER.format(html)
            english_sent.append((i.content, result))
    elif request.args.get('lang') == 'nl':
        en_sentences = all_sentence.filter_by(lang_type="nl").all()
        nlp = spacy.load('nl_core_news_lg')
        for i in en_sentences:
            docx = nlp(i.content)
            html = displacy.render(docx,style="ent")
            html = html.replace("\n\n","\n")
            result = HTML_WRAPPER.format(html)
            english_sent.append((i.content, result))
    elif request.args.get('lang') == 'ja':
        en_sentences = all_sentence.filter_by(lang_type="ja").all()
        nlp = spacy.load('ja_core_news_lg')
        for i in en_sentences:
            docx = nlp(i.content)
            html = displacy.render(docx,style="ent")
            html = html.replace("\n\n","\n")
            result = HTML_WRAPPER.format(html)
            english_sent.append((i.content, result))
    else:
        en_sentences = all_sentence.filter_by(lang_type="en").all()
        nlp = spacy.load('en_core_web_lg')
        for i in en_sentences:
            docx = nlp(i.content)
            html = displacy.render(docx,style="ent")
            html = html.replace("\n\n","\n")
            result = HTML_WRAPPER.format(html)
            english_sent.append((i.content, result))

    return render_template('result.html', english_sent=english_sent)



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('index'))
    return render_template('login.html', form=form)


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@ app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(name=form.name.data,email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('register.html', form=form)



if __name__ == '__main__':
    app.run(debug=True)
