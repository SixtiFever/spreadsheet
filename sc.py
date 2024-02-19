from flask import Flask, request
import Controller

app = Flask(__name__)
c = Controller

@app.route("/cells/<id>", methods=['PUT'])
def create(id):
    js = request.get_json()
    try:
        r_id = js['id']
        formula = js['formula']
        if r_id != id:
            return "",400
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
    r = c.read(id)
    print(r)
    if r == 200:
        return "",200
    elif r == 404:
        return "",404
    else:
        return "",500

@app.route('/cells', methods=['GET'])
def list():
    print('test')
    try:
        r = c.read()
        print(r)
        return "",200
    except Exception as e:
        return "",500



if __name__ == '__main__':
    app.run(host='localhost', port=3000, debug=True)