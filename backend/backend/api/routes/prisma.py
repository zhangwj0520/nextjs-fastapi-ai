from fastapi import APIRouter

from prisma.models import User, Post
from prisma.types import UserUpdateInput, UserCreateInput
from prisma.partials import UserWithoutRelations, PostWithoutRelations

from typing import Optional, List

router = APIRouter()


# Define a GET endpoint for listing users.
@router.get(
    "/user",
    response_model=List[UserWithoutRelations],
)
async def list_users(take: int = 10) -> List[User]:
    """
    This endpoint returns a list of users with specified number of records (`take` parameter).

    :param take: The number of user records to return. Defaults to `10`.
    :type take: int

    :return: A list of UserWithoutRelations instances representing the users.
    :rtype: List[UserWithoutRelations]
    """
    return await User.prisma().find_many(take=take)


@router.post(
    "/user",
    response_model=UserWithoutRelations,
)
async def create_user(item: UserCreateInput) -> User:
    """
    这个函数定义了一个 POST 方法，用于创建一个新的用户。

    参数：
    - `item`: 一个 UserCreateInput 实例，包含了新用户的创建所需数据（如用户名和电子邮件）。

    返回值：
    - `UserWithoutRelations`：这是对返回的用户实体的一个修改版本，通常意味着不包括与该用户相关联的关系模型字段。这可能是因为在 API 层级上处理性能、内存或简化响应的目的。

    实现流程：
    1. 使用 Prisma 的 ORM 方法 `.create(item)` 来创建一个新的用户实例。
    2. 然后，通过 `await User.prisma().create(item)` 调用异步操作来执行创建操作，并在完成时返回结果。这通常意味着该方法会等待数据库操作完成并返回新创建的 User 对象。

    注意：在这个上下文中，User 类和 Prisma ORM（Prisma Client）都假设已经集成到系统中以处理数据库交互。
    """
    return await User.prisma().create(item)


@router.put(
    "/users/{user_id}",
    response_model=UserWithoutRelations,
)
async def update_user(
    user_id: str,
    name: Optional[str] = None,
    email: Optional[str] = None,
) -> Optional[User]:
    data: UserUpdateInput = {}

    if name is not None:
        data["name"] = name

    if email is not None:
        data["email"] = email

    return await User.prisma().update(
        where={
            "id": user_id,
        },
        data=data,
    )


# @router.delete(
#     "/users/{user_id}",
#     response_model=User,
# )
# async def delete_user(user_id: str) -> Optional[User]:
#     return await User.prisma().delete(
#         where={
#             "id": user_id,
#         },
#         include={
#             "posts": True,
#         },
#     )


# @router.get(
#     "/users/{user_id}",
#     response_model=UserWithoutRelations,
# )
# async def get_user(user_id: str) -> Optional[User]:
#     return await User.prisma().find_unique(
#         where={
#             "id": user_id,
#         },
#     )


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
