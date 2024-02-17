import sqlite3
from flask import g

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
            cursor.execute("INSERT INTO cells VALUES (?, ?)", (id, formula))
        else:
            print('Cell ' + id + ' already exists')

        conn.execute("COMMIT")
    except:
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
            # read all cells
            cursor.execute("SELECT * FROM cells")
            print(cursor.fetchall())
        else:
            # read 1 cell
            cursor.execute("SELECT * FROM cells WHERE id=?", (id,))
            result = cursor.fetchall()
            formula = result[0][1]

            # check whether cell is value or a reference to other cell(s)
            if is_numeric_string(formula):
                # is numeric -> Read value
                print(formula)
            else:
                # is a reference -> Perform operations
                print('ref')

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


create('D5', '33.7')
read('A1')

