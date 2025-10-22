from fastapi import FastAPI
from fastapi.responses import Response
import uvicorn

from api.database import engine
from api.models import DecBase
from api.routers.show import router as shows_router
from api.routers.session import router as sessions_router

app = FastAPI()
app.include_router(shows_router)
app.include_router(sessions_router)

DecBase.metadata.create_all(bind=engine)


@app.get("/")
def index():
    return Response({"msg": "This is the SHOWS api"})


if __name__ == "__main__":
    uvicorn.run("api.main:app", host="localhost", port=8000)