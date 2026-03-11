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
    with open(DATA_FILE,"r") as f:
        players=json.load(f)
except:
    players={}

def save():
    with open(DATA_FILE,"w") as f:
        json.dump(players,f)

def get_player(user):

    uid=str(user.id)

    if uid not in players:

        players[uid]={
            "name":user.first_name,
            "mef":0,
            "sol":0,
            "money":0,
            "xp":0,
            "lvl":1,
            "last":0,
            "roulette":False,
            "lab_lvl":1,
            "lab_last":0
        }

    players[uid]["name"]=user.first_name
    return players[uid]


# ===== МЕНЮ =====

def menu():

    kb=ReplyKeyboardMarkup(resize_keyboard=True)

    kb.row("🧪 Шкурить")
    kb.row("📦 Инвентарь","🏆 Топ")
    kb.row("🐙 Кракен","🧪 Лаборатория")

    return kb


def kraken_menu():

    kb=ReplyKeyboardMarkup(resize_keyboard=True)

    kb.row("💰 Продать стафф")
    kb.row("🎰 Рулетка ₽","🧊 Рулетка Меф")
    kb.row("⬅ Назад")

    return kb


def lab_menu():

    kb=ReplyKeyboardMarkup(resize_keyboard=True)

    kb.row("👨‍🔬 Варить")
    kb.row("⬆ Апгрейд")
    kb.row("⬅ Назад")

    return kb


# ===== СТАРТ =====

@bot.message_handler(commands=["start"])
def start(m):

    bot.send_message(
        m.chat.id,
        "💊 Симулятор шкурохода",
        reply_markup=menu()
    )


# ===== ИНВЕНТАРЬ =====

@bot.message_handler(func=lambda m:m.text=="📦 Инвентарь")
def inv(m):

    p=get_player(m.from_user)

    bot.send_message(
        m.chat.id,
        f"""
📦 Инвентарь

🧊 Меф: {p['mef']}
🧂 Соль: {p['sol']}

💰 Деньги: {p['money']}₽
⭐ Уровень: {p['lvl']}
XP: {p['xp']}/{p['lvl']*10}
""",
        reply_markup=menu()
    )


# ===== ТОП =====

@bot.message_handler(func=lambda m:m.text=="🏆 Топ")
def top(m):

    rating=[]

    for uid,data in players.items():

        score=data["mef"]+data["sol"]
        rating.append((data["name"],score))

    rating=sorted(rating,key=lambda x:x[1],reverse=True)[:10]

    text="🏆 Топ игроков\n\n"

    for i,(name,score) in enumerate(rating,1):

        text+=f"{i}. {name} — {score}\n"

    bot.send_message(m.chat.id,text,reply_markup=menu())


# ===== КРАКЕН =====

@bot.message_handler(func=lambda m:m.text=="🐙 Кракен")
def kraken(m):

    bot.send_message(
        m.chat.id,
        "🐙 Кракен маркет",
        reply_markup=kraken_menu()
    )


@bot.message_handler(func=lambda m:m.text=="⬅ Назад")
def back(m):

    bot.send_message(m.chat.id,"Главное меню",reply_markup=menu())


# ===== ПРОДАЖА =====

@bot.message_handler(func=lambda m:m.text=="💰 Продать стафф")
def sell(m):

    p=get_player(m.from_user)

    money=(p["mef"]*3000)+(p["sol"]*1500)

    if money==0:

        bot.send_message(m.chat.id,"Нечего продавать",reply_markup=kraken_menu())
        return

    p["money"]+=money
    p["mef"]=0
    p["sol"]=0

    save()

    bot.send_message(m.chat.id,f"💰 +{money}₽",reply_markup=kraken_menu())


# ===== РУЛЕТКА МЕФ =====

@bot.message_handler(func=lambda m:m.text=="🧊 Рулетка Меф")
def mef_start(m):

    p=get_player(m.from_user)

    if p["money"]<1500:

        bot.send_message(m.chat.id,"💸 Нужно 1500₽",reply_markup=kraken_menu())
        return

    p["money"]-=1500
    p["roulette"]=True
    save()

    bot.send_message(m.chat.id,"🎰 Число 1-10")


# ===== РУЛЕТКА ₽ =====

@bot.message_handler(func=lambda m:m.text=="🎰 Рулетка ₽")
def rub_start(m):

    p=get_player(m.from_user)

    if p["money"]<1000:

        bot.send_message(m.chat.id,"💸 Нужно 1000₽",reply_markup=kraken_menu())
        return

    p["money"]-=1000

    if random.randint(1,2)==1:

        win=2000
        p["money"]+=win
        text=f"🎉 Ты выиграл {win}₽"

    else:

        text="😐 Ты проиграл"

    save()

    bot.send_message(m.chat.id,text,reply_markup=kraken_menu())


# ===== ЧИСЛО РУЛЕТКИ =====

@bot.message_handler(func=lambda m:m.text.isdigit())
def roulette_play(m):

    p=get_player(m.from_user)

    if not p["roulette"]:
        return

    num=int(m.text)

    if num<1 or num>10:
        return

    win=random.randint(1,10)

    if num==win:

        p["mef"]+=5
        text=f"🎉 Угадал {win}\n🧊 +5 мефа"

    else:

        text=f"😐 Выпало {win}"

    p["roulette"]=False

    save()

    bot.send_message(m.chat.id,text,reply_markup=kraken_menu())


# ===== ЛАБОРАТОРИЯ =====

@bot.message_handler(func=lambda m:m.text=="🧪 Лаборатория")
def lab(m):

    p=get_player(m.from_user)

    bot.send_message(
        m.chat.id,
        f"""
🧪 Лаборатория Стёпы

👨‍🔬 уровень: {p['lab_lvl']}
""",
        reply_markup=lab_menu()
    )


@bot.message_handler(func=lambda m:m.text=="👨‍🔬 Варить")
def cook(m):

    p=get_player(m.from_user)

    now=time.time()

    cooldown=600-(p["lab_lvl"]*30)

    if now-p["lab_last"]<cooldown:

        bot.send_message(m.chat.id,"⏱ ещё варится",reply_markup=lab_menu())
        return

    gain=p["lab_lvl"]

    p["mef"]+=gain
    p["lab_last"]=now

    save()

    bot.send_message(m.chat.id,f"🧊 Стёпа сварил {gain} мефа",reply_markup=lab_menu())


@bot.message_handler(func=lambda m:m.text=="⬆ Апгрейд")
def lab_upgrade(m):

    p=get_player(m.from_user)

    price=p["lab_lvl"]*5000

    if p["money"]<price:

        bot.send_message(m.chat.id,f"💸 Нужно {price}₽",reply_markup=lab_menu())
        return

    p["money"]-=price
    p["lab_lvl"]+=1

    save()

    bot.send_message(m.chat.id,"⬆ лаборатория улучшена",reply_markup=lab_menu())


# ===== ШКУРКА =====

@bot.message_handler(func=lambda m:m.text=="🧪 Шкурить")
def work(m):

    p=get_player(m.from_user)

    now=time.time()

    if now-p["last"]<180:

        bot.send_message(m.chat.id,"⏱ подожди",reply_markup=menu())
        return

    r=random.randint(1,100)

    if r<=50:
        p["mef"]+=1
        text="🧊 меф"

    elif r<=65:
        p["sol"]+=1
        text="🧂 соль"

    elif r<=80:
        text="😐 пусто"

    else:

        if p["mef"]+p["sol"]==0:

            text="👮 облава но ничего не нашли"

        else:

            lost_mef=int(p["mef"]*0.5)
            lost_sol=int(p["sol"]*0.5)

            p["mef"]-=lost_mef
            p["sol"]-=lost_sol

            text=f"👮 забрали\n🧊{lost_mef}\n🧂{lost_sol}"

    p["last"]=now
    save()

    bot.send_message(m.chat.id,text,reply_markup=menu())


bot.infinity_polling()
