from app.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    conn.execute(text("UPDATE customers SET balance = 1000000.00 WHERE username = 'load_tester';"))
    conn.commit()
print("Money injected succesfully!")