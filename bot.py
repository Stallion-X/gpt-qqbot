import re
import openai
from asyncer import asyncify
from creart import create
from graia.ariadne.app import Ariadne
from graia.ariadne.connection.config import config, HttpClientConfig, WebsocketClientConfig
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.element import At
from graia.ariadne.message.parser.base import MentionMe
from graia.ariadne.model import Friend, Member
from graia.broadcast import Broadcast
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.model import Group
from loguru import logger
from chatgpt import ChatGPT
import balance

qq = 999999999
admin = 111111111
bcc = create(Broadcast)
app = Ariadne(config(qq, "", HttpClientConfig("http://localhost:16080"),
                     WebsocketClientConfig("ws://localhost:16080")))
friendDict = {}
groupDict = {}
admin_mode = False


# TODO 请求失败时的异常处理，不然协程卡住，一直add waiting queue而不会再次请求
# TODO 说明书
# TODO 显示已注册的群组和私聊列表
# DONE 查询余额
# DONE 管理员模式 手动热切换key
# TODO 管理员模式查看当前所有sessions 注册或反注册
# TODO 插件注册模式对接不同api后端
# TODO 重构架构（指令处理类等）
# TODO saya
# TODO 支持区分发送对象（角色扮演prompt，在群里按名字进行扮演）
# DONE 高并发模式（不同的ChatGPT对象（session）同时请求）
# TODO 配置文件

@app.broadcast.receiver("FriendMessage")
async def friend_chat(app: Ariadne, friend: Friend, message: MessageChain):
    if friend.id != qq:
        if message.display == '#admin':
            return
        if friend.id == admin and admin_mode is True:
            return
        if friend.id not in friendDict:
            friendDict[friend.id] = ChatGPT()
            logger.success(f"friend {friend.id} registered")
        if message.display == "#clear":
            await app.send_message(
                friend,
                MessageChain(f"clear memory..."),
            )
        if message.display == '#balance':
            logger.success('balance querying...')
            try:
                await app.send_message(
                    friend,
                    MessageChain(f"{await asyncify(balance.get_remaining)()}"),
                )
                logger.success('balance query success')
                return
            except Exception as e:
                logger.error(e)
                return
        elif message.display == "#reload":
            await asyncify(friendDict[friend.id].save)()
            logger.success("save friend memory complete")
            del friendDict[friend.id]
            friendDict.pop(friend.id, None)
            friendDict[friend.id] = ChatGPT()
            logger.success(f"friend {friend.id} reloaded")
            return
        if friendDict[friend.id].inuse is False and not friendDict[friend.id].waitQueue:  # session未在被使用，等待队列为空
            await app.send_message(friend, MessageChain(f"{await friendDict[friend.id].push(message.display)}"))
        if friendDict[friend.id].inuse is True:  # session正在被使用
            friendDict[friend.id].waitQueue.append(message.display)
            logger.info("added to waiting queue")
            if len(friendDict[friend.id].waitQueue) > 3:
                await app.send_message(
                    friend,
                    MessageChain(f"正在等待前一条回复，少安毋躁...（bot异步协程升级中，bug较多，如遇一直卡等待请使用\"#reload\"）"),
                )
        if friendDict[friend.id].inuse is False and friendDict[friend.id].waitQueue:  # session未在被使用，等待队列不为空
            while friendDict[friend.id].waitQueue:
                await app.send_message(friend, MessageChain(
                    f"{await friendDict[friend.id].push(friendDict[friend.id].waitQueue.popleft())}"))
                logger.info(f"waiting queue remaining:{len(friendDict[friend.id].waitQueue)}")


@bcc.receiver(GroupMessage)
async def group_chat(app: Ariadne, group: Group, member: Member, message: MessageChain = MentionMe()):
    if group.id in groupDict:
        if message.display == "#clear":
            await app.send_message(
                group,
                MessageChain(f"clear memory..."),
            )
        if message.display == '#balance':
            logger.success('balance querying...')
            try:
                await app.send_message(
                    group,
                    MessageChain(f"{await asyncify(balance.get_remaining)()}"),
                )
                logger.success('balance query success')
                return
            except Exception as e:
                logger.error(e)
                return
        elif message.display == "#dereg" and member.id == admin:
            await asyncify(groupDict[group.id].save)()
            logger.success("save group memory complete")
            del groupDict[group.id]
            groupDict.pop(group.id, None)
            logger.success(f"group {group.id} deregistered")
            return
        # await app.send_message(
        #     group,
        #     MessageChain(At(member.id), f" {await groupDict[group.id].push(message.display)}"),
        # )
        if groupDict[group.id].inuse is False and not groupDict[group.id].waitQueue:  # session未在被使用，等待队列为空
            await app.send_message(group,
                                   MessageChain(At(member.id), f" {await groupDict[group.id].push(message.display)}"))
        if groupDict[group.id].inuse is True:  # session正在被使用
            groupDict[group.id].waitQueue.append(message.display)
            logger.info("added to waiting queue")
            if len(groupDict[group.id].waitQueue) > 3:
                await app.send_message(
                    group,
                    MessageChain(At(member.id), f" 正在等待前一条回复，少安毋躁..."),
                )
        if groupDict[group.id].inuse is False and groupDict[group.id].waitQueue:  # session未在被使用，等待队列不为空
            while groupDict[group.id].waitQueue:
                await app.send_message(group, MessageChain(
                    At(member.id),
                    f" {await groupDict[group.id].push(groupDict[group.id].waitQueue.popleft())}"))
                logger.info(f"waiting queue remaining:{len(groupDict[group.id].waitQueue)}")
    else:
        if message.display == "#reg" and member.id == admin:
            groupDict[group.id] = ChatGPT()
            logger.success(f"group {group.id} registered")


@app.broadcast.receiver("FriendMessage")
async def command_line(app: Ariadne, friend: Friend, message: MessageChain):
    global admin_mode
    if friend.id == admin:
        if message.display == '#admin' and admin_mode is False:
            admin_mode = True
            logger.success('admin access granted')
            return
        if message.display == '#exit' and admin_mode is True:
            admin_mode = False
            logger.success('admin exited')
            return
        if admin_mode is True:
            if message.display == '#key':
                await app.send_message(
                    friend,
                    MessageChain(f"{openai.api_key}"),
                )
                logger.info(f'get key {openai.api_key}')
            if re.match("#changekey:", message.display):
                openai.api_key = message.display.split(':')[1]
                logger.info(f"switched to key {openai.api_key}")
            # await app.send_message(friend, MessageChain([Plain("Hello, World!")]))


Ariadne.launch_blocking()
for key in friendDict.keys():
    friendDict[key].save()
logger.success('save all friend memory complete')
for key in groupDict.keys():
    groupDict[key].save()
logger.success('save all group memory complete')
