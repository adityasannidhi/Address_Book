import fastapi as _fastapi
import fastapi.security as _security
import sqlalchemy.orm as _orm
from typing import List
import schemas as _schemas
import services as _services

from fastapi.middleware.cors import CORSMiddleware

app = _fastapi.FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_headers=['*'],
    allow_methods=['*']
)

@app.post("/api/v1/users")
async def register_user(
        user: _schemas.UserRequest, db: _orm.session = _fastapi.Depends(_services.get_db)
):
    # call to check if user with email exists
    db_user = await _services.getUserByEmail(email=user.email,db=db)
    # if user found, throw exception
    if db_user:
        raise _fastapi.HTTPException(status_code=400, detail="Email already exist, try with another email!")

    # create the user and return a token
    db_user = await _services.create_user(user=user, db=db)
    return await _services.create_token(user=db_user)

@app.post("/api/v1/login")
async def login_user(
        form_data: _security.OAuth2PasswordRequestForm = _fastapi.Depends(),
        db: _orm.session = _fastapi.Depends(_services.get_db)
):
    db_user = await _services.login(email=form_data.username, password=form_data.password, db=db)

    # INVALID LOGIN THEN THROW EXCEPTION
    if not db_user:
        raise _fastapi.HTTPException(status_code=401, detail="Wrong Login Credentials!")
    # CREATE AND RETURN THE TOKEN
    return await _services.create_token(db_user)

@app.get("/api/v1/users/current-user", response_model=_schemas.UserResponse)
async def current_user(user: _schemas.UserResponse = _fastapi.Depends(_services.current_user)):
    return user

@app.post("/api/v1/addresss", response_model=_schemas.addressResponse)
async def create_address(
        address_request: _schemas.addressRequest,
        db: _orm.Session = _fastapi.Depends(_services.get_db),
        user:_schemas.UserRequest = _fastapi.Depends(_services.current_user)
):
    return await _services.create_address(user=user,db=db,address=address_request)

@app.get("/api/v1/addresss/user", response_model=List[_schemas.addressResponse])
async def get_addresss_by_user(
        db: _orm.Session = _fastapi.Depends(_services.get_db),
        user:_schemas.UserRequest = _fastapi.Depends(_services.current_user)
):
    return await _services.get_addresss_by_user(user=user,db=db)

@app.get("/api/v1/addresss/all", response_model=List[_schemas.addressResponse])
async def get_addresss_by_all(
        db: _orm.Session = _fastapi.Depends(_services.get_db)
):
    return await _services.get_addresss_by_all(db=db)

@app.get("/api/v1/addresss/{address_id}/",response_model=_schemas.addressResponse)
async def get_address_detail(
        address_id: int, db: _orm.session = _fastapi.Depends(_services.get_db)
):
    address = await _services.get_address_detail(address_id=address_id,db=db)
    return  address

@app.get("/api/v1/addresss/{coordinates}/",response_model=_schemas.addressResponse)
async def get_address_detail(
        coordinates_x: int,coordinates_y: int, db: _orm.session = _fastapi.Depends(_services.get_db)
):
    address = await _services.retrieve_address(coordinates_x=coordinates_x,coordinates_y=coordinates_y,db=db)
    return  address

@app.get("/api/v1/users/{user_id}/",response_model=_schemas.UserResponse)
async def get_user_detail(
        user_id: int, db: _orm.session = _fastapi.Depends(_services.get_db)
):
    return  await _services.get_user_detail(user_id=user_id,db=db)

@app.delete("/api/v1/addresss/{address_id}/")
async def delete_address(
        address_id: int,
        db: _orm.session = _fastapi.Depends(_services.get_db),
        user: _schemas.UserRequest = _fastapi.Depends(_services.current_user)
):
    address = await _services.get_address_detail(address_id=address_id,db=db)
    await _services.delete_address(address=address,db=db)

    return "address deleted Successfully"


@app.put("/api/v1/users/{address_id}/",response_model=_schemas.addressResponse)
async def update_address(
        address_id: int,
        address_request: _schemas.addressRequest,
        db: _orm.session = _fastapi.Depends(_services.get_db)
):
    db_address = await _services.get_address_detail(address_id=address_id,db=db)

    return await _services.update_address(address_request=address_request,address=db_address,db=db)

