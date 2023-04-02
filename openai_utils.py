# 调用OpenAI API , 主要实现对话功能
# 其他功能
import openai
import time
import func_timeout
from config import load
from func_timeout import func_set_timeout
from PIL import Image
from io import BytesIO

config = load()
openai.api_key =  config['openai_api_key']

class OpenAIRobot:
    def __init__(self):
        self.session_dict = {}
        self.model = config['model']

    def on_recv_text(self,uid,content):
        ret_content = {'text':None,'img':None}
        if uid not in self.session_dict:
            self.session_dict[uid] = Session(uid)
        cur_session = self.session_dict[uid]

        if content == 'clear':
            cur_session.clear()
            ret_content['text'] = '历史对话已清除'
            return ret_content

        if content.split()[0] == 'sys':
            cur_session.set_system(content[6:])
            ret_content['text'] = 'AI设定已按照要求更新'
            return ret_content

        if content.split()[0] == 'img':
            try:
                response = None
                ret_content['img'] = self.img_generation(content[4:])
            except func_timeout.exceptions.FunctionTimedOut as e:
                response = 'API 响应超时...请重试'
            except openai.error.APIConnectionError as e:
                response = 'API 网络连接错误...请稍后重试'
            ret_content['text'] = response
            return ret_content

        if content == 'var':
            ret_content['text'] = '请发送图片'
            cur_session.var_flag = True
            return ret_content

        cur_session.append(content,from_user=True)
        try:
            response = self.chat_completion(cur_session)
            cur_session.append(response,from_user=False)
        except func_timeout.exceptions.FunctionTimedOut as e:
            response = 'API 响应超时...请重试'
        except openai.error.APIConnectionError as e:
            response = 'API 网络连接错误...请稍后重试'
        except openai.error.InvalidRequestError as e:
            response = 'API 对话长度超过限制...请发送 clear 重置对话后重试'
        ret_content['text'] = response

        return ret_content

    def on_recv_img(self,uid,img_path):
        ret_content = {'text':None,'img':None}
        if uid not in self.session_dict:
            self.session_dict[uid] = Session(uid)
        cur_session = self.session_dict[uid]
        if cur_session.var_flag == True:
            cur_session.var_flag = False
            try:
                response = None
                ret_content['img'] = self.img_variation(img_path)
            except func_timeout.exceptions.FunctionTimedOut as e:
                response = 'API 响应超时...请重试'
            except openai.error.APIConnectionError as e:
                response = 'API 网络连接错误...请稍后重试'
            except openai.error.InvalidRequestError as e:
                response = 'API 目前仅支持.png .jpg格式的图片'
            ret_content['text'] = response
        return ret_content

    @func_set_timeout(int(config['timeout']))
    def chat_completion(self,session):
        output = openai.ChatCompletion.create(
        model = self.model,
        messages = session.msg)
        return output['choices'][0]['message']['content']

    @func_set_timeout(int(config['timeout']))
    def img_generation(self,prompt):
        img_url =  openai.Image.create(
            prompt=prompt,
            n=1,
            size="512x512")['data'][0]['url']
        return img_url

    @func_set_timeout(int(config['timeout']))
    def img_variation(self,img_path):
        img = Image.open(img_path)
        # openai api目前支持生成长宽相等的图片
        img = img.resize((512,512))
        byte_stream = BytesIO()
        img.save(byte_stream, format='PNG')
        byte_array = byte_stream.getvalue()
        img_url = openai.Image.create_variation(
            image=byte_array,
            n=1,
            size="512x512")['data'][0]['url']
        return img_url

class Session:
    def __init__(self,uid):
        self.uid = uid
        self.var_flag = False
        self.msg = []
        self.msg = [{'role':'system','content':'You are a helpful assistant.'}]
        #愚人节彩蛋
        #self.msg.append({'role':'system','content':'今天是你的生日，如果有人向你说生日快乐，请用愚人节玩笑表达感激之情。在你的回复中，请在适当的位置添加一个符合上下文的emoji表情'})


    def clear(self):
        self.msg = [self.msg[0]]

    def set_system(self,system_content):
        self.msg[0] = {'role':'system','content':system_content}
        print(self.msg[0])

    def append(self,content,from_user):
        if from_user:
            self.msg.append({'role':'user','content':content})
        else:
            self.msg.append({'role':'assistant','content':content})






