from flask import Flask, request, jsonify
import SQLiteController, argparse, FirebaseController

app = Flask(__name__)
c = SQLiteController
f = FirebaseController
parser = argparse.ArgumentParser(description='Script to interact with either SQLite or Firebase storage')
parser.add_argument('-r', '--version', choices=['sqlite', 'firebase'], required=True, help='Specify either sqlite or firebase')
args = parser.parse_args()
v = 'f' if args.version == 'firebase' else 's'

if v == 's':
    c.clear_table()
    c.init_db()
else:
    f.reset_db()

@app.route("/cells/<id>", methods=['PUT'])
def create(id):
    js = request.get_json()
    try:
        r_id = js['id']
        formula = js['formula']
        if r_id != id:
            return "",400
        
        # if firebase
        if v == 'f':
            # execute firebase
            r = f.create(id, formula)
            return "",r
        else:
            c.create(id, formula)
            is_numeric = c.is_numeric_string(formula)
            if is_numeric:
                # create cell
                return "",201
            else:
                # is a reference to other cells
                return "",204
        
    except KeyError:
        return "",400
    

@app.route('/cells/<id>', methods=['GET'])
def read(id):
    if v == 'f':
        r = f.read(id)
        code = r[0]
        val = r[1]
        if code == 200:
            # "formula":"42"
            return f"\"formula\":\"{val}\"",code
        else:
            return "",code

    else:
        r = c.read(id)

        if r[0] == 200:
            t = str(r[1])
            return f"\"formula\":\"{t}\"",200
        elif r[0] == 404:
            return "",404
        else:
            return "",500

@app.route('/cells', methods=['GET'])
def list():
    if v == 's':
        # sqlite version
        try:
            r = c.read()
            if r[0] == 200:
                # make array of only cell id's
                ids = [t[0] for t in r[1]]
                print(str(ids))
                return str(ids),200
        except Exception as e:
            print(e)
            return "",500
    else:
        # firebase version
        try:
            r = f.read()
            if r[1] == 200:
                ids = [t for t in r[0]]
                if ids[0] == '^^':
                    ids.pop(0)
                return str(ids),200
        except Exception as e:
            print(e)
            return "",500




@app.route('/cells/delete_table', methods=['GET'])
def delete_table():
    c.clear_table()

# @app.route('/cells/create_table', methods=['GET'])
# def create_table():
#     c.init_db()
#     return "Create table"

if __name__ == '__main__':
    app.run(host='localhost', port=3000, debug=True)