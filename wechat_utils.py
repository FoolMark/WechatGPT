# 实现用户管理功能
# master用户(一般为登录的账号)，可以发送指令添加\删除 user，并dump到.yaml文件设置里
# 设置user，指定自动回复聊天对象
import itchat
import yaml
from PIL import Image
import datetime
import requests

def load():
    with open('config/user.yaml','r',encoding='utf-8') as f:
        data = yaml.load(f)
        master_name = data['master_name']
        user_names = data['user_name']
        return master_name,user_names

def dump(master_name,user_names):
    with open('config/user.yaml','w',encoding='utf-8') as f:
        data = {'master_name':master_name,'user_name':user_names}
        yaml.dump(data,f,allow_unicode=True)

class WechatTool:
    def __init__(self,robot):
        self.map = {'id2name':{},'name2id':{}}
        self.master_name = None
        self.master_id = None
        self.user_names = []
        self.user_ids = []
        self.login()
        self.getMap()
        self.init_user()
        self.robot = robot

    def getMap(self):
        friends = itchat.get_friends()
        for friend in friends:
            uid = friend.get('UserName')
            name = friend.get('NickName')
            self.map['id2name'][uid] = name
            self.map['name2id'][name] = uid
        return map

    def init_user(self):
        self.master_name,self.user_names = load()
        self.master_id = self.map['name2id'][self.master_name]
        for name in self.user_names:
            self.add_user(name)
            uid = self.map['name2id'][name]
            self.user_ids.append(uid)

    def add_user(self,name):
        if name not in self.user_names and name in self.map['name2id']:
            uid = self.map['name2id'][name]
            self.user_names.append(name)
            self.user_ids.append(uid)
            itchat.send(f'添加成功 {name}',toUserName='filehelper')

    def del_user(self,name):
        if name in self.user_names:
            uid = self.map['name2id'][name]
            self.user_names.remove(name)
            self.user_ids.remove(uid)
            itchat.send(f'删除成功 {name}',toUserName='filehelper')

    def display_user(self):
        itchat.send(str(self.user_names),toUserName='filehelper')

    def update(self):
        dump(self.master_name,self.user_names) 
        itchat.send(f'更新成功',toUserName='filehelper')

    def login(self):
        itchat.auto_login(hotReload=True)
    
    def start(self):
        itchat.run()

    def send_text(self,text,uid):
        # 自己不能给自己发消息，因此在文件传输助手中回复
        if uid == self.master_id:
            uid = 'filehelper'
        text = 'GPT:  ' + text
        itchat.send(text,toUserName=uid)

    def send_img(self,img_url,uid):
        if uid == self.master_id:
            uid = 'filehelper'
        out_path = self.parse_img(img_url)
        itchat.send_image(out_path,toUserName=uid)
    
    def parse_img(self,img_url):
        stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        out_path = f'tmp/{stamp}-dalle.png'
        with open(out_path,'wb') as f:
            f.write(requests.get(img_url).content)
        return out_path

    def on_recv_text(self,msg):
        uid = msg['FromUserName']
        content = msg['Text']
        name = self.map['id2name'][uid]
        chat = True

        # instruction from master
        if name in self.master_name:
            instruct = content.split()[0]
            if instruct in ['add','del','display','update','help']:
                chat = False
            if instruct == 'add':
                self.add_user(content.split()[1])
            if instruct == 'del':
                self.del_user(content.split()[1])
            if instruct == 'display':
                self.display_user()
            if instruct == 'update':
                self.update()
            if instruct == 'help':
                itchat.send_image('help.png',toUserName='filehelper')

        # text msg from user
        if name in self.user_names and chat:
            instruct = content.split()[0]
            if instruct == 'help':
                itchat.send_image('help.png',toUserName=uid)
            else:
                ret_content = self.robot.on_recv_text(uid,content)
                text = ret_content['text']
                img_url = ret_content['img']
                if(text != None):
                    self.send_text(text,uid)
                if(img_url != None):
                    self.send_img(img_url,uid)

    def on_recv_img(self,msg):
        uid = msg['FromUserName']
        name = self.map['id2name'][uid]
        if name in self.user_names:
            filename = msg['FileName']
            msg.download(f'tmp/{filename}')
            ret_content = self.robot.on_recv_img(uid,img_path=f'tmp/{filename}')
            text = ret_content['text']
            img_url = ret_content['img']
            if(text != None):
                self.send_text(text,uid)
            if(img_url != None):
                self.send_img(img_url,uid)
