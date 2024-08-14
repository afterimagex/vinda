import functools

from vinda.api import schemas
from loguru import logger
from traceback import format_exception
from fastapi import HTTPException


class SingletonBase(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonBase, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


def response_handle(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        response = schemas.Response()
        try:
            response.data = await func(*args, **kwargs)
            return response.model_dump()
        except Exception as e:
            response.code = -1
            response.message = str(e)
            response.traceback = format_exception(e)
            logger.error(response)
            raise HTTPException(status_code=500, detail=response.message)
            # return response
    return wrapper