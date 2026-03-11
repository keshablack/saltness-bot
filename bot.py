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
            "lab_last":0,
            "total":0
        }

    players[uid]["name"]=user.first_name
    return players[uid]


# ===== МЕНЮ =====

def menu():

    kb=ReplyKeyboardMarkup(resize_keyboard=True)

    kb.row("🧪 Шкурить")
    kb.row("📦 Инвентарь","🐙 Кракен")
    kb.row("🧪 Лаборатория","🏆 Топ")

    return kb


def kraken_menu():

    kb=ReplyKeyboardMarkup(resize_keyboard=True)

    kb.row("💰 Продать стафф")
    kb.row("🎰 Рулетка ₽","🧊 Рулетка Меф")
    kb.row("📦 Инвентарь","⬅ Назад")

    return kb


def lab_menu():

    kb=ReplyKeyboardMarkup(resize_keyboard=True)

    kb.row("👨‍🔬 Варить")
    kb.row("⬆ Апгрейд лаборатории")
    kb.row("📦 Инвентарь","⬅ Назад")

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

    username=m.from_user.username
    if username:
        username="@"+username
    else:
        username=m.from_user.first_name

    bot.send_message(
        m.chat.id,
        f"""
📦 Инвентарь {username}

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
        rating.append((data["name"],data.get("total",0)))

    rating=sorted(rating,key=lambda x:x[1],reverse=True)[:10]

    text="🏆 Топ шкуроходов\n\n"

    for i,(name,score) in enumerate(rating,1):
        text+=f"{i}. {name} — {score} стаффа\n"

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

    bot.send_message(
        m.chat.id,
        f"""
💰 Продажа

Ты получил {money}₽

Баланс: {p['money']}₽
""",
        reply_markup=kraken_menu()
    )


# ===== РУЛЕТКА ₽ =====

@bot.message_handler(func=lambda m:m.text=="🎰 Рулетка ₽")
def rub_start(m):

    p=get_player(m.from_user)

    if p["money"]<1000:

        bot.send_message(
            m.chat.id,
            "💸 Нужно 1000₽ для игры",
            reply_markup=kraken_menu()
        )
        return

    p["money"]-=1000
    save()

    msg=bot.send_message(m.chat.id,"🎰 Крутим рулетку...")

    animation=[
        "🎰 | 🔴 ⚫ ⚫ |",
        "🎰 | ⚫ 🔴 ⚫ |",
        "🎰 | ⚫ ⚫ 🔴 |",
        "🎰 | 🔴 ⚫ ⚫ |",
        "🎰 | ⚫ 🔴 ⚫ |"
    ]

    for frame in animation:

        time.sleep(0.6)

        bot.edit_message_text(
            frame,
            m.chat.id,
            msg.message_id
        )

    if random.randint(1,2)==1:

        win=2000
        p["money"]+=win

        result=f"""
🎰 Рулетка

🎉 Ты выиграл {win}₽

💰 Баланс: {p['money']}₽
"""

    else:

        result=f"""
🎰 Рулетка

😐 Ты проиграл

💰 Баланс: {p['money']}₽
"""

    save()

    bot.edit_message_text(
        result,
        m.chat.id,
        msg.message_id
    )


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

    bot.send_message(m.chat.id,"🎰 Выбери число от 1 до 10")


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

        text=f"""
🎰 Рулетка Меф

🎉 Угадал число {win}

🧊 +5 мефа

Теперь у тебя:
🧊 {p['mef']} мефа
🧂 {p['sol']} соли
"""

    else:

        text=f"""
🎰 Рулетка Меф

😐 Выпало число {win}

📦 У тебя осталось:
🧊 {p['mef']} мефа
🧂 {p['sol']} соли
"""

    p["roulette"]=False

    save()

    bot.send_message(m.chat.id,text,reply_markup=kraken_menu())


# ===== ШКУРКА =====

@bot.message_handler(func=lambda m:m.text=="🧪 Шкурить")
def work(m):

    p=get_player(m.from_user)

    now=time.time()

    cooldown=180-(p["lab_lvl"]*10)

    if now-p["last"]<cooldown:

        seconds=int(cooldown-(now-p["last"]))

        bot.send_message(
            m.chat.id,
            f"⏱ Следующая шкурка через {seconds} сек",
            reply_markup=menu()
        )
        return

    bonus=p["lab_lvl"]*2
    r=random.randint(1,100-bonus)

    p["xp"]+=1

    if r<=50:

        p["mef"]+=1
        p["total"]+=1
        text="🧊 Ты сошкурил меф"

    elif r<=65:

        p["sol"]+=1
        p["total"]+=1
        text="🧂 Ты нашёл солягу"

    elif r<=80:

        text="😐 Сегодня пусто"

    else:

        if p["mef"]+p["sol"]==0:

            text="👮 Облава, но у тебя ничего не нашли"

        else:

            lost_mef=int(p["mef"]*0.5)
            lost_sol=int(p["sol"]*0.5)

            p["mef"]-=lost_mef
            p["sol"]-=lost_sol

            text=f"👮 Забрали {lost_mef} мефа и {lost_sol} соли"


    p["last"]=now

    save()

    bot.send_message(
        m.chat.id,
        f"""
{text}

📦 Сейчас у тебя:

🧊 Меф: {p['mef']}
🧂 Соль: {p['sol']}
💰 Деньги: {p['money']}₽
""",
        reply_markup=menu()
    )


    # ===== ЛАБОРАТОРИЯ =====

@bot.message_handler(func=lambda m:m.text=="🧪 Лаборатория")
def lab(m):

    p=get_player(m.from_user)

    bonus=p["lab_lvl"]*5
    cooldown=p["lab_lvl"]*30
    price=p["lab_lvl"]*5000

    bot.send_message(
        m.chat.id,
        f"""
🧪 Лаборатория Стёпы

👨‍🔬 Стёпа варщик: нанят
🏭 Уровень лаборатории: {p['lab_lvl']}

Бонусы:
+{bonus}% шанс мефа
−{cooldown} сек кулдаун

💰 Апгрейд лаборатории — {price}₽
""",
        reply_markup=lab_menu()
    )


@bot.message_handler(func=lambda m:m.text=="👨‍🔬 Варить")
def cook(m):

    p=get_player(m.from_user)

    now=time.time()

    cooldown=600-(p["lab_lvl"]*30)

    if now-p["lab_last"]<cooldown:

        seconds=int(cooldown-(now-p["lab_last"]))

        bot.send_message(
            m.chat.id,
            f"⏱ Варка ещё идёт\nОсталось {seconds} сек",
            reply_markup=lab_menu()
        )
        return

    gain=p["lab_lvl"]*2

    p["mef"]+=gain
    p["total"]+=gain
    p["lab_last"]=now

    save()

    bot.send_message(
        m.chat.id,
        f"""
🧪 Стёпа сварил стафф

🧊 +{gain} мефа

📦 Теперь у тебя:
🧊 {p['mef']} мефа
🧂 {p['sol']} соли
""",
        reply_markup=lab_menu()
    )


@bot.message_handler(func=lambda m:m.text=="⬆ Апгрейд лаборатории")
def lab_upgrade(m):

    p=get_player(m.from_user)

    price=p["lab_lvl"]*5000

    if p["money"]<price:

        bot.send_message(
            m.chat.id,
            f"💸 Нужно {price}₽ для апгрейда",
            reply_markup=lab_menu()
        )
        return

    p["money"]-=price
    p["lab_lvl"]+=1

    save()

    bot.send_message(
        m.chat.id,
        f"""
⬆ Лаборатория улучшена!

🏭 Новый уровень: {p['lab_lvl']}

Теперь:
+{p['lab_lvl']*5}% шанс мефа
−{p['lab_lvl']*30} сек кулдаун
""",
        reply_markup=lab_menu()
    )


bot.infinity_polling()
