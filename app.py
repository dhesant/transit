# from http://flask.pocoo.org/ tutorial
from flask import Flask, render_template
app = Flask(__name__)

@app.route("/") # take note of this decorator syntax, it's a common pattern
def hello():
    return "Hello World!"

@app.route('/welcome')
def welcome():
        return render_template('welcome.html')

if __name__ == "__main__":
    app.run(debug=True)

