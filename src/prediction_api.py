""" API provider for baseball game/event predictions. """
import logging
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

app = FastAPI()

# Setup Logging
logging.basicConfig(level=logging.DEBUG,
    handlers=[
        # no need from a docker container - logging.FileHandler("prediction_api.log"),
        logging.StreamHandler()
    ])

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """ Additional logging for getting extra detail about certain http binding errors. """
    exc_str = f'{exc}'.replace('\n', ' ').replace('   ', ' ')
    logging.error("Request: %s - Exception: %s" , request, exc_str)
    content = {'status_code': 10422, 'message': exc_str, 'data': None}
    return JSONResponse(content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

@app.get("/")
async def root():
    return { "message": "Welcome to the Baseball Prediction Service!" }
