from fastapi import APIRouter, Depends, HTTPException, Path
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from typing import Annotated
from starlette import status
import models
from models import Todos
from database import SessionLocal
from routers import auth
from .auth import get_current_user

router = APIRouter()

# This will only run when todos.db does not exists
# the above line create everything from our database.py file and models.py file to be created
# a new database that has a new table of 'todos' and all the columns which we have given

# Now, todos.db has been created, so we have to install sqlite on our system

router.include_router(auth.router)


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
user_dependency = Annotated[dict, Depends(get_current_user)]



class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, lt=6)
    complete: bool


@router.get("/", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    # depends -- dependency injection
    # we have to do something before executing whatever we are trying to execute
    return db.query(Todos).filter(Todos.owner_id == user.get('id')).all()
    # here we call, our db, then here we write a query (which is a script to our database)
    # where we have pass our model(TODOS) and in return we want all our data so we have
    # used .all() method.


# Fetch Single Todo based on the todo id
@router.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    # Path(gt=0) -- validation at path, like id should be greater than 0
    # if we give lesser value then this will throw an exception.
    todo_model = db.query(Todos).filter(Todos.id == todo_id)\
        .filter(Todos.owner_id == user.get('id')).first()
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail='Todo not found.')


@router.post("/todo", status_code=status.HTTP_201_CREATED)
async def create_todo(user: user_dependency, db: db_dependency,
                      todo_request: TodoRequest):

    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    # Now, when the user try to add data in db, he got an error, because he didn't
    # authorized himself, so us tag(todo, create todo) ke pass me ek lock wala icon hoga
    # jha usko pehle khudko authorize krna pdega then wo ab db me data add kr payega
    todo_model = Todos(**todo_request.dict(), owner_id=user.get('id'))

    db.add(todo_model)
    # adding means getting the db ready / we want to add this data into our db
    db.commit()
    # do a transaction into the database / helps us to store our data in db (reflecting)
    # permanent store karne ke liye commit() use krna pdega


@router.put("/todo/{todo_id}", status_code= status.HTTP_204_NO_CONTENT)
async def update_todo(user: user_dependency, db: db_dependency,
                      todo_request: TodoRequest,
                      todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    todo_model = db.query(Todos).filter(Todos.id == todo_id)\
        .filter(Todos.owner_id == user.get('id')).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail='Todo not found')

    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.priority = todo_request.priority
    todo_model.complete = todo_request.complete

    db.add(todo_model)
    db.commit()


@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    todo_model = db.query(Todos).filter(Todos.id == todo_id)\
        .filter(Todos.owner_id == user.get('id')).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail='Todo not found')
    db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get('id'))    .delete()

    db.commit()


