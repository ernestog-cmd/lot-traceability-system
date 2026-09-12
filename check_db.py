import sqlite3
conn = sqlite3.connect('lots.db')
cursor = conn.cursor()
print("alembic:", cursor.execute('SELECT * FROM alembic_version').fetchall())
print("tablas:", cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall())
print("part_numbers:", cursor.execute('PRAGMA table_info(part_numbers)').fetchall())
print("lots:", cursor.execute('PRAGMA table_info(lots)').fetchall())
conn.close()