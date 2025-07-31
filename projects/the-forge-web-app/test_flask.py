# Flask test script
from flask import Flask

app = Flask(__name__)

@app.route('/')
def test():
    return "Flask test page"

if __name__ == '__main__':
    app.run(debug=True) 