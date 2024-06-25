from fastapi import APIRouter

from prisma.models import User, Post
from prisma.types import (
    UserUpdateInput,
    UserCreateInput,
)
from prisma.partials import UserWithoutRelations, PostWithoutRelations

from typing import Optional, List

router = APIRouter()


@router.get(
    "/user",
    response_model=List[UserWithoutRelations],
)
async def list_users(take: int = 10) -> List[User]:
    return await User.prisma().find_many(take=take)


@router.post("/user", response_model=UserWithoutRelations)
async def create_user(user: UserCreateInput) -> User:
    return await User.prisma().create(user)


@router.put(
    "/user",
    response_model=UserWithoutRelations,
)
async def update_user_byid(user: UserUpdateInput) -> UserWithoutRelations:
    """
    根据用户ID更新用户信息。

    :param user: UserUpdateInput - 用户ID和更新后的用户信息。
    :return: UserWithoutRelations - 更新后的用户信息。
    """
    id = user["id"]
    del user["id"]
    return await User.prisma().update(
        where={"id": id},
        data=user,
    )


@router.put(
    "/user/{user_id}",
    response_model=UserWithoutRelations,
)
async def update_user(user_id: int, user: UserUpdateInput):
    return await User.prisma().update(
        where={
            "id": user_id,
        },
        data=user,
    )


@router.delete(
    "/user/{user_id}",
    response_model=User,
)
async def delete_user(user_id: int):
    print("user_id", user_id)
    return await User.prisma().delete(
        where={
            "id": user_id,
        },
        include={
            "posts": True,
        },
    )


@router.get(
    "/user/{user_id}",
    response_model=UserWithoutRelations,
)
async def get_user(user_id: int) -> Optional[User]:
    return await User.prisma().find_unique(
        where={
            "id": user_id,
        },
    )


# @router.get(
#     "/users/{user_id}/posts",
#     response_model=List[PostWithoutRelations],
# )
# async def get_user_posts(user_id: str) -> List[Post]:
#     user = await User.prisma().find_unique(
#         where={
#             "id": user_id,
#         },
#         include={
#             "posts": True,
#         },
#     )
#     if user is not None:
#         # we are including the posts, so they will never be None
#         assert user.posts is not None
#         return user.posts
#     return []


# @router.post(
#     "/users/{user_id}/posts",
#     response_model=PostWithoutRelations,
# )
# async def create_post(user_id: str, title: str, published: bool) -> Post:
#     return await Post.prisma().create(
#         data={
#             "title": title,
#             "published": published,
#             "author": {
#                 "connect": {
#                     "id": user_id,
#                 },
#             },
#         }
#     )


# @router.get(
#     "/posts",
#     response_model=List[PostWithoutRelations],
# )
# async def list_posts(take: int = 10) -> List[Post]:
#     return await Post.prisma().find_many(take=take)


# @router.get(
#     "/posts/{post_id}",
#     response_model=Post,
# )
# async def get_post(post_id: str) -> Optional[Post]:
#     return await Post.prisma().find_unique(
#         where={
#             "id": post_id,
#         },
#         include={
#             "author": True,
#         },
#     )


# @router.delete(
#     "/posts/{post_id}",
#     response_model=Post,
# )
# async def delete_post(post_id: str) -> Optional[Post]:
#     return await Post.prisma().delete(
#         where={
#             "id": post_id,
#         },
#         include={
#             "author": True,
#         },
#     )
