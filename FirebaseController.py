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
    """
    determines whether the input string formula is directly 
    calculatable i.e contains a reference or not
    """
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
    """
    returns the contents of the cell with the given id
    """
    data = requests.get(f"{url}/cells.json").json()
    for record in data.values():
        lid = list(record.keys())[0]
        if id == lid:
            formula = list(record.values())[0]
            return formula
        
    # if id not found, return 0
    return '0'

def check_cell_exists(id):
    """
    checks whether a cell with the given id exists
    """
    data = requests.get(f"{url}/cells.json").json()
    for record in data.values():
        lid = list(record.keys())[0]
        if id == lid:
            return True
    return False

def remove_trailing_zeros(sum):
    """
    function to safeguard against trailing zeros, 
    just in case in correct format is returned.
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
    """
    updated the formula of the given cell
    """
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
    """
    Creates or updates the spreadsheet with the given id and formula.
    If either cell id or formula is invalid or not enteres, code 400 is returned
    representing a bad request
    """

    code = 0

    # check if request is valid
    if is_numeric_string(id) or formula == 0 or id == 0:
        print('Bad Request')
        return 400,""
    
    # check whether cell already exists to establish whether to perform
    # and update or create a new cell
    cell_exists = check_cell_exists(id)
    data = {id : formula}

    if cell_exists:
        # perform update and assign 204
        res = perform_formula_update(id, formula)
        code = 204
        print(res)
    else:
        # create new cell and assign 201
        res = requests.post(f"{url}/cells.json", json=data)
        code = 201

    return code

    

def read(id = 0):
    """
    reads the cell of the given id from the firebase database. 
    If no id is given, reads the entire contents of the spreadsheet.
    """

    # get all database contents
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
                    calculate formula with references via recursion
                    """

                    # base case -> when input formula is calculatable i.e contains no references
                    if is_numeric_string(formula):
                        s = eval(formula)
                        return float(s)
                    
                    else:
                        # recursve
                        f = formula
                        pattern = re.compile(r'[*+()-/ " " ]')
                        split_list = pattern.split(formula) # split formula by operators to extract references
                        refs = [item for item in split_list if item and not item.isdigit()] # assign list of formula references

                        # iterate references, replacing the ref ID in the original string with 
                        # the content of the references which is either calcultable via eval() or is
                        # another reference
                        for id in refs:
                            id_formula = get_formula_by_id(id)
                            val = id_formula if not is_numeric_string(id_formula) else eval(id_formula)
                            f = f.replace(id, str(val))
                        # pass the updated formula as the argument of the recursion    
                        return recurse_formulas(f)

                s = recurse_formulas(string_formula)  # calculate formulas recursively
                result = remove_trailing_zeros(s)  # remove unecessary trailing 0s
                return [200, result]

            
        print('ID not found')
        return [404, 0]
    

# delete
def delete(id):
    """
    deletes the cell of the given id if present
    """
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
