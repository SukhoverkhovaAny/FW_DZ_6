# Задание №5*
# Разработать API для управления списком задач с использованием базы
# данных MongoDB. Для этого создайте модель Task со следующими полями:
# ○ id: str (идентификатор задачи, генерируется автоматически)
# ○ title: str (название задачи)
# ○ description: str (описание задачи)
# ○ done: bool (статус выполнения задачи)
# API должно поддерживать следующие операции:
# ○ Получение списка всех задач: GET /tasks/
# ○ Получение информации о конкретной задаче: GET /tasks/{task_id}/
# ○ Создание новой задачи: POST /tasks/
# ○ Обновление информации о задаче: PUT /tasks/{task_id}/
# ○ Удаление задачи: DELETE /tasks/{task_id}/
# Для валидации данных используйте параметры Field модели Task.
# Для работы с базой данных используйте PyMongo.

import databases
import sqlalchemy
from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import List

DATABASE_URL = "sqlite:///mydatabase.db"

database = databases.Database(DATABASE_URL)

metadata = sqlalchemy.MetaData()

tasks = sqlalchemy.Table(
    "tasks",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("title", sqlalchemy.String(32)),
    sqlalchemy.Column("description", sqlalchemy.String(128)),
    sqlalchemy.Column("done", sqlalchemy.Boolean),
)

engine = sqlalchemy.create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

metadata.create_all(engine)

app = FastAPI()

class Task(BaseModel):
    title : str = Field(max_length=32)
    description : str = Field(max_length=128)
    done : bool


class TaskID(Task):
    id : int


@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


# @app.get("/fake_task/{count}")
# async def create_note(count : int):
#     for i in range(count):
#         query = tasks.insert().values(title=f'title{i}', description=f'descrirtion{i} task', done=True)
#         await database.execute(query)
#     return {'message': f'{count} fake tasks create'}

@app.get("/tasks/", response_model=List[TaskID])
async def get_tasks():
    query = tasks.select()
    return await database.fetch_all(query)

@app.get("/tasks/{task_id}", response_model=Task)
async def get_task(task_id: int):
    query = tasks.select().where(tasks.c.id == task_id)
    return await database.fetch_one(query)


@app.post("/tasks/", response_model=TaskID)
async def create_task(task : Task):
    query = tasks.insert().values(**task.model_dump())
    last_record_id = await database.execute(query)
    return {**task.model_dump(), "id": last_record_id}

@app.put("/tasks/{task_id}", response_model=TaskID)
async def change_task(task_id: int, new_task: Task):
    query = tasks.update().where(tasks.c.id == task_id).values(**new_task.model_dump())
    await database.execute(query)
    return {**new_task.model_dump(), "id": task_id}

@app.delete("/tasks/{task_id}")
async def delete_task(task_id: int):
    query = tasks.delete().where(tasks.c.id == task_id)
    await database.execute(query)
    return {'message': "User delete"}