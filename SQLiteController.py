import sqlite3, operator, re
from flask import g

operator_dict = {'+': operator.add, '-': operator.sub, 'x': operator.mul, '/': operator.truediv, '*': operator.mul}

# initialises database and creates table
def init_db():
    conn = sqlite3.connect('sheet.db')
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE cells (id TEXT, formula TEXT DEFAULT '0')")
    conn.commit()
    conn.close()
    print('Table cells created')
    return ""

def clear_table():
    try:

        conn = sqlite3.connect('sheet.db')
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS cells")
        conn.commit()
        print('Table deleted')
    except Exception as e:
        print(e)
    finally:
        conn.close()
    return "Deleted table"

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
    
def perform_reference_ops(formula, cursor):
    """
    performs operations when a cell references another cell
    """
    f = formula
    pattern = re.compile(r'[*+()-/ " " ]') # extract references
    split_list = pattern.split(formula)
    refs = [item for item in split_list if item and not item.isdigit()]

    # replace references with corresponding values
    for id in refs:
        val = cursor.execute("SELECT * FROM cells WHERE id='" + id + "'").fetchall()[0][1]
        res = str(eval(val))
        f = f.replace(id, res)
    sum = eval(f)

    # check whether sum is float or integer
    decimal_part = str(sum).split('.')

    if len(decimal_part) > 1:
        trailing_val = eval(decimal_part[1])
        if trailing_val == 0:
            return decimal_part[0]
        else:
            return sum
    else:
        return sum


# inserts values into the database
def create(id, formula = 0):
    conn = sqlite3.connect('sheet.db')
    cursor = conn.cursor()

    try:
        conn.execute("BEGIN")
        
        # check if cell exists
        cursor.execute("SELECT * FROM cells WHERE id=?", (id,))
        if len(cursor.fetchall()) <= 0:
            # insert new cell
            print('Inserted new cell ' + id)
            cursor.execute("INSERT INTO cells VALUES (?, ?)", (id, formula))
        else:
            # update cell
            print('Updated cell ' + id)
            cursor.execute("UPDATE cells SET formula='"+formula+"' WHERE id='" + id + "'")

        conn.execute("COMMIT")
    except:
        # rollback to previous version if error
        conn.execute("ROLLBACK")
        raise
    finally:
        conn.close()

    return ""


def read(id = 0):

    conn = sqlite3.connect('sheet.db')
    cursor = conn.cursor()
    res = []
    try:
        conn.execute("BEGIN")

        ### LIST ###
        if id == 0:
            cursor.execute("SELECT * FROM cells")
            res += cursor.fetchall()
            return [200, res]

        ### CALCULATE CELL FORMULA ###
        else:
            # read 1 cell
            cursor.execute("SELECT * FROM cells WHERE id=?", (id,))
            result = cursor.fetchall()
            # if cell doesn't exist, print 0 and return
            if len(result) <= 0:
                return [404]

            formula = result[0][1]
            # check whether cell is value or contains at least one reference
            if is_numeric_string(formula):
                # is numeric -> Read value
                try:
                    print(eval(formula))
                    return eval(formula),200
                except Exception as e:
                    return e
                
            else:
                # contains at least 1 reference
                print('Enter ref ops')
                total = perform_reference_ops(formula, cursor)
            conn.execute("COMMIT")
            return [200, total]
        
    except Exception as e:
        print(e)
        conn.execute("ROLLBACK")
        return [500]
    finally:
        conn.close()


def update(id, formula):
    return ""


def delete(id):
    return ""
