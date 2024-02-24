from flask import Flask, request, jsonify
import requests, re

url = "https://ecm3408-ff937-default-rtdb.europe-west1.firebasedatabase.app"

### UTIL FUNCTIONS ###

def reset_db():
    path = f"{url}/cells.json"
    requests.delete(path)
    res = requests.post(url=path, json={'^^':'^^'})
    if res.status_code == 200:
        print('Successfully reset database')
    else:
        print('Error resetting database')


def is_numeric_string(formula):
    try:

        # attempt to calculate the formula
        eval(formula)

        return True
    except ValueError:

        # If ValueError occurs, it means the string cannot be cast to an integer
        return False
    except Exception as e:

        return False
    
def get_formula_by_id(id):
    data = requests.get(f"{url}/cells.json").json()
    for record in data.values():
        lid = list(record.keys())[0]
        if id == lid:
            formula = list(record.values())[0]
            return formula
        
    # if id not found, return 0
    return '0'

def check_cell_exists(id):
    data = requests.get(f"{url}/cells.json").json()
    for record in data.values():
        lid = list(record.keys())[0]
        if id == lid:
            return True
    return False

def perform_formula_update(id, formula):
    data = requests.get(f"{url}/cells.json").json()
    path = f"{url}/cells/"
    for k,v in data.items():
        lid = list(v)[0]
        if lid == id:
            path += f"{k}.json"
            data = {id: formula}
            res = requests.patch(path, json=data)
            if res.status_code == 200:
                print('successful update')
                return 200
            else:
                print('update error')
                return 500


    
def perform_ref_ops(formula):
    db = requests.get(f"{url}/cells.json").json()
    f = formula
    pattern = re.compile(r'[*+()-/ " " ]') # extract references
    split_list = pattern.split(formula)
    refs = [item for item in split_list if item and not item.isdigit()]
    # replace references with corresponding values
    for id in refs:
        val = get_formula_by_id(id)
        res = eval(val)
        f = f.replace(id, str(res))
    sum = eval(f)
    return [200, sum]



## CRUD OPERATIONS ###

# create
def create(id = 0, formula = 0):
    # res = requests.post(f"{url}/cells.json", json={'Test': 'Test'})

    code = 0

    # check if request is valid is valid
    if is_numeric_string(id) or formula == 0 or id == 0:
        print('Invalid post request')
        return 400,""
    
    # check if formula is numeric or a reference
    is_numeric = is_numeric_string(formula)
    if is_numeric:
        code = 201
    else:
        # if formula is a reference
        code = 204
    
    cell_exists = check_cell_exists(id)
    data = {id : formula}
    if cell_exists:
        print('Cell exists. Performing update.')
        res = perform_formula_update(id, formula)
        print(res)
    else:
        print('Creating new cell.')
        res = requests.post(f"{url}/cells.json", json=data)
        print(res)
    return code




# read
def read(id = 0):
    """
    reads from the firebase database
    """

    data = requests.get(f"{url}/cells.json").json()

    # if cell id is invalid
    if is_numeric_string(id):
        print('invalid id')
        return [404,0]

    # print list if not id is given
    if id == 0:
        ids = []
        for record in data.values():
            lid = list(record.keys())[0]
            ids.append(lid)
        return ids,200
    else:

        for record in data.values():
            lid = list(record.keys())[0]
            if lid == id:
                # perform calculation
                formula = list(record.values())[0]

                # if cell value can be calculated directly i.e is numeric
                if is_numeric_string(formula):
                    s = eval(formula)
                    print(s)
                    return [200, s]
                
                # if cell value contains at least 1 reference
                else:
                    s = perform_ref_ops(formula)
                    return [200, s[1]]
            
        print('ID not found')
        return [404, 0]
    

# delete
def delete(id):
    data = requests.get(f"{url}/cells.json").json()
    path = f"{url}/cells/"
    for k,v in data.items():
        lid = list(v)[0]
        if lid == id:
            path += f"{k}.json"
            res = requests.delete(path)
            if res.status_code == 200:
                return 200
            else:
                return 500
    return 404


reset_db()