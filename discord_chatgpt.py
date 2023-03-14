import discord
import requests
import openai
import json
import os
import dotenv

dotenv.load_dotenv()
openai_key = os.getenv("OPENAI_KEY")
TOKEN = os.getenv("BOT_TOKEN")
user_id = int(os.getenv("USER_ID"))
channel_id = int(os.getenv("CHANNEL_ID"))

openai.api_key = openai_key
endpoint = "https://api.chatgpt.com/v1/chat"

# インテントオブジェクトを作成
intents = discord.Intents.all()
intents.members = True

def load_system_content(past_messages):
    with open("system_content.txt", "r") as f:
        system_content = f.read()
        system = {"role": "system", "content": system_content}
        past_messages.append(system)
        return

# 履歴読み込み
path = "./messages.json"
past_messages:list = []
if os.path.isfile(path):
    with open(path, "r") as f:
        past_messages = json.load(f)
if len(past_messages) == 0:
    load_system_content(past_messages)

# botの接続
client = discord.Client(intents=intents)



# 起動時
@client.event
async def on_ready():
    print('ログインしました')

# メッセージ受信時
@client.event
async def on_message(message):
    # 指定したチャンネルとユーザーでないと反応しない
    if message.author.bot or message.channel.id != channel_id or message.author.id != user_id:
        return print(message.content)
    
    if message.content == '/deletememory':
        past_messages.clear()
        load_system_content(past_messages)
        return print("記憶を消去しました")

    user_message = {"role": "user", "content": message.content}
    past_messages.append(user_message)
    response = openai.ChatCompletion.create(
      model="gpt-3.5-turbo",
      messages=past_messages,
      temperature=0.9,
      frequency_penalty=0.6,
      presence_penalty=0.6,
    )
    response_message = {"role": "assistant", "content": response.choices[0].message.content}
    past_messages.append(response_message)
    with open(path, "w") as f:
        json.dump(past_messages, f)
    await message.channel.send(response['choices'][0]['message']['content'])



client.run(TOKEN)