<<<<<<< HEAD
import sqlite3

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
               ("admin", "admin123", "admin"))

conn.commit()
conn.close()

=======
import sqlite3

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
               ("admin", "admin123", "admin"))

conn.commit()
conn.close()

>>>>>>> 787dd367c657a4b2ee84f2d01e270a7c27ede54b
print("Admin Added")