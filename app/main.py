from fastapi import FastAPI
from app import models
from app.database import engine

# 1. The Spark: This is the inception of the 'zorvyn.db' file by building
# all the tables based of the 'models.py' file
models.Base.metadata.create_all(bind=engine)

# 2. The Engine: Initializing the FastAPI Application
app = FastAPI(
    title="Zorvyn Finance API",
    description="Backedn screening assessment for Zorvyn FinTech",
    version="1.0.0",
)

# 3. A quick health check route to check how the server is doing
@app.get("/")
def read_root():
    return {"status": "Zorvyn API Vault is Online & Healthy!"}