import flask
from flask import Flask,request,render_template,jsonify
import os
import run as run
app = Flask(__name__, static_url_path='/static')
app.config['UPLOAD_FOLDER'] = os.path.join('resources','upload')


@app.route("/")
def index():
    return render_template('index.html', name="")


@app.route('/api/upload', methods=['POST', 'GET'])
def upload():
    error = None
    if request.method == 'POST':
        file = request.files['file']
        if file:
            params = run.param_to_dict(request.form)
            csv_file = os.path.join('..',app.config['UPLOAD_FOLDER'], file.filename)
            fd = file.save(csv_file)
            return flask.jsonify(run.main(csv_file, params))
    else:
        error = 'Invalid data'
        return render_template('index.html', error=error,meth="GET")

if __name__ == "__main__":
     app.run(debug=True)
