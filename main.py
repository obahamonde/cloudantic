import os
from datetime import datetime
from typing import Optional

from cloudantic import *

AUTH0_URL = os.environ["AUTH0_URL"]
class Namespace(DynaModel):
    """
    Namesoace
    """

    user: str = Field(..., pk=True)
    namespace: str = Field(..., sk=True)
    created_at: str = Field(
        default_factory=lambda: str(datetime.astimezone(datetime.now()))
    )


class Task(DynaModel):
    user: str = Field(..., pk=True)
    title: str = Field(...)
    description: str = Field(...)
    created_at: str = Field(
        default_factory=lambda: str(datetime.astimezone(datetime.now()))
    )
    completed: bool = Field(default=False, sk=True)


class User(DynaModel):
    """
    Auth0 User, Github User or Cognito User
    """

    email: Optional[str] = Field(default=None)
    email_verified: Optional[bool] = Field(default=False)
    family_name: Optional[str] = Field(default=None)
    given_name: Optional[str] = Field(default=None)
    locale: Optional[str] = Field(default=None, sk=True)
    name: str = Field(...)
    nickname: Optional[str] = Field(default=None)
    picture: Optional[str] = Field(default=None)
    sub: str = Field(..., pk=True)
    updated_at: Optional[str] = Field(default=None)


class Document(DynaModel):
    """
    Document
    """

    user: str = Field(..., pk=True)
    namespace: str = Field(..., sk=True)
    title: str = Field(...)
    content: str = Field(...)
    created_at: str = Field(
        default_factory=lambda: str(datetime.astimezone(datetime.now()))
    )


class Post(DynaModel):
    user: str = Field(..., pk=True)
    namespace: str = Field(..., sk=True)
    title: str = Field(...)
    content: str = Field(...)
    created_at: str = Field(
        default_factory=lambda: str(datetime.astimezone(datetime.now())),sk=True
    )


class Message(DynaModel):
    user: str = Field(..., pk=True)
    namespace: str = Field(..., sk=True)
    role: str = Field(...)
    content: str = Field(...)
    created_at: str = Field(
        default_factory=lambda: str(datetime.astimezone(datetime.now())),
        sk=True,
    )


class Uploads(DynaModel):
    user: str = Field(..., pk=True)
    namespace: str = Field(..., sk=True)
    key: str = Field(...)
    created_at: str = Field(
        default_factory=lambda: str(datetime.astimezone(datetime.now()))
    )
    content_type: str = Field(...)
    size: int = Field(...)
    pages: Optional[int] = Field(default=None)


app = APIServer()


@app.get("/")
async def index():
    return HTTPFound("/docs")


@app.sse("/api/chat/{user}")
async def chat(user:str,text: str, sse: EventSourceResponse):
    agent = Agent(namespace="chat")
    string = ""
    async for message in agent.run(text):
        if message:
            string += message
            await sse.send(message)  # type: ignore
    await Message(user=user,namespace="chat",role="user",content=text).put()
    await Message(user=user,namespace="chat",role="assistant",content=string).put()
    await sse.send("",event="done")  # type: ignore
    return sse

@app.get("/api/chatlist/{user}")
async def chat_list(user:str):
    return await Message.query(pk=user)    

@app.get("/api")
async def api():
    return {"message": "An Opinionated AWS, AioHTTP, VueJS Stack"}

@app.post("/api/auth")
async def auth(request:Request):
    token = request.headers.get("Authorization", "").split(" ")[-1]
    user = await APIClient(base_url=AUTH0_URL,headers={"Authorization":f"Bearer {token}"}).get("/userinfo")
    return await User(**user).put()

@app.get("/api/user/{user}")
async def users(user: str):
    return (await User.query(pk=user))[0]


@app.post("/api/post")
async def post(post: Post):
    print(post.pk, post.sk)
    return await post.put()

@app.get("/api/post/{user}")
async def posts(user: str):
    data =  await Post.query(pk=user)
    print(data)
    return data

@app.delete("/api/post/{user}")
async def delete_post(user: str, sk: str):
    print(user, sk)
    return await Post.delete(pk=user, sk="#".join(sk.split(",")))


@app.on_event("startup")
async def startup(_):
    await DynaModel.create_table()


