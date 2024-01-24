from fastapi import FastAPI
import models
from database import engine
from routers import auth, todos, admin, users

# using this technique, we have just clean our application for scalability and maintainability
# we can create multiple python files, each with own distinct functionalities then we will
# combine them to main.py file

app = FastAPI()
models.Base.metadata.create_all(bind=engine)
# This will only run when todos.db does not exist.
# the above line create everything from our database.py file and models.py file to be created
# a new database that has a new table of 'todos' and all the columns which we have given

# Now, todos.db has been created, so we have to install sqlite on our system

app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(users.router)

#
# def get_db():
#     # create db dependency
#     # before each request, we now need to fetch this db session local and be able to open up the
#     # connection and close the connection on every request send to this fast api application
#     db = SessionLocal()
#     try:
#         # only the code prior to and including yield statement is executed before sending a response
#         # the code following the yield statement, is executed after the response has been delivered.
#         yield db
#     finally:
#         db.close()
#
#
# db_dependency = Annotated[Session, Depends(get_db)]
#
# class TodoRequest(BaseModel):
#     title: str = Field(min_length=3)
#     description: str = Field(min_length=3, max_length=100)
#     priority: int = Field(gt=0, lt=6)
#     complete: bool
#
#
# @app.get("/", status_code=status.HTTP_200_OK)
# async def read_all(db: db_dependency):
#     # depends -- dependency injection
#     # we have to do something before executing whatever we are trying to execute
#     return db.query(Todos).all()
#     # here we call, our db, then here we write a query (which is a script to our database)
#     # where we have pass our model(TODOS) and in return we want all our data so we have
#     # used .all() method.
#
#
# # Fetch Single Todo based on the todo id
# @app.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
# async def read_todo(db: db_dependency, todo_id: int = Path(gt=0)):
#     # Path(gt=0) -- validation at path, like id should be greater than 0
#     # if we give lesser value then this will throw an exception.
#     todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
#     if todo_model is not None:
#         return todo_model
#     raise HTTPException(status_code=404, detail='Todo not found.')
#
#
# @app.post("/todo", status_code=status.HTTP_201_CREATED)
# async def create_todo(db: db_dependency, todo_request: TodoRequest):
#     todo_model = Todos(**todo_request.dict())
#
#     db.add(todo_model)
#     # adding means getting the db ready / we want to add this data into our db
#     db.commit()
#     # do a transaction into the database / helps us to store our data in db (reflecting)
#     # permanent store karne ke liye commit() use krna pdega
#
# @app.put("/todo/{todo_id}", status_code= status.HTTP_204_NO_CONTENT)
# async def update_todo(db: db_dependency, todo_request: TodoRequest, todo_id: int = Path(gt=0)):
#     todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
#     if todo_model is None:
#         raise HTTPException(status_code=404, detail='Todo not found')
#
#     todo_model.title = todo_request.title
#     todo_model.description = todo_request.description
#     todo_model.priority = todo_request.priority
#     todo_model.complete = todo_request.complete
#
#     db.add(todo_model)
#     db.commit()
#
#
# @app.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
# async def delete_todo(db: db_dependency, todo_id: int = Path(gt=0)):
#     todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
#     if todo_model is None:
#         raise HTTPException(status_code=404, detail='Todo not found')
#     db.query(Todos).filter(Todos.id == todo_id).delete()
#
#     db.commit()
#
#
