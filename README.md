## 一个简单的 Telegram 入群验证 Bot

使用效果展示:(视频在 YouTube)

https://youtu.be/l9MTDzRq2jw

如果有兴趣想要自己搭建一个验证 Bot 可以参考以下步骤。

首先就是 VPS 选择：必须得是 GFW 外面的 VPS 上才能部署，要不然无法访问 Telegram 的 API，自然也无法使用相应的功能了。

### 安装环境

第二步安装必须的插件，使用下面的代码安装 python3、pip3、redis、telepot。我的系统环境是 Ubuntu，如你的环境不是 Ubuntu 请自行替换命令。

```
apt install python3-pip -y
apt install redis -y
pip3 install telepot
pip3 install redis
pip3 install captcha
```

### 获取Bot token

这里你需要自行在 Telegram 上私聊 [@BotFather](https://t.me/BotFather) ，点击 start 后向它发送命令`/newbot`，后面的对话如下图所示：

![](https://static.tstrs.me/20210226new_bot.png)

最下面红框部分为你的 bot token.

### 获取源码

上面的全部都安装好后使用以下命令从 GitHub 获取源码。

```
git clone https://github.com/SaltyLeo/telegram-simple-captcha-bot.git
```
如一切正常，应该是如下输出：

```
Cloning into 'telegram-simple-captcha-bot'...
remote: Enumerating objects: 13, done.
remote: Counting objects: 100% (13/13), done.
remote: Compressing objects: 100% (12/12), done.
remote: Total 13 (delta 0), reused 10 (delta 0), pack-reused 0
Unpacking objects: 100% (13/13), done.
```

### 调试部署

源码下载完毕后，就要编辑代码将记得 Bot Token 放到代码里，使用以下命令编辑 `tgbot.py `

```
cd telegram-simple-captcha-bot && nano tgbot.py

# 修改第18行，将 Token 添加到引号内。
TOKEN = ''#你的bot_TOKEN

#修改为如下所示即可:
TOKEN = '1571461630:AAHtC3BXXXXXXXXXXXXXvF-bGuRG4w8YYI'#你的bot_TOKEN

#最后记得使用 ctrl+x 保存文件并退出nano
```

将 Bot 添加到你需要开启验证的 Telegram 群组中，并授予权限。机器人至少需要两个权限：`删除消息`和`封禁用户`，如下图所示：

![](https://static.tstrs.me/photo_2021-02-26_11-09-42.jpg)


此时回到命令行，使用 `python3 tgbot.py` 启动 Bot 。并在机器人所在的群组中随便发送一条消息，如果运行正常会显示如下输出：

```
bot 已启动 ...
本群组ID为: -10011342xxxxx
```

记住你的群组 ID，我们再次编辑 `tgbot.py ` 文件，将群组 ID 放到第17行的引号中，如下所示：

```
auth_chat = '-10011342xxxxx'#群组id
TOKEN = '1571461630:AAHtC3BXXXXXXXXXXXXXvF-bGuRG4w8YYI'#你的bot_TOKEN
```

最后记得保存文件并退出，Bot 所有的配置均已完成。你现在可以使用命令 `python3 tgbot.py` 启动 Bot，然后使用小号入群测试，应该和本文开篇的视频效果一致。

### 持久化运行

未完待续