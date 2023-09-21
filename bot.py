from creart import create
from graia.ariadne.app import Ariadne
from graia.ariadne.connection.config import config, HttpClientConfig, WebsocketClientConfig
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.parser.base import MentionMe
from graia.ariadne.model import Friend, Member
from graia.broadcast import Broadcast
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.model import Group
from loguru import logger
from chatgpt import ChatGPT

bcc = create(Broadcast)
app = Ariadne(config(999999999, "", HttpClientConfig("http://localhost:16080"),
                     WebsocketClientConfig("ws://localhost:16080")))
friendDict = {}
groupDict = {}


# TODO 插件注册模式对接不同api后端
# TODO saya
# TODO 表情emoji等特殊处理
# TODO 支持回复@ 支持区分发送对象（进行角色扮演）
# TODO 高并发模式（复制ChatGPT对象，同时请求）

@app.broadcast.receiver("FriendMessage")
async def friend_chat(app: Ariadne, friend: Friend, message: MessageChain):
    if friend.id not in friendDict:
        friendDict[friend.id] = ChatGPT()
        logger.success(f"friend {friend.id} registered")
    if message.display == "#clear":
        await app.send_message(
            friend,
            MessageChain(f"clear memory..."),
        )
    await friendDict[friend.id].push(message.display)
    await app.send_message(friend, MessageChain(f"{await friendDict[friend.id].pull()}"))


@bcc.receiver(GroupMessage)
async def group_chat(app: Ariadne, group: Group, member: Member, message: MessageChain = MentionMe()):
    if group.id in groupDict:
        if message.display == "#clear":
            await app.send_message(
                group,
                MessageChain(f"clear memory..."),
            )
        await groupDict[group.id].push(message.display)
        await app.send_message(
            group,
            MessageChain(f"{await groupDict[group.id].pull()}"),
        )
    else:
        if message.display == "#reg" and member.id == 111111111:
            groupDict[group.id] = ChatGPT()
            logger.success(f"group {group.id} registered")


@app.broadcast.receiver("FriendMessage")
async def command_line(app: Ariadne, friend: Friend, message: MessageChain):
    if friend.id == 111111111:
        pass
        # await app.send_message(friend, MessageChain([Plain("Hello, World!")]))


Ariadne.launch_blocking()
for key in friendDict.keys():
    friendDict[key].save()
logger.success('save friend memory complete')
for key in groupDict.keys():
    groupDict[key].save()
logger.success('save group memory complete')
