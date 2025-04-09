__name__ = "CI/CD Demo App"
__version__ = "1.0.0"
__author__ = "David Martínez García"
__credits__ = ["GIROS DIT-UPM", "David Martínez García"]

## -- BEGIN IMPORT STATEMENTS -- ##

from contextlib import asynccontextmanager
from datetime import datetime, timezone
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
import logging
from pydantic import BaseModel

## -- END IMPORT STATEMENTS -- ##

## -- BEGIN DEFINITION OF PYDANTIC MODELS -- ##

class GetHelloResponse(BaseModel):
    who: str
    where: int
    when: str
    message: str

## -- END DEFINITION OF PYDANTIC MODELS -- ##

## -- BEGIN LOGGING CONFIGURATION -- ##

logger = logging.getLogger(__name__)
logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.DEBUG,
    datefmt='%Y-%m-%d %H:%M:%S')

## -- END LOGGING CONFIGURATION -- ##

## -- BEGIN DEFINITION OF AUXILIARY FUNCTIONS AND VARIABLES -- ##

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application started")

    yield

    logger.info("Application finished")

## -- END DEFINITION OF AUXILIARY FUNCTIONS -- ##

## -- BEGIN MAIN CODE -- ##

app = FastAPI(
    lifespan=lifespan,
    title=__name__ + " - REST API",
    version=__version__
)

@app.get(path = "/hello",
         description = "Retrieve greeting.",
         tags = ["Default"],
         responses = {
             status.HTTP_200_OK: {
                 "model": GetHelloResponse
             }
         }
)
async def get_hello(request: Request):
    '''
    FastAPI request handler function: HTTP GET /hello.
    '''

    logger.info("Received HTTP GET request from " + request.client.host + ":" + str(request.client.port) + " to /hello")

    output = {
        "who": request.client.host,
        "where": request.client.port,
        "when": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "message": "Hello"
    }

    return JSONResponse(status_code = status.HTTP_200_OK, content = output)

## -- END MAIN CODE -- ##
