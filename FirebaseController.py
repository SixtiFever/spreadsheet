import config, pyrebase, operator, re
from config import firebase_config

firebase = pyrebase.initialize_app(firebase_config)
db = firebase.database()

operator_dict = {'+': operator.add, '-': operator.sub, 'x': operator.mul, '/': operator.truediv, '*': operator.mul}

def reset_db():
    db = firebase.database()
    db.child('cells').remove()
    db.child('cells').push({'^^': '^^'})

def check_if_cell_exists(id):
    db = firebase.database()
    cells = db.child('cells').get()
    for cell in cells:
        if id in cell.val().keys():
            return True
    return False

def check_if_cells_object_exists():
    try:
        db = firebase.database()
        db.child('cells').get()
        return True
    except Exception as e:
        print(e)
        return False

def get_cell(id):
    db = firebase.database()
    cells = db.child('cells').get()
    for cell in cells:
        if id in cell.val().keys():
            return cell.val()[id]
    return {}

def update_cell(db, id, data):
    cells = db.child("cells").get()
    for cell in cells:
        if id in cell.val().keys():
            cell_id = cell.key()
            db.child('cells').child(cell_id).update(data)
            print('Cell updated')
            return
    print('cell not found')
    return ""

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


def perform_ref_ops(formula):
    db = firebase.database()
    f = formula
    pattern = re.compile(r'[*+()-/ " " ]') # extract references
    split_list = pattern.split(formula)
    refs = [item for item in split_list if item and not item.isdigit()]

    # replace references with corresponding values
    for id in refs:
        val = get_cell(id)
        res = eval(val)
        print(res)
        f = f.replace(id, str(res))
    sum = eval(f)
    return [200, sum]



# create
def create(id = 0, formula = 0):
    db = firebase.database()

    code = 0 # assign response code

    # check if cell ID is valid
    if is_numeric_string(id) or formula == 0 or id == 0:
        print('Invalid input')
        return 400,""
    
    # check if formula is numeric or a reference
    is_numeric = is_numeric_string(formula)
    if is_numeric:
        code = 201
    else:
        # if formula is a reference
        code = 204

    cell_exists = check_if_cell_exists(id)
    data = {id : formula}
    if cell_exists:
        print('Cell exists... Perform update')
        update_cell(db, id, data)
    else:
        print('Creating new cell')
        db.child('cells').push(data)
    return code


# read
def read(id = 0):

    db = firebase.database()
    code = 0

    if is_numeric_string(id):
        print('invalid id')
        return [404,0]
    
    if id == 0:
        # reading list
        cells = db.child('cells').get()
        ids = []
        for cell in cells:
            key = list(cell.val().keys())
            ids.append(key[0])
        return ids,200
    
    else:
        # if valid cell id, read cell
        if check_if_cell_exists(id):
            formula = get_cell(id)
            if is_numeric_string(formula):
                val = eval(formula)
                return val
            else:
                print('is a reference')
                sum = perform_ref_ops(formula)
                return sum
        else:
            return [400,0]
    

# list

# delete


