# -*- coding: utf-8 -*-
import re
import random
import time
import telepot
import redis
import chardet
import time
import datetime
from random import choice
from random import shuffle
from telepot.loop import MessageLoop
from captcha.image import ImageCaptcha
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton

id_count = redis.StrictRedis(host='localhost',port=6379,db=5,charset='UTF-8')#临时数据存放
auth_chat = ''#群组id
TOKEN = ''#你的bot_TOKEN
chinese_captcha = [] #全局中文字符串集合
user_list = [] #未验证用户集
del_count = 0 #已删除机器人统计
def set_chinese():#将文件写入全局变量
    global chinese_captcha
    try:
        f = open('hz.json', 'r')    # 打开文件
        chinese_captcha = f.read()  # 读取文件内容
    finally:
        if f:
            f.close()
def get_chinese_captcha(num):#获取指定字数的中文字符
    li = []
    for i in range(0,num):
        li.append(choice(chinese_captcha))
    return ''.join(li)

def bulid_captcha(code):
    #使用随机的字体，生成验证码图片
    image = ImageCaptcha(fonts=['zt/%s.ttf'%random.randint(1,5)])
    data = image.generate('%s'%code)
    return data

def uname_DS(uname):
    #对用户名打码
    return '%s██%s'%(uname[0:2],uname[-2:])

def bulid_kb(gcc):
    #生成随机返回
    kb_list=[get_chinese_captcha(4),get_chinese_captcha(4),gcc,get_chinese_captcha(4)]
    shuffle(kb_list)
    return kb_list,kb_list.index(gcc)

def on_chat_message(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    if str(chat_id) == auth_chat:
        #用户ID
        members_id = msg['from']['id']
        if content_type == 'new_chat_member':
            #新用户列表
            global user_list 
            #用户昵称
            new_members_name = msg['from']['first_name']
            #限制新入群成员所有权限
            bot.restrictChatMember(chat_id,members_id,until_date = None)
            #删除入群消息
            bot.deleteMessage(telepot.message_identifier(msg))
            #验证码字段
            gcc = get_chinese_captcha(4)
            #生成随机验证码并打乱排序
            bkg = bulid_kb(gcc)
            #验证码输入模块
            keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=bkg[0][0], callback_data='0')],[InlineKeyboardButton(text=bkg[0][1], callback_data='1')],[InlineKeyboardButton(text=bkg[0][2], callback_data='2')],[InlineKeyboardButton(text=bkg[0][3], callback_data='3')]])
            #发送验证码图片
            sp = bot.sendPhoto(chat_id,bulid_captcha(gcc),caption='[%s](tg://user?id=%s)\n请在 *90秒* 内选择下方与图片一致的验证码，否则将会被 *永久封禁* 。\n你只有2次机会。'%(uname_DS(new_members_name),members_id),disable_notification=True,parse_mode= 'Markdown',reply_markup=keyboard)
            #加到新用户列表
            user_list.append(members_id)#加到list
            #添加到redis，并设置自动销毁时间为110秒。
            id_count.rpush(members_id,bkg[1],sp['message_id'])
            id_count.expire(members_id,110)
        elif content_type == 'left_chat_member':
            #删除退群信息
            bot.deleteMessage(telepot.message_identifier(msg))
            cc_code = id_count.lrange(members_id,0,-1)
            #未完成流程就退出群组，封锁掉。
            if cc_code != None:
                try:
                    bot.deleteMessage((auth_chat,int(id_count.lrange(members_id,0,-1)[1].decode('utf-8'))))
                    id_count.delete(members_id)
                    bot.kickChatMember(auth_chat,members_id)
                    user_list.remove(members_id)
                except:
                    pass
    elif auth_chat == '':
        print('本群组ID为: '+str(chat_id))
def on_callback_query(msg):
    query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
    raw_uid = msg['message']['caption_entities'][0]['user']['id']
    if raw_uid == from_id:
        icl = id_count.llen(from_id)
        cc_code = id_count.lrange(from_id,0,-1)
        try:
            #校验验证码与返回是否一致
            if cc_code[0].decode('utf-8') == query_data:
                #解除封锁
                bot.restrictChatMember(auth_chat,from_id,can_send_messages=True, can_send_other_messages=True,can_add_web_page_previews=True)
                bot.answerCallbackQuery(query_id, text='你已通过验证！')
                #验证通过删除验证消息
                bot.deleteMessage(telepot.message_identifier(msg['message']))
                #从redis 和 新用户列表中移除。
                id_count.delete(from_id)
                user_list.remove(from_id)
            elif icl == 2:
                #验证错误，提示还有一次机会。
                bot.answerCallbackQuery(query_id, text='验证错误，请重试。\n你还有一次机会。')
                id_count.rpush(from_id,'0')
            elif icl == 3:
                #移出群组
                bot.answerCallbackQuery(query_id, text='验证错误，再见。') 
                bot.kickChatMember(auth_chat,from_id) 
                bot.deleteMessage(telepot.message_identifier(msg['message']))
                id_count.delete(from_id)
                user_list.remove(from_id)
            else:
                bot.kickChatMember(auth_chat,from_id) 
                bot.deleteMessage(telepot.message_identifier(msg['message']))
                id_count.delete(from_id)
                user_list.remove(from_id)
        except:
                pass
    else:
        bot.answerCallbackQuery(query_id, text='你不需要验证。')

bot = telepot.Bot(TOKEN)
MessageLoop(bot, {'chat': on_chat_message,'callback_query': on_callback_query}).run_as_thread()
set_chinese()
print ('bot 已启动 ...')

while 1:
    #每3秒统计一遍未验证用户是否达到90秒限制。
    time.sleep(3)
    for i in user_list:
        c = 0
        if id_count.ttl(i) <=20:
            try:
                bot.deleteMessage((auth_chat,int(id_count.lrange(i,0,-1)[1].decode('utf-8'))))
                id_count.delete(i)
                user_list.remove(i)
                bot.kickChatMember(auth_chat,i)
                c = c + 1
            except:
                pass
        if c != 0 :
            del_count = del_count + 1
            print('已移除 %s 个未完成验证的用户'%del_count)
    
    

