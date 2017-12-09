#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

import socket
import time
import re
import os
import configparser
from threading import Thread


def print_room_info(room_info):
    room_status=room_info['data']['room_status']
    room_id=room_info['data']['room_id']
    cate_name=room_info['data']['cate_name']
    room_name=room_info['data']['room_name']
    owner_name=room_info['data']['owner_name']
    online=room_info['data']['online']
    fans_num=room_info['data']['fans_num']
    if(room_status!='1'):
        print('主播 '+str(owner_name)+' 未开播!')
    print('房间名:'+str(room_name),
          '主播ID:'+str(owner_name),
          '游戏分类:'+str(cate_name),
          '在线人数:'+str(online),
          '关注人数:'+str(fans_num))


def connect_to_room(room_id):
    url='http://open.douyucdn.cn/api/RoomApi/room/'+str(room_id)
    headers={
            'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10=_12_5) AppleWebKit/603.2.4 (KHTML, like Gecko) Version/10.1.1 Safari/603.2.4'
            }
    print('------------房间信息获取中----------')
    r = requests.get(url,headers=headers)
    html=r.content.decode('utf-8')
    room_info=json.loads(html)
    if(room_info['error']!=0):
        print('房间不存在!')
        return
    print_room_info(room_info)
    return room_info['data']['room_id']

'''
    弹幕服务器地址  端口
    danmu.douyutv.com:8061
    anmu.douyutv.com:8062
    danmu.douyutv.com:12601
    danmu.douyutv.com:12602
    第三方接入弹幕服务器列表
    IP 地址：openbarrage.douyutv.com
    端口：8601
'''

client= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.settimeout(20.0)

def connect():
    client.connect(('openbarrage.douyutv.com',8601))

def sendmsg(msgstr):
    msg=msgstr.encode('utf-8')
    data_length= len(msg)+8
    code=689
    msgHead = int.to_bytes(data_length, 4, 'little') + int.to_bytes(data_length, 4, 'little') + int.to_bytes(code, 4, 'little')
    client.send(msgHead)  #发送协议头
    client.send(msg)      #发送消息请求

def chinese_count(data):
    count = 0
    for s in data:
        if ord(s) > 127:
            count += 1
    return count

def save_result(msg_text, file_path):
    with open(file_path,'a') as f:
        f.write(msg_text + ' ')

def connectdanmuserver(room_id):
    connect()
    print('----------弹幕服务器连接中----------')
    msg = 'type@=loginreq/roomid@={}/\x00'.format(room_id)
    sendmsg(msg)
    join_room_msg = 'type@=joingroup/rid@={}/gid@=-9999/\x00'.format(room_id) #加入房间分组消息
    sendmsg(join_room_msg)
    chat_msg_pattern = re.compile(b'type@=chatmsg/.+?/nn@=(.+?)/txt@=(.+?)/.+?/level@=(.+?)/')
    while True:
        try:
            data = client.recv(1024)  #这个data就是服务器向客户端发送的消息
        except:
            print('----------连接失败，重试中----------')
            connectdanmuserver(room_id)
            continue
        for nn, txt, level in chat_msg_pattern.findall(data):
            try:
                nick_name = '[{}]:'.format(nn.decode())
                msg_text = txt.decode()
                print('[{}] [lv.{}] {} {}'.format(time.strftime("%Y-%m-%d %H:%M:%S"), level.decode().rjust(2), nick_name.ljust(25-chinese_count(nick_name)), msg_text))
                save_result(msg_text, '../result/danmu/' + room_id)
            except:
                pass

def keeplive():
    while True:
        time.sleep(10)
        msg = 'type@=mrkl/\x00'
        sendmsg(msg)

# 列出常看主播
def list_favorite_options(config):
    print('-----------常看主播列表------------')
    for room_id, person in config.items('favorite'):
        print ('{} = {}'.format(room_id.ljust(8), person))
    print('------------------------------------')

# 获取配置
def get_config():
    config = configparser.RawConfigParser()
    config.read('config.ini')
    return config

if __name__ == '__main__':
    config = get_config()
    list_favorite_options(config)
    while True:
        room_id = connect_to_room(input('请输入房间号或名称:'))
        if room_id:
            break
    t1 = Thread(target=connectdanmuserver,args=(room_id, ))
    t1.start()
    t2 = Thread(target=keeplive)
    t2.start()
