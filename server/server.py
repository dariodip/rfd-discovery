import flask
from flask import Flask,request,render_template,jsonify
import os
import run
import sys

"""
This module start the server used by the web gui to elaborate the user's requests. It use as IP address the localhost,
and it take as parameter the listening port. If the port is omitted, the server will use the default port 5000.
"""

app = Flask(__name__, static_url_path='/static')
app.config['UPLOAD_FOLDER'] = os.path.join('resources','upload')


@app.route("/")
def index():
    """
    Generate the web gui's index page.
    :return: web gui's index page
    """
    return render_template('index.html', name="")


@app.route('/api/upload', methods=['POST', 'GET'])
def upload():
    """
    Given an uploaded file, save it and return a JSON containing parameters about the function that execute
    the algorithm.
    If it can not open that file, return an error message.
    :return: a JSON with the function call that execute the algorithm or a web page with an error message
    """
    if request.method == 'POST':
        file = request.files['file']
        if file:
            csv_file = os.path.join('..', app.config['UPLOAD_FOLDER'], file.filename)
            fd = file.save(csv_file)
            return flask.jsonify(run.main(csv_file, request.form))
    else:
        error = 'Invalid data'
        return render_template('index.html', error=error,meth="GET")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        port = 5000
    else:
        port = int(sys.argv[1])
    app.run(debug=True, port=port)

