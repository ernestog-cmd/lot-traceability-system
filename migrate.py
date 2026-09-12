import sqlite3

conn = sqlite3.connect('lots.db')
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS product_families (
    name VARCHAR NOT NULL,
    status VARCHAR NOT NULL,
    proposed_by VARCHAR NOT NULL,
    approved_by VARCHAR,
    PRIMARY KEY (name)
)
""")

cursor.execute("UPDATE alembic_version SET version_num = '1369334eeb8c'")

conn.commit()
conn.close()
print("Done")