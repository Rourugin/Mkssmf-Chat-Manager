from typing import Any, Optional
from sqlalchemy import select, func, or_

from app.database.models import Base, Post
from app.database.models import async_session


async def set_post(post_id: int, media_group_id: Optional[str]) -> Any:
    conditions = [Post.post_id == post_id]
    if media_group_id is not None:
        conditions.append(Post.media_group_id == media_group_id)

    query = select(Post).where(or_(*conditions))
    async with async_session() as session:
        result = await session.execute(query)
        post = result.scalar()
        if post is not None:
            return None
        obj_post = Post(
            post_id=post_id,
            media_group_id=media_group_id
        )
        session.add(obj_post)
        await session.commit()


async def get_post(id: int) -> Post | None:
    query = select(Post).where(Post.id == id)
    async with async_session() as session:
        result = await session.execute(query)
        return result.scalar()


async def get_random_post() -> Post | None:
    query = select(Post).order_by(func.random()).limit(1)
    async with async_session() as session:
        result = await session.execute(query)
        return result.scalar()