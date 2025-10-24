from fastapi import FastAPI
from fastapi.responses import Response
import uvicorn
import logging

from api.database import engine
from api.models import DecBase
from api.routers.show import router as shows_router
from api.routers.session import router as sessions_router

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s"
)

logger = logging.getLogger(__name__)


app = FastAPI()
app.include_router(shows_router)
app.include_router(sessions_router)

DecBase.metadata.create_all(bind=engine)


@app.get("/")
def index():
    logger.info("App launched!")
    return Response({"msg": "This is the SHOWS api"})


if __name__ == "__main__":
    uvicorn.run("api.main:app", host="localhost", port=8000)