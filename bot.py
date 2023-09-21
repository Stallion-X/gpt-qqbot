from creart import create
from graia.ariadne.app import Ariadne
from graia.ariadne.connection.config import config, HttpClientConfig, WebsocketClientConfig
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.element import Plain
from graia.ariadne.message.parser.base import MentionMe
from graia.ariadne.model import Friend
from graia.broadcast import Broadcast
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.model import Group

import chatgpt

bcc = create(Broadcast)
app = Ariadne(config(999999999, "", HttpClientConfig("http://localhost:16080"),
                     WebsocketClientConfig("ws://localhost:16080")))


# TODO 插件注册模式对接不同api后端
# TODO saya

@app.broadcast.receiver("FriendMessage")
async def friend_message_listener(app: Ariadne, friend: Friend, ):
    if friend.id == 111111111:
        await app.send_message(friend, MessageChain([Plain("Hello, World!")]))


@bcc.receiver(GroupMessage)
async def chat1(app: Ariadne, group: Group, message: MessageChain = MentionMe()):
    if group.id == 222222222:
        if message.display == "#clear":
            await app.send_message(
                group,
                MessageChain(f"clear memory..."),
            )
        await chatgpt.push(message.display)
        await app.send_message(
            group,
            MessageChain(f"{await chatgpt.pull()}"),
        )


@bcc.receiver(GroupMessage)
async def chat2(app: Ariadne, group: Group, message: MessageChain = MentionMe()):
    if group.id == 333333333:
        if message.display == "#clear":
            await app.send_message(
                group,
                MessageChain(f"clear memory..."),
            )
        await chatgpt.push(message.display)
        await app.send_message(
            group,
            MessageChain(f"{await chatgpt.pull()}"),
        )


Ariadne.launch_blocking()
chatgpt.save()
