from flask import Flask, request
import sqlite3

app = Flask(__name__)

# initialise database
conn = sqlite3.connect('sheet.db')
csr = conn.cursor()
csr.execute("CREATE TABLE IF NOT EXISTS cells (id TEXT, formula TEXT)")
conn.commit()
conn.close()

@app.route('/cells', methods=['PUT'])
def create():
    js = request.get_json()  # get json of PUT request
    id = js.get("id")  # cell id
    formula = js.get("formula")  # cell formula

    if id != None:

        conn = sqlite3.connect('sheet.db')
        csr = conn.cursor()
        result = csr.execute("SELECT * FROM cells WHERE id='"+id+"'")
        # if id already exists in database -> Override it
        if result:
            csr.execute("UPDATE cells SET formula = ? WHERE id = ?", (formula, id))
        else:
            # if doesn't already exist -> Create new cell
            csr.execute("INSERT INTO cells VALUES (?, ?)", (id, formula))
            
        csr.execute("SELECT * FROM cells")
        rows = csr.fetchall()
        print(rows)
        conn.commit()
        conn.close()
        return "Home" # OK
    else:
        return "",400 # Bad Request





# def index():

#     # create table on load
#     conn = sqlite3.connect('sheet.db')
#     cursor = conn.cursor()
#     cursor.execute('CREATE TABLE IF NOT EXISTS cells(id TEXT, formula TEXT)')

#     create_cell(cursor, 'D7', '29')
#     print_all(cursor)
#     return (
#         "Home"
#     )


# def create_cell(cursor, id, val):
#    cursor.execute("INSERT INTO cells VALUES ('" + id + "','" + val + "')")

# def print_all(cursor):
#     cursor.execute("SELECT * FROM cells")
#     print(cursor.fetchall())




if __name__ == '__main__':
    app.run(host='localhost', port=3000, debug=True)