from app.database import engine
from sqlalchemy import text

def wipe_database():
    with engine.connect() as conn:
        # Obliterating the hidden Alembic history table
        conn.execute(text("DROP TABLE IF EXISTS alembic_version CASCADE"))

        # Obliterating any old tables to guarantee a true blank slate
        conn.execute(text("DROP TABLE IF EXISTS records CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS employees CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS customers CASCADE"))

        conn.commit()
    print("SUCCESS: Ghost tables forcefully dropped from the inside!")

if __name__=="__main__":
    wipe_database()