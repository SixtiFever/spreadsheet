from flask import Flask, request, jsonify
import requests, re
from config import firebase_url

url = firebase_url

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

def remove_trailing_zeros(sum):
     # check whether sum is float or integer
    
    decimal_part = str(sum).split('.')  # create list about the decimal

    if len(decimal_part) > 1:
        trailing_val = eval(decimal_part[1])
        if trailing_val == 0:
            return decimal_part[0]
        else:
            return sum
    else:
        return sum


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
# def read(id = 0):
#     """
#     reads from the firebase database
#     """

#     data = requests.get(f"{url}/cells.json").json()

#     # if cell id is invalid
#     if is_numeric_string(id):
#         print('invalid id')
#         return [404,0]

#     # print list if not id is given
#     if id == 0:
#         ids = []
#         for record in data.values():
#             lid = list(record.keys())[0]
#             ids.append(lid)
#         return ids,200
#     else:

#         for record in data.values():
#             lid = list(record.keys())[0]
#             if lid == id:
#                 # perform calculation
#                 formula = list(record.values())[0]

#                 # if cell value can be calculated directly i.e is numeric
#                 if is_numeric_string(formula):
#                     s = eval(formula)
#                     print(s)
#                     return [200, s]
                
#                 # if cell value contains at least 1 reference
#                 else:
#                     s = perform_ref_ops(formula)
#                     return [200, s[1]]
            
#         print('ID not found')
#         return [404, 0]
    

def read(id = 0):
    """
    reads from the firebase database
    """

    data = requests.get(f"{url}/cells.json").json()

    # if cell id is invalid
    if is_numeric_string(id):
        print('invalid id')
        return [404,0]

    # if no id is passed to function, return list
    if id == 0:
        ids = []
        for record in data.values():
            lid = list(record.keys())[0]
            ids.append(lid)
        return ids,200
    else:

        # find cell in spreadsheet
        for record in data.values():
            lid = list(record.keys())[0]

            # cell found
            if lid == id:
                string_formula = str(list(record.values())[0])

                def recurse_formulas(formula):
                    """
                    deal with references recursively
                    """

                    # base case -> When formulais calculatable i.e contains no references
                    if is_numeric_string(formula):
                        print('Final formula: ' + formula)
                        s = eval(formula)
                        return float(s)
                    
                    else:
                        # keep resursing
                        f = formula
                        pattern = re.compile(r'[*+()-/ " " ]') # extract references
                        split_list = pattern.split(formula)
                        refs = [item for item in split_list if item and not item.isdigit()]
                        for id in refs:
                            val = "(" + get_formula_by_id(id) + ")"
                            f = f.replace(id, val)
                        return recurse_formulas(f)

                s = recurse_formulas(string_formula)  # calculate formulas recursively
                result = remove_trailing_zeros(s)  # remove unecessary trailing 0s
                return [200, result]
                # deal with trailing 0's ???

            
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

# create('B1', '3 * 8')
# create('B2', 'A1 / 4 + B1')
# create('A1', '5 * 7')
# create('D4', 'A1 * B1 - B2')
# create('G1', 'G2 + G3 + 10 + D4 + Z1')
# create('G2', '10 + 10')
# create('G3', '2 + (3 * G4)')
# create('G4', '2')
# create('G1', 'G2 + G3 + 10 + D4 + Z1')
# create('Z1', 'Z2')
# create('Z2', 'Z3')
# create('Z3', 'Z4')
# create('Z4', 'Z5')
# create('Z5', 'Z6')
# create('Z6', '0.75')

# read('G1')
