from typing import Any, Optional
from sqlalchemy import select, func, or_, and_

from app.database.models import Post, User
from app.database.models import async_session


async def set_post(channel_id: int, post_id: int, media_group_id: Optional[str]) -> Any:
    conditions = [and_(Post.channel_id == channel_id, Post.post_id == post_id)]
    if media_group_id is not None:
        conditions.append(Post.media_group_id == media_group_id)

    query = select(Post).where(or_(*conditions))
    async with async_session() as session:
        result = await session.execute(query)
        post = result.scalar()
        if post is not None:
            return None
        obj_post = Post(
            channel_id=channel_id,
            post_id=post_id,
            media_group_id=media_group_id
        )
        session.add(obj_post)
        await session.commit()


async def set_user(user_id: int, status: int) -> Any:
    query = select(User).where(User.user_id == user_id)
    async with async_session() as session:
        result = await session.execute(query)
        user = result.scalar()
        if user is not None:
            return None
        obj_user = User(
            user_id=user_id,
            status=status,
            respect=0,
            bananas=0
        )
        session.add(obj_user)
        await session.commit()


async def get_user(user_id: int) -> User | None:
    query = select(User).where(User.user_id == user_id)
    async with async_session() as session:
        result = await session.execute(query)
        return result.scalar()


async def get_random_post() -> Post | None:
    query = select(Post).order_by(func.random()).limit(1)
    async with async_session() as session:
        result = await session.execute(query)
        return result.scalar()


async def has_channel_posts(channel_id: int) -> bool:
    query = select(Post.id).where(Post.channel_id == channel_id).limit(1)
    async with async_session() as session:
        result = await session.execute(query)
        return result.scalar() is not None