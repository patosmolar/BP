from flask import Flask, render_template, url_for
app = Flask(__name__)

posts = [
    {
        'author': 'Corey Schafer',
        'title': 'Blog Post 1',
        'content': 'First post content',
        'date_posted': 'April 20, 2018'
    },
    {
        'author': 'Jane Doe',
        'title': 'Blog Post 2',
        'content': 'Second post content',
        'date_posted': 'April 21, 2018'
    }
]


@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', posts=posts)

@app.route("/modes")
def modes():
    return render_template('modes.html', title='Módy')

@app.route("/settings")
def settings():
    return render_template('settings.html', title='Nastavenia')
    
@app.route("/schedule")
def schedule():
    return render_template('schedule.html', title='Plánovač')
    
@app.route("/priame_ovladanie")
def priame_ovladanie():
    return render_template('priame_ovladanie.html', title='Real-Time ovládanie')


if __name__ == '__main__':
    app.run(debug=True)