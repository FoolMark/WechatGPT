from wechat_utils import *
from openai_utils import *
openai_robot = OpenAIRobot()
wechat_robot = WechatTool(robot=openai_robot)

@itchat.msg_register(itchat.content.TEXT)
def process_msg(msg):
    global wechat_robot
    wechat_robot.on_recv_text(msg)

@itchat.msg_register(itchat.content.PICTURE)
def process_img(msg):
    global wechat_robot
    wechat_robot.on_recv_img(msg)

wechat_robot.start()

