import requests,json,sys,time
from flask import render_template, url_for, flash, redirect, request,jsonify
from bakalarka import app, db, bcrypt
from bakalarka.forms import  LoginForm
from bakalarka.models import User
from flask_login import login_user, current_user, logout_user, login_required
import json


@app.context_processor
def setWeather():
    API_KEY = '1dc3d9ddda7b79c3e8e80ce27c139ae5'
    fcity = "Trstená"
    url = 'http://api.openweathermap.org/data/2.5/weather?q={}&appid={}&units=metric'
    r = requests.get(url.format(fcity,API_KEY)).json()
    ftime = time.strftime('%H:%M:%S')
    fdate = time.strftime('%A %B, %d-%m-%Y')
    icon = "http://openweathermap.org/img/w/{}.png".format(r["weather"][0]["icon"])
    
    return dict(weather=r,time = ftime,date=fdate,wicon=icon)







@app.route("/")
@app.route("/home")
@login_required
def home():
    return render_template('home.html')
  



@app.route("/scheduler")
@login_required
def scheduler():
    return render_template('scheduler.html', title='Scheduler')
  

@app.route("/login",  methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/account")
@login_required
def account():
    return render_template('account.html', title='Account')


@app.route('/data')
def return_data():
    start_date = request.args.get('start', '')
    end_date = request.args.get('end', '')
    # You'd normally use the variables above to limit the data returned
    # you don't want to return ALL events like in this code
    # but since no db or any real storage is implemented I'm just
    # returning data from a text file that contains json elements

    with open("bakalarka/events.json", "r") as input_data:
        # you should use something else here than just plaintext
        # check out jsonfiy method or the built in json module
        # http://flask.pocoo.org/docs/0.10/api/#module-flask.json
        return input_data.read()