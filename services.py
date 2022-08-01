import database as _database
import models as _models
import fastapi.security as _security
import sqlalchemy.orm as _orm
import schemas as _schemas
import email_validator as _email_validator
import fastapi as _fastapi
import passlib.hash as _hash
import jwt as _jwt

_JWT_SECRET = "asdfghjklqwertyuiopzxcvbnm"
oauth2schema = _security.OAuth2PasswordBearer("/api/v1/login")

def create_db():
    return _database.Base.metadata.create_all(bind=_database.engine)

def get_db():
    db = _database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def getUserByEmail(email: str, db: _orm.session):
    return db.query(_models.UserModel).filter(_models.UserModel.email == email).first()

async def create_user(user: _schemas.UserRequest, db: _orm.session):
    # check valid email
    try:
        isValid = _email_validator.validate_email(email=user.email)
        email = isValid.email
    except _email_validator.EmailNotValidError:
        raise _fastapi.HTTPException(status_code=400, detail="Email not valid!")

    # convert normal password to hash form
    hashed_password = _hash.bcrypt.hash(user.password)

    # create the user model to be saved in database
    user_obj = _models.UserModel(
        email=email,
        name=user.name,
        phone=user.phone,
        password_hash=hashed_password
    )

    #save the user in the db
    db.add(user_obj)
    db.commit()
    db.refresh(user_obj)
    return user_obj

async def create_token(user: _models.UserModel):
    #convert user model to user schema
    user_schema = _schemas.UserResponse.from_orm(user)
    #convert obj to dictionary
    user_dict = user_schema.dict()
    del user_dict["created_at"]

    token = _jwt.encode(user_dict, _JWT_SECRET)

    return dict(access_token=token, token_type="bearer")

async def login(email: str, password: str, db: _orm.session):
    db_user = await getUserByEmail(email=email, db=db)

    # RETURN FALSE IF NO USER WITH EMAIL FOUND
    if not db_user:
        return False

    #RETURN FALSE IF NO USER WITH PASSWORD FOUND
    if not db_user.password_verification(password=password):
        return False

    return db_user

async def current_user(db: _orm.Session = _fastapi.Depends((get_db)),
                       token: str = _fastapi.Depends(oauth2schema)):
    try:
        payload = _jwt.decode(token, _JWT_SECRET, algorithms=["HS256"])
        #Get user by Id and Id is already abaialbale in the decoded user payload along with email,phone and name
        db_user = db.query(_models.UserModel).get(payload["id"])
    except:
        raise _fastapi.HTTPException(status_code=401,detail="Wrong User Credentials")

    #if all okay then return the DTO/Schema version User
    return _schemas.UserResponse.from_orm(db_user)

async def create_address(user:_schemas.UserResponse,db:_orm.session,address:_schemas.addressRequest):
    address = _models.addressModel(**address.dict(),user_id=user.id)
    db.add(address)
    db.commit()
    db.refresh(address)

    #convert the address model to address DTO/Schema and return to API layer
    return _schemas.addressResponse.from_orm(address)

async def get_addresss_by_user(user: _schemas.UserResponse, db: _orm.session):
    addresss = db.query(_models.addressModel).filter_by(user_id=user.id)

    #convert each address models to address schema and make a list to be returned
    return list(map(_schemas.addressResponse.from_orm, addresss))

async def get_addresss_by_all(db: _orm.session):
    addresss = db.query(_models.addressModel)

    #convert each address models to address schema and make a list to be returned
    return list(map(_schemas.addressResponse.from_orm, addresss))

async def get_address_detail(address_id: int, db: _orm.session):
    db_address = db.query(_models.addressModel).filter(_models.addressModel.id==address_id).first()
    if db_address is None:
        raise _fastapi.HTTPException(status_code=404, detail="address not found")

    #return _schemas.addressResponse.from_orm(db_address)
    return db_address

async def retrieve_address(coordinates_x: int,coordinates_y: int, db: _orm.session):
    db_address = db.query(_models.addressModel).filter(_models.addressModel.x==coordinates_x).filter(_models.addressModel.y==coordinates_y).first()
    if db_address is None:
        raise _fastapi.HTTPException(status_code=404, detail="address not found")

    #return _schemas.addressResponse.from_orm(db_address)
    return db_address

async def get_user_detail(user_id: int, db: _orm.session):
    db_user = db.query(_models.UserModel).filter(_models.UserModel.id==user_id).first()
    if db_user is None:
        raise _fastapi.HTTPException(status_code=404, detail="User not found")

    return _schemas.UserResponse.from_orm(db_user)

async def delete_address(address: _models.addressModel, db: _orm.session):
    db.delete(address)
    db.commit()

async def update_address(
        address_request: _schemas.addressRequest,
        address: _models.addressModel,
        db: _orm.session
):
    address.x = address_request.x
    address.y = address_request.y

    db.commit()
    db.refresh(address)
    return _schemas.addressResponse.from_orm(address)







