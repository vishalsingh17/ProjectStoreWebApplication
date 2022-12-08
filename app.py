from fastapi import FastAPI
from starlette.responses import RedirectResponse
from starlette import status
from starlette.staticfiles import StaticFiles
import uvicorn

from project_store_data_access_layer.data_access import prepare_db
from project_store_entity_layer import entity as models
from project_store_routers_layer import auth, applications
from project_store_config_layer.configuration import Configuration

app = FastAPI()

engine, _, _ = prepare_db()
models.Base.metadata.create_all(bind=engine)

app.mount("/static", StaticFiles(directory=Configuration().STATIC_DIR), name="static")

@app.get("/")
async def root():
    return RedirectResponse("/application", status_code=status.HTTP_302_FOUND)
app.include_router(auth.router)
app.include_router(applications.router)

if __name__ == "__main__":
    uvicorn.run(app)

