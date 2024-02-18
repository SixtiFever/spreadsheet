import sqlite3
from flask import g
import operator

operator_dict = {'+': operator.add, '-': operator.sub, 'x': operator.mul, '/': operator.truediv}

# initialises database and creates table
def init_db():
    conn = sqlite3.connect('sheet.db')
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS cells (id TEXT, formula TEXT DEFAULT '0')")
    conn.commit()
    conn.close()
    return ""

def is_numeric_string(formula):
    try:
        # Try converting the string to an integer using int()
        float_val = float(formula)
        return True
    except ValueError:
        # If ValueError occurs, it means the string cannot be cast to an integer
        return False
    
def perform_reference_ops(formula, cursor):
    """
    performs operations when a cell references another cell
    """
    # is a reference -> Perform operations
    operands = formula.split(' ')
    # if single reference E.g D4 -> Get and print value
    if len(operands) <= 1:
        res = cursor.execute("SELECT * FROM cells WHERE id='" + operands[0] + "'")
        val = res.fetchall()[0][1] # obtain calue of cell id
        print(id + ': '+ val)
    else:
        print(operands)
        # for each reference in operands, obtain the value and replace in-place
        sum = float(cursor.execute("SELECT * FROM cells WHERE id='" + operands[0] + "'").fetchall()[0][1]) if len(cursor.execute("SELECT * FROM cells WHERE id='" + operands[0] + "'").fetchall()) >= 1 else 0 
        o = 1
        r = 2
        for i in range(0, len(operands)):
            if r > len(operands):
                        break
            right_val = float(cursor.execute("SELECT * FROM cells WHERE id='" + operands[r] + "'").fetchall()[0][1]) if len(cursor.execute("SELECT * FROM cells WHERE id='" + operands[r] + "'").fetchall()) >= 1 else 0 
            print(right_val)
            op = operator_dict[operands[o]]
            sum = op(sum,right_val)
            o += 2
            r += 2
        print(sum)
    





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

    try:
        conn.execute("BEGIN")
        
        if id == 0:
            # list all cells
            cursor.execute("SELECT * FROM cells")
            print(cursor.fetchall())

        else:
            # read 1 cell
            cursor.execute("SELECT * FROM cells WHERE id=?", (id,))
            result = cursor.fetchall()
            # if cell doesn't exist, print 0 and return
            if len(result) <= 0:
                print(0)
                return
            
            formula = result[0][1]

            # check whether cell is value or a reference to other cell(s)
            if is_numeric_string(formula):
                # is numeric -> Read value
                print(formula)
             

            else:
                # is a reference -> perform operations on the formula
                perform_reference_ops(formula, cursor)

        conn.execute("COMMIT")
    except:
        conn.execute("ROLLBACK")
        raise
    finally:
        conn.close()

    return ""


def update(id, formula):
    return ""


def delete(id):
    return ""


create('D6', 'A1 + A2 - A3 x A4 / A1')
read('D6')

