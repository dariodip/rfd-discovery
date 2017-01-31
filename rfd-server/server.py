from flask import Flask,request,render_template,jsonify

app = Flask(__name__, static_url_path='/static')


@app.route("/")
def index():
    return render_template('index.html', name="")


@app.route('/_add_numbers')
def add_numbers():
    print (request)
    a = request.args.get('a', 0, type=int)
    b = request.args.get('b', 0, type=int)
    return jsonify(result=a + b)


@app.route('/api/upload', methods=['POST', 'GET'])
def upload():
    error = None
    if request.method == 'POST':
        f = request.files['file']
        return f.read()
    else:
        error = 'Invalid data'
        return render_template('index.html', error=error,meth="GET")

if __name__ == "__main__":
     app.run(debug=True)
