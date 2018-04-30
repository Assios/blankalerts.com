import sqlite3 as sql

con = sql.connect("./database.db")
cur = con.cursor()
email = "asbjorn@steinskog.me"
tok = "jada"
cur.execute("INSERT INTO emails (email, token) VALUES (?,?)", (email, tok))
con.commit()
cur.close()
