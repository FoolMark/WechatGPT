# WechatGPT: 微信chatGPT聊天机器人
- 调用[chatGPT API](https://platform.openai.com/docs/api-reference/introduction)实现自动聊天、根据文字生成图像等功能
- 微信端信息收发参考[itchat](https://github.com/littlecodersh/ItChat)，部分新注册的微信号可能无法使用itchat，建议用[itchat-uos](https://github.com/why2lyj/ItChat-UOS)替代(具体api可能有所不同)

# Get Started 
- Requirements: python 3.8 ||   ```pip install -r requirements.txt```
- ```config/user.yaml```: 在此指定master_name(微信主账号)和user_name(自动回复的对象)
- ```config/config.yaml```: 在此指定你的openai_api_key(OpenAI官网申请)以及GPT模型(详见[Link](https://platform.openai.com/docs/api-reference/introduction)，***本repo中提供的api_key不保证一直有效*** )，设置回复响应等待时间(s)
- 运行程序： ```python run.py``` 扫码登陆微信即可，log in time out问题请参考[Link](https://github.com/zhayujie/chatgpt-on-wechat/issues/8)
# Usage
## Master (微信主账号用户)命令
- 以下命令可以在任何对话中使用(建议在<文件传输助手>中输入)，返回命令会在<文件传输助手>中显示
- ```add  <用户昵称>``` 添加用户(自动回复对象)
- ```del  <用户昵称>``` 删除用户
- ```update``` 将当前所有用户写入.yaml文件(下次重启程序时直接载入)
- ```display``` 显示所有用户
## User 命令
- 以下命令在当前对话界面使用(i.e. user与master的对话界面)
- ```help``` 查看帮助文档
- ```clear``` 清空上文对话
- ```sys  <AI设定>``` （默认值为 "You are a helpful assistant."） e.g. ```sys ``` - 指定AI在与用户对话时的设定
- ```img  <图像描述>``` [生成一张符合描述的图像](https://platform.openai.com/docs/api-reference/images/create), e.g. ```img 白色的黑猫```
- ```var + <*.jpg>``` [根据输入图像生成一张略有变化的图像](https://platform.openai.com/docs/api-reference/images/create-variation)， 先发送```var``` ， 收到回复后再发送图像 