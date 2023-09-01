from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from astro_bot.database.tables import Base, Rovers, User
from astro_bot.models.rovers import Rover
from astro_bot.settings import BotSettings


class DbClient:
    base = Base

    @staticmethod
    async def check_user_receives_apod(user_id: str, session: AsyncSession) -> bool:
        query = select(User).where((User.id == user_id) & (User.send_apod.is_(True)))
        row_result = await session.execute(query)
        result = row_result.scalar_one_or_none()
        return True if result else False

    @staticmethod
    async def add_user_to_newsletter(user_id: int, session: AsyncSession):
        query = insert(User).values(id=user_id, send_apod=True)
        await session.execute(query)
        await session.commit()

    @staticmethod
    async def get_user_list_for_apod(session: AsyncSession) -> list[int]:
        query = select(User).where(User.send_apod.is_(True))
        row_results = await session.execute(query)
        results = row_results.scalars().all()
        return [user.id for user in results]

    @classmethod
    async def create_tables(cls):
        engine = create_async_engine(BotSettings().connection_string.get_secret_value())
        async with engine.begin() as conn:
            await conn.run_sync(cls.base.metadata.create_all)

    @staticmethod
    async def remove_user_from_newsletter(user_id: int, session: AsyncSession):
        query = delete(User).where(User.id == user_id)
        await session.execute(query)
        await session.commit()

    @staticmethod
    async def get_rover_data(rover_name: str, session: AsyncSession) -> Rovers:
        query = select(Rovers).where(Rovers.name == rover_name)
        row_result = await session.execute(query)
        result = row_result.scalar_one_or_none()
        return result

    @staticmethod
    async def record_rover_data(rover: Rover, session: AsyncSession):
        data = rover.data.dict()
        query = update(Rovers).values(data=data).where(Rovers.name == rover.name)
        await session.execute(query)
        await session.commit()
