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

def get_player(user):
    uid = str(user.id)

    if uid not in players:
        players[uid] = {
            "name": user.first_name,
            "mef": 0,
            "sol": 0,
            "money": 0,
            "xp": 0,
            "lvl": 1,
            "last": 0,
            "roulette": False
        }

    players[uid]["name"] = user.first_name
    return players[uid]


# ===== МЕНЮ =====

def menu():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)

    kb.row("🧪 Шкурить")
    kb.row("📦 Инвентарь", "🏆 Топ")
    kb.row("🐙 Кракен")

    return kb

def kraken_menu():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("💰 Продать стафф")
    kb.row("🎰 Рулетка ₽","🧊 Рулетка Меф")
    kb.row("⬅ Назад")
    return kb


# ===== СТАРТ =====

@bot.message_handler(commands=["start"])
def start(m):
    bot.send_message(
        m.chat.id,
        "💊 Симулятор шкурохода\n\nЖми кнопку ниже",
        reply_markup=menu()
    )


# ===== ИНВЕНТАРЬ =====

@bot.message_handler(func=lambda m: m.text=="📦 Инвентарь")
def inv(m):
    p=get_player(m.from_user)

    bot.send_message(
        m.chat.id,
        f"""📦 Инвентарь

🧊 Меф: {p['mef']}
🧂 Соляга: {p['sol']}

💰 Деньги: {p['money']}₽
⭐ Уровень: {p['lvl']}
XP: {p['xp']}/{p['lvl']*10}
""",
        reply_markup=menu()
    )


# ===== ТОП =====

@bot.message_handler(func=lambda m: m.text=="🏆 Топ")
def top(m):

    rating=[]

    for uid,data in players.items():
        score=data["mef"]+data["sol"]
        rating.append((data["name"],score))

    rating=sorted(rating,key=lambda x:x[1],reverse=True)[:10]

    text="🏆 Топ игроков\n\n"

    for i,(name,score) in enumerate(rating,1):
        text+=f"{i}. {name} — {score} стаффа\n"

    bot.send_message(m.chat.id,text,reply_markup=menu())


# ===== КРАКЕН =====

@bot.message_handler(func=lambda m: m.text=="🐙 Кракен")
def kraken(m):

    bot.send_message(
        m.chat.id,
        "🐙 Добро пожаловать на Кракен\n\nЗдесь можно продать стафф",
        reply_markup=kraken_menu()
    )


@bot.message_handler(func=lambda m: m.text=="⬅ Назад")
def back(m):

    bot.send_message(
        m.chat.id,
        "Главное меню",
        reply_markup=menu()
    )


@bot.message_handler(func=lambda m: m.text=="💰 Продать стафф")
def sell(m):

    p=get_player(m.from_user)

    money=(p["mef"]*3000)+(p["sol"]*1500)

    if money==0:
        bot.send_message(m.chat.id,"У тебя нечего продавать.",reply_markup=kraken_menu())
        return

    p["money"]+=money
    p["mef"]=0
    p["sol"]=0

    save()

    bot.send_message(m.chat.id,f"💰 Ты продал стафф на {money}₽",reply_markup=kraken_menu())
    
@bot.message_handler(func=lambda m: m.text=="🧊 Рулетка Меф")
def mef_roulette_start(m):

    p=get_player(m.from_user)

    if p["money"]<1500:
        bot.send_message(
            m.chat.id,
            "💸 Нужно 1500₽ для игры",
            reply_markup=kraken_menu()
        )
        return

    p["money"]-=1500
    "roulette": False
    save()

    bot.send_message(
        m.chat.id,
        "🎰 Выбери число от 1 до 10"
    )
    
@bot.message_handler(func=lambda m: m.text.isdigit())
def mef_roulette_play(m):

    p=get_player(m.from_user)

    if not p.get("roulette"):
        return

    num=int(m.text)

    if num<1 or num>10:
        bot.send_message(m.chat.id,"Выбери число от 1 до 10")
        return

    win=random.randint(1,10)

    if num==win:
        p["mef"]+=5
        text=f"🎉 Ты угадал число {win}!\n\n🧊 +5 мефа"
    else:
        text=f"😐 Выпало число {win}\nТы проиграл."

    p["roulette"]=False

    save()

    bot.send_message(
        m.chat.id,
        text,
        reply_markup=kraken_menu()
    )

# ===== ШКУРКА =====

@bot.message_handler(func=lambda m: m.text=="🧪 Шкурить")
def work(m):

    p=get_player(m.from_user)

    now=time.time()

    # кулдаун 3 минуты
    if now-p["last"]<180:

        minutes=int((180-(now-p["last"]))/60)+1

        bot.send_message(
            m.chat.id,
            f"⏱ Ты уже шкурил\nжди {minutes} мин",
            reply_markup=menu()
        )
        return

    r=random.randint(1,100)

    # XP
    p["xp"]+=1

    if p["xp"]>=p["lvl"]*10:
        p["xp"]=0
        p["lvl"]+=1
        bot.send_message(m.chat.id,f"🎉 Новый уровень: {p['lvl']}")

    # выпадение
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

            text=f"""👮 Облава!

Опер Тимур Соколов сегодня добрый,
поэтому забрал только часть стаффа.

🧊 Меф: -{lost_mef}
🧂 Соль: -{lost_sol}
"""

    p["last"]=now

    save()

    bot.send_message(m.chat.id,text,reply_markup=menu())


bot.infinity_polling()
