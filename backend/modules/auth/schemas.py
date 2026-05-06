from pydantic import BaseModel, Field

from backend.modules.users.schemas import UserOut

class RequestCodeIn(BaseModel):
    phone:str=Field(..., examples=["83999157461"],)
class RequestCodeOut(BaseModel):
    message:str
class VerifyCodeIn(BaseModel):
    phone:str=Field(..., examples=["83999157461"],)
    code:str=Field(..., min_length=6, max_length=6, examples=["555666"],)
class TokenOut(BaseModel):
    access_token:str
    token_type:str="bearer"
    user: UserOut