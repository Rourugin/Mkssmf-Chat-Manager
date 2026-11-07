import os
from dotenv import load_dotenv
from typing import Annotated, Optional
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine


load_dotenv()
engine = create_async_engine(url=os.getenv('SQLALCHEMY_URL'))
async_session = async_sessionmaker(engine)


intpk = Annotated[int, mapped_column(primary_key=True)]
intun = Annotated[int, mapped_column(unique=True)]
strun = Annotated[Optional[str], mapped_column(unique=True)]

class Base(AsyncAttrs, DeclarativeBase):
    pass


class Post(Base):
    __tablename__ = 'posts'

    id: Mapped[intpk]
    post_id: Mapped[intun]
    media_group_id: Mapped[strun]


async def async_main() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)