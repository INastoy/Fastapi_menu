from pydantic import BaseModel


class BaseMessage(BaseModel):
    error: str


class Message303(BaseMessage):
    error: str = 'Already exists'


class Message404(BaseMessage):
    error: str = 'Item not found'


class Message401(BaseMessage):
    error: str = 'Incorrect username or password'


RESPONSE_303 = {303: {'model': Message303, 'description': 'See Other'}}

RESPONSE_401 = {401: {'model': Message401, 'description': 'Unauthorized'}}
RESPONSE_404 = {404: {'model': Message404, 'description': 'Not found'}}
