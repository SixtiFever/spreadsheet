import sqlite3, operator, re

operator_dict = {'+': operator.add, '-': operator.sub, 'x': operator.mul, '/': operator.truediv, '*': operator.mul}

# initialises database and creates table
def init_db():
    conn = sqlite3.connect('sheet.db')
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE cells (id TEXT, formula TEXT DEFAULT '0')")
    conn.commit()
    conn.close()
    return ""

def clear_table():
    try:

        conn = sqlite3.connect('sheet.db')
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS cells")
        conn.commit()
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



### OPERATIONS ###


# inserts values into the database
def create(id, formula = 0):
    conn = sqlite3.connect('sheet.db')
    cursor = conn.cursor()
    code = 0
    try:
        conn.execute("BEGIN")
        
        # check if cell exists
        cursor.execute("SELECT * FROM cells WHERE id=?", (id,))
        if len(cursor.fetchall()) <= 0:
            # insert new cell
            cursor.execute("INSERT INTO cells VALUES (?, ?)", (id, formula))
            code = 201
        else:
            # update cell
            cursor.execute("UPDATE cells SET formula='"+formula+"' WHERE id='" + id + "'")
            code = 204
        conn.execute("COMMIT")
    except:
        # rollback to previous version if error
        conn.execute("ROLLBACK")
        raise
    finally:
        conn.close()

    return code


def read(id = 0):
    """
    reads from the spreadsheet. Returns 404 is cell id doesn't exist.
    200 if successfull. 500 if there is an internal service error.
    """

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
                    return eval(formula),200
                except Exception as e:
                    return e
                
            else:

                string_formula = formula

                def recurse_formulas(formula):
                    """
                    deal with references recursively
                    """

                    # base case -> When formulais calculatable i.e contains no references
                    if is_numeric_string(formula):
                        s = eval(formula)
                        return float(s)
                    
                    else:
                        # keep resursing
                        f = formula
                        pattern = re.compile(r'[*+()-/ " " ]') # extract references
                        split_list = pattern.split(formula)
                        refs = [item for item in split_list if item and not item.isdigit()]
                        for id in refs:
                            cursor.execute("SELECT * FROM cells WHERE id=?", (id,))
                            result = cursor.fetchall()
                            formula = '0' if len(result) <= 0 else result[0][1] # 
                            val = formula if not is_numeric_string(formula) else eval(formula)
                            f = f.replace(id, str(val))
                        return recurse_formulas(f)
                    
                s = recurse_formulas(string_formula)

                result = remove_trailing_zeros(s)  
                conn.execute("COMMIT")
                return [200, result]
        
    except Exception as e:
        print(e)
        conn.execute("ROLLBACK")
        return [500]
    finally:
        conn.close()


def delete(id):

    conn = sqlite3.connect('sheet.db')
    cursor = conn.cursor()
    cell_present = False
    
    try:
        conn.execute("BEGIN")
        c = cursor.execute("SELECT * FROM cells WHERE id='" + id + "'")
        if len(c.fetchall()) >= 1:
            cursor.execute("DELETE FROM cells WHERE id='" + id + "'")
            cell_present = True
        conn.execute("COMMIT")
    except Exception as e:
        print(e)
        conn.execute("ROLLBACK")
        return 404
    finally:
        conn.close()

    return 200 if cell_present else 404
