import requests, re, os

url = os.environ['FBASE']

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
    """
    safeguarding against unecessary trailing zeros
    """
    
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
                return 200
            else:
                print('update error')
                return 500



## CRUD OPERATIONS ###

# create
def create(id = 0, formula = 0):

    code = 0

    # check if request is valid is valid
    if is_numeric_string(id) or formula == 0 or id == 0:
        print('Bad Request')
        return 400,""
    
    cell_exists = check_cell_exists(id)
    data = {id : formula}
    if cell_exists:
        res = perform_formula_update(id, formula)
        code = 204
        print(res)
    else:
        res = requests.post(f"{url}/cells.json", json=data)
        code = 201
    return code

    

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
                        s = eval(formula)
                        return float(s)
                    
                    else:
                        # keep rec ursing
                        f = formula
                        pattern = re.compile(r'[*+()-/ " " ]') # extract references
                        split_list = pattern.split(formula)
                        refs = [item for item in split_list if item and not item.isdigit()]
                        for id in refs:
                            id_formula = get_formula_by_id(id)
                            val = id_formula if not is_numeric_string(id_formula) else eval(id_formula)
                            f = f.replace(id, str(val))
                        return recurse_formulas(f)

                s = recurse_formulas(string_formula)  # calculate formulas recursively
                result = remove_trailing_zeros(s)  # remove unecessary trailing 0s
                return [200, result]

            
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
