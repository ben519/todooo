from typing import List
from fastapi import FastAPI, status, HTTPException, Depends
from database import Base, engine, SessionLocal
from sqlalchemy.orm import Session
import models
import schemas

# Create the database
Base.metadata.create_all(engine)

# Initialize app
app = FastAPI()

# Helper function to get database session
def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

@app.get("/")
def root():
    return "todooo"

@app.post("/todo", response_model=schemas.ToDo, status_code=status.HTTP_201_CREATED)
def create_todo(todo: schemas.ToDoCreate, session: Session = Depends(get_session)):

    # create an instance of the ToDo database model
    tododb = models.ToDo(task = todo.task)

    # add it to the session and commit it
    session.add(tododb)
    session.commit()
    session.refresh(tododb)

    # return the todo object
    return tododb

@app.get("/todo/{id}", response_model=schemas.ToDo)
def read_todo(id: int, session: Session = Depends(get_session)):

    # get the todo item with the given id
    todo = session.query(models.ToDo).get(id)

    # check if todo item with given id exists. If not, raise exception and return 404 not found response
    if not todo:
        raise HTTPException(status_code=404, detail=f"todo item with id {id} not found")

    return todo

@app.put("/todo/{id}", response_model=schemas.ToDo)
def update_todo(id: int, task: str, session: Session = Depends(get_session)):

    # get the todo item with the given id
    todo = session.query(models.ToDo).get(id)

    # update todo item with the given task (if an item with the given id was found)
    if todo:
        todo.task = task
        session.commit()

    # check if todo item with given id exists. If not, raise exception and return 404 not found response
    if not todo:
        raise HTTPException(status_code=404, detail=f"todo item with id {id} not found")

    return todo

@app.delete("/todo/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(id: int, session: Session = Depends(get_session)):

    # get the todo item with the given id
    todo = session.query(models.ToDo).get(id)

    # if todo item with given id exists, delete it from the database. Otherwise raise 404 error
    if todo:
        session.delete(todo)
        session.commit()
    else:
        raise HTTPException(status_code=404, detail=f"todo item with id {id} not found")

    return None

@app.get("/todo", response_model = List[schemas.ToDo])
def read_todo_list(session: Session = Depends(get_session)):

    # get all todo items
    todo_list = session.query(models.ToDo).all()

    return todo_list