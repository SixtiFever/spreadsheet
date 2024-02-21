import config, pyrebase, operator
from config import firebase_config

firebase = pyrebase.initialize_app(firebase_config)
db = firebase.database()

operator_dict = {'+': operator.add, '-': operator.sub, 'x': operator.mul, '/': operator.truediv, '*': operator.mul}

# create database
if db.child().get().val() == None:
    db.child('cells').push({'test':'test'})


def check_if_cell_exists(id):
    db = firebase.database()
    cells = db.child('cells').get()
    for cell in cells:
        if id in cell.val().keys():
            return True
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
    operands = formula.split(' ')
    # if single reference E.g D4 -> Get and print value
    if len(operands) <= 1:
        return eval(operands[0])
    else:
        # for each reference in operands, obtain the value and replace in-place
        sum = eval(get_cell(operands[0])) if not is_numeric_string(operands[0]) else eval(operands[0])
        o = 1
        r = 2
        for i in range(0, len(operands)):
            if r > len(operands):
                        break
            if is_numeric_string(operands[r]):
                right_val = eval(operands[r])
            else:
                right_val = read(operands[r])
            # right_val = float(cursor.execute("SELECT * FROM cells WHERE id='" + operands[r] + "'").fetchall()[0][1]) if len(cursor.execute("SELECT * FROM cells WHERE id='" + operands[r] + "'").fetchall()) >= 1 else 0 
            op = operator_dict[operands[o]]
            sum = op(sum,right_val)
            o += 2
            r += 2

        return [200, sum]
        # check whether sum is float or integer
        # decimal_part = str(sum).split('.')
        # trailing_val = eval(decimal_part[1])
        # if trailing_val == 0:
        #     return decimal_part[0]
        # else:
        #     return sum

#####  HANDLE ALL ERRORS HERE AND RETURN ERRORS + RESPONSE TO SC.PY



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

        code = 200
        return "Read list"
    
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


