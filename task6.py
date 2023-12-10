# Задание №6
# Необходимо создать базу данных для интернет-магазина. База данных должна
# состоять из трех таблиц: товары, заказы и пользователи. Таблица товары должна
# содержать информацию о доступных товарах, их описаниях и ценах. Таблица
# пользователи должна содержать информацию о зарегистрированных
# пользователях магазина. Таблица заказы должна содержать информацию о
# заказах, сделанных пользователями.
# ○ Таблица пользователей должна содержать следующие поля: id (PRIMARY KEY),
# имя, фамилия, адрес электронной почты и пароль.
# ○ Таблица товаров должна содержать следующие поля: id (PRIMARY KEY),
# название, описание и цена.
# ○ Таблица заказов должна содержать следующие поля: id (PRIMARY KEY), id
# пользователя (FOREIGN KEY), id товара (FOREIGN KEY), дата заказа и статус
# заказа.
# Создайте модели pydantic для получения новых данных и
# возврата существующих в БД для каждой из трёх таблиц
# (итого шесть моделей).
# Реализуйте CRUD операции для каждой из таблиц через
# создание маршрутов, REST API (итого 15 маршрутов).
# ○ Чтение всех
# ○ Чтение одного
# ○ Запись
# ○ Изменение
# ○ Удаление

import databases
import sqlalchemy
from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import List

DATABASE_URL = "sqlite:///mydatabase.db"

database = databases.Database(DATABASE_URL)

metadata = sqlalchemy.MetaData()

goods = sqlalchemy.Table(
    "goods",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String(32)),
    sqlalchemy.Column("description", sqlalchemy.String(128)),
    sqlalchemy.Column("price", sqlalchemy.Integer),
)
orders = sqlalchemy.Table(
    "orders",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("id_user", sqlalchemy.Integer, FOREIGN_KEY='users.id'),
    sqlalchemy.Column("id_good", sqlalchemy.Integer, FOREIGN_KEY='goods.id'),
    sqlalchemy.Column("data_order", sqlalchemy.String(32)),
    sqlalchemy.Column("status", sqlalchemy.Boolean),
)
users = sqlalchemy.Table(
    "users",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String(32)),
    sqlalchemy.Column("surname", sqlalchemy.String(32)),
    sqlalchemy.Column("email", sqlalchemy.String(32)),
    sqlalchemy.Column("password", sqlalchemy.String(32)),
)

engine = sqlalchemy.create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

metadata.create_all(engine)

app = FastAPI()

class Good(BaseModel):
    id: int
    name : str = Field(max_length=32)
    description : str = Field(max_length=128)
    price : int

class Order(BaseModel):
    id: int
    id_user : int
    id_good: int
    data_order: str = Field(max_length=32)
    status: bool

class User(BaseModel):
    id: int
    name : str = Field(max_length=32)
    surname : str = Field(max_length=32)
    email : str = Field(max_length=32)
    password: str = Field(max_length=32)

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.get("/goods/", response_model=List[Good])
async def get_goods():
    query = goods.select()
    return await database.fetch_all(query)

@app.get("/goods/{good_id}", response_model=Good)
async def get_good(good_id: int):
    query = goods.select().where(goods.c.id == good_id)
    return await database.fetch_one(query)

@app.post("/goods/", response_model=Good)
async def create_good(good : Good):
    query = goods.insert().values(**good.model_dump())
    last_record_id = await database.execute(query)
    return {**good.model_dump(), "id": last_record_id}

@app.put("/goods/{good_id}", response_model=Good)
async def change_good(good_id: int, new_good: Good):
    query = goods.update().where(goods.c.id == good_id).values(**new_good.model_dump())
    await database.execute(query)
    return {**new_good.model_dump(), "id": good_id}

@app.delete("/goods/{good_id}")
async def delete_good(good_id: int):
    query = goods.delete().where(goods.c.id == good_id)
    await database.execute(query)
    return {'message': "Good delete"}


@app.get("/orders/", response_model=List[Order])
async def get_orders():
    query = orders.select()
    return await database.fetch_all(query)

@app.get("/orders/{order_id}", response_model=Order)
async def get_order(order_id: int):
    query = orders.select().where(orders.c.id == order_id)
    return await database.fetch_one(query)

@app.post("/orders/", response_model=Order)
async def create_order(order : Order):
    query = orders.insert().values(**order.model_dump())
    last_record_id = await database.execute(query)
    return {**order.model_dump(), "id": last_record_id}

@app.put("/orders/{order_id}", response_model=Order)
async def change_order(order_id: int, new_order: Order):
    query = orders.update().where(orders.c.id == order_id).values(**new_order.model_dump())
    await database.execute(query)
    return {**new_order.model_dump(), "id": order_id}

@app.delete("/orders/{order_id}")
async def delete_order(order_id: int):
    query = orders.delete().where(orders.c.id == order_id)
    await database.execute(query)
    return {'message': "Order delete"}


@app.get("/users/", response_model=List[User])
async def get_users():
    query = users.select()
    return await database.fetch_all(query)

@app.get("/users/{user_id}", response_model=User)
async def get_user(user_id: int):
    query = users.select().where(users.c.id == user_id)
    return await database.fetch_one(query)

@app.post("/users/", response_model=User)
async def create_user(user : User):
    query = users.insert().values(**user.model_dump())
    last_record_id = await database.execute(query)
    return {**user.model_dump(), "id": last_record_id}

@app.put("/users/{user_id}", response_model=User)
async def change_user(user_id: int, new_user: User):
    query = users.update().where(users.c.id == user_id).values(**new_user.model_dump())
    await database.execute(query)
    return {**new_user.model_dump(), "id": user_id}

@app.delete("/users/{user_id}")
async def delete_user(user_id: int):
    query = users.delete().where(users.c.id == user_id)
    await database.execute(query)
    return {'message': "User delete"}

