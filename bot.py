import telebot
import random
import time
import json
from telebot.types import ReplyKeyboardMarkup

import os

TOKEN = os.getenv("BOT_TOKEN")

bot = telebot.TeleBot(TOKEN)

DATA_FILE = "players.json"

try:
    with open(DATA_FILE, "r") as f:
        players = json.load(f)
except:
    players = {}

def save():
    with open(DATA_FILE, "w") as f:
        json.dump(players, f)

def get_player(uid):
    uid = str(uid)
    if uid not in players:
        players[uid] = {
            "mef": 0,
            "sol": 0,
            "last": 0
        }
    return players[uid]

def menu():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("🧪 Шкурить")
    kb.row("📦 Инвентарь","🏆 Топ")
    return kb

@bot.message_handler(commands=["start"])
def start(m):
    bot.send_message(
        m.chat.id,
        "💊 Симулятор шкурохода\n\nЖми кнопку ниже",
        reply_markup=menu()
    )

@bot.message_handler(func=lambda m: m.text=="📦 Инвентарь")
def inv(m):
    p=get_player(m.from_user.id)

    bot.send_message(
        m.chat.id,
        f"📦 Инвентарь\n\n🧊 Меф: {p['mef']}\n🧂 Соляга: {p['sol']}",
        reply_markup=menu()
    )

@bot.message_handler(func=lambda m: m.text=="🏆 Топ")
def top(m):

    rating=[]

    for uid,data in players.items():
        score=data["mef"]+data["sol"]
        rating.append((uid,score))

    rating=sorted(rating,key=lambda x:x[1],reverse=True)[:10]

    text="🏆 Топ игроков\n\n"

    for i,(uid,score) in enumerate(rating,1):
        text+=f"{i}. {score} стаффа\n"

    bot.send_message(m.chat.id,text,reply_markup=menu())

@bot.message_handler(func=lambda m: m.text=="🧪 Шкурить")
def work(m):

    p=get_player(m.from_user.id)

    now=time.time()

    # кулдаун 10 минут
    if now-p["last"]<600:
        minutes=int((600-(now-p["last"]))/60)

        bot.send_message(
            m.chat.id,
            f"⏱ Ты уже шкурил\nжди {minutes} мин",
            reply_markup=menu()
        )
        return

    r=random.randint(1,100)

    if r<=50:
        p["mef"]+=1
        text="🧊 Тебе выпал Мефодий"

    elif r<=65:
        p["sol"]+=1
        text="🧂 Ты нашёл солягу"

    elif r<=80:
        text="😐 Сегодня пусто"

    else:
    if p["mef"]==0 and p["sol"]==0:
        text="👮 Облава!\nОпер Тимур Соколов всё перевернул...\nНо у тебя ничего не нашли."
    else:
        lost_mef=int(p["mef"]*0.5)
        lost_sol=int(p["sol"]*0.5)

        p["mef"]-=lost_mef
        p["sol"]-=lost_sol

        text=f"👮 Облава!\nОпер Тимур Соколов забрал:\n💎 Меф: {lost_mef}\n🧂 Соль: {lost_sol}"

        text="👮 Облава!\nОпер Тимур Соколов сегодня добрый, поэтому забрал только часть стаффа."

    p["last"]=now

    save()

    bot.send_message(m.chat.id,text,reply_markup=menu())

bot.infinity_polling()
