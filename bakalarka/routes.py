import requests,json,sys,time,httplib2,uuid,flask,os
from flask import render_template, url_for, flash, redirect, request,jsonify,Response
from bakalarka import app, db, bcrypt, sched,jobs
from bakalarka.forms import  LoginForm
from bakalarka.models import User
from flask_login import login_user, current_user, logout_user, login_required
from apiclient import discovery
from oauth2client import client
from googleapiclient import sample_tools
from rfc3339 import rfc3339
from dateutil import parser




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
    print(sched.print_jobs())
    return flask.redirect(flask.url_for('setCalendar'))


@app.route("/scheduler")
@login_required
def scheduler():
    cid = current_user.calendarID
    if(cid == '-1'):
        return flask.redirect(flask.url_for('setCalendar'))
    else:
        cname = current_user.calendarID   
        src = "https://calendar.google.com/calendar/embed?src="+cname 
        with open("bakalarka/static/events.json", 'r') as f:
            data = json.loads(f.read()) 
                         
        return flask.render_template('scheduler.html',src=src,events=data)


@app.route("/setCalendar")
def setCalendar():
    flask.session['next'] =  "setCalendar"
    if 'credentials' not in flask.session:
      return flask.redirect(flask.url_for('oauth2callback'))
    credentials = client.OAuth2Credentials.from_json(flask.session['credentials'])
    if credentials.access_token_expired:
        return flask.redirect(flask.url_for('oauth2callback'))
    credentials = client.OAuth2Credentials.from_json(flask.session['credentials'])
    http_auth = credentials.authorize(httplib2.Http())

    service = discovery.build('calendar', 'v3', http_auth)


    calendars = []
    
    page_token = None
    while True:
      calendar_list = service.calendarList().list(pageToken=page_token).execute()
      for calendar_list_entry in calendar_list['items']:
        calendars.append({"name": calendar_list_entry['summary'], "id": calendar_list_entry['id']})
      page_token = calendar_list.get('nextPageToken')
      if not page_token:
        break
    flash('Nastavte si kalendár')

   
    
    
    return  render_template(('account.html'),calendars=calendars)
    
    
@app.route('/updateCID',methods= ['POST'])
def updateCID():
    current_user.calendarID = request.form.get('cid')
    db.session.commit()
    return '', 204

    


#Begin oauth callback route
@app.route('/oauth2callback')
def oauth2callback():
  flow = client.flow_from_clientsecrets(
      'client_secrets.json',['https://www.googleapis.com/auth/calendar https://www.googleapis.com/auth/userinfo.email'],
      redirect_uri=flask.url_for('oauth2callback', _external=True))
  if 'code' not in flask.request.args:
    auth_uri = flow.step1_get_authorize_url()
    return flask.redirect(auth_uri)
  else:
    auth_code = flask.request.args.get('code')
    credentials = flow.step2_exchange(auth_code)
    flask.session['credentials'] = credentials.to_json()
    return flask.redirect(flask.url_for(flask.session['next']))





@app.route('/removeEntry', methods= ['POST'])
def removeEntry():
    flask.session['next'] =  "removeEntry"
    if 'credentials' not in flask.session:
      return flask.redirect(flask.url_for('oauth2callback'))
    credentials = client.OAuth2Credentials.from_json(flask.session['credentials'])
    if credentials.access_token_expired:
        return flask.redirect(flask.url_for('oauth2callback'))
    mid = request.form.get('id')
    credentials = client.OAuth2Credentials.from_json(flask.session['credentials'])
    http_auth = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http_auth)
    imported_event = service.events().delete(calendarId=current_user.calendarID, eventId=mid).execute()

    deleteEvent(mid)
    return flask.redirect(url_for('scheduler'))
def deleteEvent(mid):   
    with open("bakalarka/static/events.json", 'r') as f:
        data = json.loads(f.read()) 
        tmp = ""
        for den in data:
            for zaznam in data[den]:
                if zaznam['id'] == mid:
                    data[den].remove(zaznam)
                    if len(data[den]) == 0:
                        tmp = den
                        
                    
        if tmp != "":
            del data[tmp]
        with open("bakalarka/static/events.json", 'w') as f:
                f.write(json.dumps(data, sort_keys=True, indent=4, separators=(',', ': ')))
    resetScheduler()


@app.route('/createEntry', methods= ['POST'])
def createEntry():
    flask.session['next'] =  "createEntry"
    if 'credentials' not in flask.session:
      return flask.redirect(flask.url_for('oauth2callback'))
    credentials = client.OAuth2Credentials.from_json(flask.session['credentials'])
    if credentials.access_token_expired:
        return flask.redirect(flask.url_for('oauth2callback'))

    vyska = request.form.get('vyska')
    uhol = request.form.get('uhol')
    date = request.form.get('date')
    time = request.form.get('time')

   
    credentials = client.OAuth2Credentials.from_json(flask.session['credentials'])


    http_auth = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http_auth)
    eventName = "@scheduled"
    eventID = str(uuid.uuid4())
    event = {
        'summary': eventName,
        'start': {
        'dateTime': date+"T"+time+":00",
        'timeZone': 'Europe/Prague',
        },
        'end': {
        'dateTime': date+"T"+time+":00",
        'timeZone': 'Europe/Prague',
        },
        'description': "Výška:"+vyska + " - Uhol:"+uhol,
        'icalUID ': eventID
    }
    imported_event = service.events().insert(calendarId=current_user.calendarID, body=event).execute()
    writeEvent(vyska,uhol,date,time,imported_event['id'])

    

    return flask.redirect(url_for('scheduler'))
def writeEvent(vyska,uhol,mdate,mtime,eventID):
    date = mdate
    event = [{}]
   
    with open("bakalarka/static/events.json", 'r') as f:
        data = json.loads(f.read()) 
        if date not in data:
            event = [{ "time":mtime,"vyska":vyska,"uhol":uhol,"id":eventID}]
            data[date] = event
        else:
            event = { "time":mtime,"vyska":vyska,"uhol":uhol, "id":eventID}
            data[date].append(event)

        with open("bakalarka/static/events.json", 'w') as f:
                f.write(json.dumps(data, sort_keys=True, indent=4, separators=(',', ': ')))
    resetScheduler()



    
def resetScheduler():
    for job in sched.get_jobs():
        job.remove()
    jobs.initializer()
    sched.add_job(jobs.initializer,'cron',hour ='0')
    

    
@app.route('/work',methods=['POST'])
def work():
    vyska = request.form.get('vyska')
    uhol = request.form.get('uhol')    
    print("Nastaví výšku: "+vyska+", uhol: "+uhol)     
    return flask.redirect(url_for('home'))    
       






       