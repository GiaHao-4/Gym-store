from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

@app.route('/')

def index():
    return render_template('addplan.html')

if __name__ == '__main__':
    with app.app_context():
        app.run(debug=True)
