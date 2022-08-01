import pydantic as _pyndantic
import datetime as _datetime

class UserBase(_pyndantic.BaseModel):
    email: str
    name: str
    phone: str

class UserRequest(UserBase):
    password: str

    class Config:
        orm_mode = True

class UserResponse(UserBase):
    id: int
    created_at: _datetime.datetime

    class Config:
        orm_mode = True


class addressBase(_pyndantic.BaseModel):
    x: float
    y: float

class addressRequest(addressBase):
    pass

class addressResponse(addressBase):
    id: int
    user_id: int
    created_at: _datetime.datetime

    class Config:
        orm_mode = True