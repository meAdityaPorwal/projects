from datetime import timedelta, datetime
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette import status
from database import SessionLocal
from models import Users
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError

router = APIRouter(
    prefix='/auth', # dividing the operations according to their file
    tags=['auth']
)

# JWT needs a secret and an algorithm, so we have to do this
# on terminal use this -- openssl rand -hex 32, ab isse jo key aayegi uska use krna
SECRET_KEY = '4a72b92198f7dc46a9566297dd0fbe4592c225afb1a025151eda1a9d4ab11ec4'
ALGORITHM = 'HS256'

# Encoding JWT
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
# Now in this bcrypt_context, we will use our hashing algorithm 'bcrypt'

# for decoding the JWT
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')


class CreateUserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str
    phone_number: str


class Token(BaseModel):
    access_token: str
    token_type: str



def get_db():
    # create db dependency
    # before each request, we now need to fetch this db session local and be able to open up the
    # connection and close the connection on every request send to this fast api application
    db = SessionLocal()
    try:
        # only the code prior to and including yield statement is executed before sending a response
        # the code following the yield statement, is executed after the response has been delivered.
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


# To authenticate the user, we have created this function, which will take username and
# password and database session, match them in database, return the result
def authenticate_user(username: str, password: str, db):
    user = db.query(Users).filter(Users.username == username).first() # based on the username
    if not user:
        return False
    # to verify whether this password matches with our original password or not.
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user


def create_access_token(username: str, user_id: int, role: str, expires_delta: timedelta):
    encode = {'sub': username, 'id': user_id, 'role': role}
    expires = datetime.utcnow() + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


# we have to check whether our token is true or fake
async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        user_role: str = payload.get('role')
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='Could Not Validate User')
        return {'username': username, 'id': user_id, 'user_role': user_role}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Could Not Validate User')


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency,
                      create_user_request: CreateUserRequest):
    create_user_model = Users(
        email = create_user_request.email,
        username = create_user_request.username,
        first_name = create_user_request.first_name,
        last_name = create_user_request.last_name,
        role = create_user_request.role,
        hashed_password = bcrypt_context.hash(create_user_request.password),
        is_active = True,
        phone_number = create_user_request.phone_number
    )

    db.add(create_user_model)
    db.commit()


# created a new API request, type : 'POST', API name : 'token', for user verification
# is token ke pass user ki sari information hogi, so ye yha se direct return krega ki user
# authentic hai ya nhi
# This 'token' is simply a JWT (JSON Web Token),

# first, receiving the information that user have submitted
@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                                 db: db_dependency):
    # here we have passed them to verify in our database
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Could Not Validate User')
    token = create_access_token(user.username, user.id, user.role, timedelta(minutes=20))
    
    return {'access_token': token, 'token_type': 'bearer'} #'Authentication is Successful'

# to submit forms to our application, we have to (pip) install python-multipart name package
# here we use 'OAuth2PasswordRequestForm' form,
# now, we have to add dependency injection to fastapi endpoint
# Due to this dependency injection, we can now give username and password to validate the credentials


# Before using JWT Token, we have to install some libraries
# pip install "python-jose[cryptography]"

