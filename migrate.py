import sqlite3

conn = sqlite3.connect('lots.db')
cursor = conn.cursor()

cursor.execute("ALTER TABLE users ADD COLUMN is_active VARCHAR NOT NULL DEFAULT 'true'")
cursor.execute("UPDATE alembic_version SET version_num = 'a1b2c3d4e5f6'")

conn.commit()
conn.close()
print("Done")