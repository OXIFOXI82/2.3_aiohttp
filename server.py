import json

import bcrypt
from aiohttp import web
from sqlalchemy.exc import IntegrityError

from models import Session, User, engine, init_orm, Advert

app = web.Application()


def hash_password(password: str):
    password = password.encode()
    password = bcrypt.hashpw(password, bcrypt.gensalt())
    password = password.decode()
    return password



@web.middleware
async def session_middleware(request, handler):
    async with Session() as session:
        request.session = session
        response = await handler(request)
        return response


async def orm_context(app):
    print("Подключение")
    await init_orm()
    yield
    print("Закрытие ")
    await engine.dispose()


app.cleanup_ctx.append(orm_context)
app.middlewares.append(session_middleware)


def get_error(error_class, message):
    return error_class(
        text=json.dumps({"error": message}), content_type="application/json"
    )


async def get_object_by_id(session, object_cls, object_id):
    obj = await session.get(object_cls, object_id)
    if obj is None:
        raise get_error(web.HTTPNotFound, f"Объект с id {object_id} не найден!")
    return obj


async def add_object(session, object_cls, obj):
    try:
        session.add(obj)
        await session.commit()
    except IntegrityError:
        if object_cls == User:
            raise get_error(web.HTTPConflict, f"Пользователь {obj.name} уже существует!")
        else:
            raise get_error(web.HTTPConflict, f"Объявление {obj.header} уже существует!")
    return obj.id


class UserView(web.View):

    @property
    def user_id(self):
        return int(self.request.match_info["user_id"])

    @property
    def session(self):
        return self.request.session

    async def get_user(self):
        user = await get_object_by_id(self.session, User, self.user_id)
        return user

    async def get(self):
        user = await self.get_user()
        return web.json_response(user.dict)

    async def post(self):
        user_data = await self.request.json()
        user = User(**user_data)
        await add_object(self.session, User, user)
        return web.json_response({"id": user.id})

    async def patch(self):
        user_data = await self.request.json()
        user = await self.get_user()
        for key, value in user_data.items():
            setattr(user, key, value)
        await add_object(self.session, User, user)
        return web.json_response({"id": user.id})

    async def delete(self):
        user = await self.get_user()
        await self.session.delete(user)
        await self.session.commit()
        return web.json_response({"status": "Удалено"})


class AdvertView(web.View):

    @property
    def advert_id(self):
        return int(self.request.match_info["advert_id"])

    @property
    def session(self):
        return self.request.session

    async def get_advert(self):
        advert = await get_object_by_id(self.session, Advert, self.advert_id)
        return advert

    async def get(self):
        advert = await self.get_advert()
        return web.json_response(advert.dict)

    async def post(self):
        advert_data = await self.request.json()
        advert = Advert(**advert_data)
        await add_object(self.session, Advert, advert)
        return web.json_response({"id": advert.id})

    async def patch(self):
        advert_data = await self.request.json()
        advert = await self.get_advert()
        for key, value in advert_data.items():
            setattr(advert, key, value)
        await add_object(self.session, Advert, advert)
        return web.json_response({"id": advert.id})

    async def delete(self):
        advert = await self.get_advert()
        await self.session.delete(advert)
        await self.session.commit()
        return web.json_response({"status": "Удалено"})


app.add_routes(
    [
        web.get("/users/{user_id:\d+}", UserView),
        web.patch("/users/{user_id:\d+}", UserView),
        web.delete("/users/{user_id:\d+}", UserView),
        web.post("/users", UserView),

        web.get("/adverts/{advert_id:\d+}", AdvertView),
        web.patch("/adverts/{advert_id:\d+}", AdvertView),
        web.delete("/adverts/{advert_id:\d+}", AdvertView),
        web.post("/adverts", AdvertView)
    ]
)

web.run_app(app)