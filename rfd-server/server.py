from flask import Flask,request,render_template,jsonify
#from dominance.dominance_tools import RFDDiscovery
#from loader.distance_mtr import DiffMatrix
import io
import os


app = Flask(__name__, static_url_path='/static')
app.config['UPLOAD_FOLDER'] = os.path.join('..','resources','upload')


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
        print(f)
        print(os.path.join(app.config['UPLOAD_FOLDER'], f.filename))
        print(request.form)
        params = request.form # ImmutableMultiDict ('header', 'true'), ('separator', ';')
        physicalfile = os.path.join(app.config['UPLOAD_FOLDER'], f.filename)
        # hss = {"lhs": [1, 2, 3], "rhs": [0]}

        # fd = f.save(physicalfile)
        # diff_mtx = DiffMatrix(physicalfile, {})
        # diff_mtx.load()
        # dist_mtx = diff_mtx.distance_matrix(hss)
        # diff_mtx = None     # for free unused memory
        # nd = RFDDiscovery(dist_mtx)
        # result = str(nd.get_rfds(nd.standard_algorithm, hss))
        return "result"
    else:
        error = 'Invalid data'
        return render_template('index.html', error=error,meth="GET")

if __name__ == "__main__":
     app.run(debug=True)
