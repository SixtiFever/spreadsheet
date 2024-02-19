import sqlite3
from flask import g
import operator

operator_dict = {'+': operator.add, '-': operator.sub, 'x': operator.mul, '/': operator.truediv, '*': operator.mul}

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
    # is a reference -> Perform operations
    operands = formula.split(' ')
    # if single reference E.g D4 -> Get and print value
    if len(operands) <= 1:
        res = cursor.execute("SELECT * FROM cells WHERE id='" + operands[0] + "'")
        val = res.fetchall()[0][1] # obtain value
        return val
    else:
        # for each reference in operands, obtain the value and replace in-place
        sum = float(cursor.execute("SELECT * FROM cells WHERE id='" + operands[0] + "'").fetchall()[0][1]) if len(cursor.execute("SELECT * FROM cells WHERE id='" + operands[0] + "'").fetchall()) >= 1 else 0 
        o = 1
        r = 2
        for i in range(0, len(operands)):
            if r > len(operands):
                        break
            right_val = read(operands[r])
            # right_val = float(cursor.execute("SELECT * FROM cells WHERE id='" + operands[r] + "'").fetchall()[0][1]) if len(cursor.execute("SELECT * FROM cells WHERE id='" + operands[r] + "'").fetchall()) >= 1 else 0 
            op = operator_dict[operands[o]]
            sum = op(sum,right_val)
            o += 2
            r += 2

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
        
        if id == 0:
            # list all cells
            cursor.execute("SELECT * FROM cells")
            res += cursor.fetchall()
            return res

        else:
            # read 1 cell
            cursor.execute("SELECT * FROM cells WHERE id=?", (id,))
            result = cursor.fetchall()
            # if cell doesn't exist, print 0 and return
            if len(result) <= 0:
                return 404
            
            formula = result[0][1]

            # check whether cell is value or a reference to other cell(s)
            if is_numeric_string(formula):
                # is numeric -> Read value
                try:
                    return eval(formula)
                except Exception as e:
                    return e
                
            else:
                # is a reference -> perform operations on the formula
                total = perform_reference_ops(formula, cursor)
                print(total)
            return 200
        
    except Exception as e:
        conn.execute("ROLLBACK")
        conn.close()
        return 500
    finally:
        conn.execute("COMMIT")
        conn.close()


def update(id, formula):
    return ""


def delete(id):
    return ""

