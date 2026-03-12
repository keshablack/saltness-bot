import telebot
import random
import time
import json
from telebot.types import ReplyKeyboardMarkup
import os

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

DATA_FILE = os.getenv("DATA_FILE","players.json")

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
            "total":0,
            "ref":None,
            "refs":0,
            "ref_reward":0
        }

    p = players[uid]

    # фикс старых игроков
    p.setdefault("ref",None)
    p.setdefault("refs",0)
    p.setdefault("ref_reward",0)

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
    kb.row("👥 Реферальная ссылка")
    kb.row("⬅️ Назад")

    return kb

def lab_menu():

    kb=ReplyKeyboardMarkup(resize_keyboard=True)

    kb.row("👨‍🔬 Варить")
    kb.row("⬆ Апгрейд лаборатории")
    kb.row("📦 Инвентарь","⬅️ Назад")

    return kb


# ===== НАЗАД =====

@bot.message_handler(func=lambda m: m.text=="⬅️ Назад")
def back(m):

    bot.send_message(
        m.chat.id,
        "🏠 Главное меню",
        reply_markup=menu()
    )


# ===== СТАРТ =====

@bot.message_handler(commands=["start"])
def start(m):

    p=get_player(m.from_user)

    args=m.text.split()

    if len(args)>1:

        ref_id=args[1]

        if ref_id!=str(m.from_user.id) and not p.get("ref"):

            if ref_id in players:

                players[ref_id]["sol"]+=5
                players[ref_id]["refs"]+=1
                players[ref_id]["ref_reward"]+=5

                p["ref"]=ref_id

                bot.send_message(
                    m.chat.id,
                    "🎉 Ты зарегистрировался по реферальной ссылке!"
                )

    save()

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

@bot.message_handler(func=lambda m: m.text=="🏆 Топ")
def top(m):

    top_farm = sorted(players.values(), key=lambda x: x.get("total",0), reverse=True)[:10]
    top_refs = sorted(players.values(), key=lambda x: x.get("refs",0), reverse=True)[:10]

    text = "🏆 Топ шкуроходов\n\n"

    for i,p in enumerate(top_farm,1):
        text += f"{i}. {p['name']} — {p.get('total',0)} стаффа\n"

    text += "\n👥 Топ рефералов\n\n"

    for i,p in enumerate(top_refs,1):
        text += f"{i}. {p['name']} — {p.get('refs',0)} друзей\n"

    bot.send_message(m.chat.id, text, reply_markup=menu())


# ===== КРАКЕН =====

@bot.message_handler(func=lambda m:m.text=="🐙 Кракен")
def kraken(m):

    bot.send_message(
        m.chat.id,
        "🐙 Кракен маркет",
        reply_markup=kraken_menu()
    )


# ===== РЕФЕРАЛКА =====

@bot.message_handler(func=lambda m:m.text=="👥 Реферальная ссылка")
def ref_link(m):

    p=get_player(m.from_user)

    uid = str(m.from_user.id)

    bot_info = bot.get_me()

    link = f"https://t.me/{bot_info.username}?start={uid}"

    bot.send_message(
        m.chat.id,
        f"""
👥 Реферальная система

🧑‍🤝‍🧑 Приглашено друзей: {p['refs']}
🎁 Получено наград: {p['ref_reward']} соли

За каждого друга:
🧂 +5 соли

Твоя ссылка:

{link}
""",
        reply_markup=kraken_menu()
    )

    
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

    cooldown=180-(p["lvl"]*4)-(p["lab_lvl"]*10)

if cooldown<30:
    cooldown=30

    if now-p["last"]<cooldown:

        seconds=int(cooldown-(now-p["last"]))

        bot.send_message(
            m.chat.id,
            f"⏱ Ну ты чайка, потерпи еще {seconds} сек",
            reply_markup=menu()
        )
        return


    r=random.randint(1,100)
    amount=random.randint(1,3)

    p["xp"]+=1

# ===== ПРОКАЧКА =====
need=p["lvl"]*10

while p["xp"]>=need:

    p["xp"]-=need
    p["lvl"]+=1

    bot.send_message(
        m.chat.id,
        f"""
⭐ Новый уровень!

Теперь ты {p['lvl']} уровень

⏱ Кулдаун шкурки уменьшен на 4 сек
"""
    )


    # ===== МАСТЕРКЛАД (3%) =====
    if r<=3:

        p["mef"]+=10
        p["total"]+=10

        with open("masterklad.PNG","rb") as photo:

            bot.send_photo(
                m.chat.id,
                photo,
                caption=f"""
💎 МАСТЕРКЛАД

Ого… ты сошкурил чей-то мастерклад

🧊 +10г мефа

📦 Теперь у тебя:
🧊 {p['mef']}г
🧂 {p['sol']}г
💰 {p['money']}₽
""",
                reply_markup=menu()
            )


    # ===== МЕФ (20%) =====
    elif r<=23:

        p["mef"]+=amount
        p["total"]+=amount

        with open("mef.jpg","rb") as photo:

            bot.send_photo(
                m.chat.id,
                photo,
                caption=f"""
🧊 Ты сошкурил клад

🧊 Меф: +{amount}г

📦 Сейчас у тебя:
🧊 {p['mef']}г
🧂 {p['sol']}г
💰 {p['money']}₽
""",
                reply_markup=menu()
            )


    # ===== СОЛЬ (30%) =====
    elif r<=53:

        p["sol"]+=amount
        p["total"]+=amount

        with open("salt.jpg","rb") as photo:

            bot.send_photo(
                m.chat.id,
                photo,
                caption=f"""
🧂 Ты сошкурил клад

🧂 Соль: +{amount}г

📦 Сейчас у тебя:
🧊 {p['mef']}г
🧂 {p['sol']}г
💰 {p['money']}₽
""",
                reply_markup=menu()
            )


    # ===== ПУСТО (27%) =====
    elif r<=80:

        with open("pusto.png.jpg","rb") as photo:

            bot.send_photo(
                m.chat.id,
                photo,
                caption="😐 Вот не повезло, пусто",
                reply_markup=menu()
            )


    # ===== ОПЕР (20%) =====
    else:

        if p["mef"]+p["sol"]==0:

            with open("oper.PNG","rb") as photo:

                bot.send_photo(
                    m.chat.id,
                    photo,
                    caption="👮 Опер Тимур Соколов принял тебя, но у тебя ничего не нашли",
                    reply_markup=menu()
                )

        else:

            lost_mef=int(p["mef"]*0.5)
            lost_sol=int(p["sol"]*0.5)

            p["mef"]-=lost_mef
            p["sol"]-=lost_sol

            with open("oper.PNG","rb") as photo:

                bot.send_photo(
                    m.chat.id,
                    photo,
                    caption=f"""
👮 Опер Тимур Соколов

Забрал часть стаффа

🧊 -{lost_mef}
🧂 -{lost_sol}
""",
                    reply_markup=menu()
                )


    p["last"]=now

    save()


# ===== ЛАБОРАТОРИЯ =====

@bot.message_handler(func=lambda m:m.text=="👨‍🔬 Варить")
def cook(m):

    p=get_player(m.from_user)

    now=time.time()

    cooldown=600-(p["lab_lvl"]*30)

    if now-p["lab_last"]<cooldown:

        seconds=int(cooldown-(now-p["lab_last"]))

        bot.send_message(
            m.chat.id,
            f"⏱️ Варка ещё идёт\nОсталось {seconds} сек",
            reply_markup=lab_menu()
        )
        return


    gain=p["lab_lvl"]*2

    p["mef"]+=gain
    p["total"]+=gain
    p["lab_last"]=now

    save()

    with open("var.PNG","rb") as photo:

        bot.send_photo(
            m.chat.id,
            photo,
            caption=f"""
🧪 Стёпа сварил стафф

🧊 +{gain} мефа

📦 Теперь у тебя:

🧊 {p['mef']} мефа
🧂 {p['sol']} соли
💰 {p['money']}₽
""",
            reply_markup=lab_menu()
        )


@bot.message_handler(func=lambda m: "Апгрейд лаборатории" in m.text if m.text else False)
def lab_upgrade(m):

    p=get_player(m.from_user)

    prices={
        1:10000,
        2:30000,
        3:80000,
        4:250000
    }

    if p["lab_lvl"]>=5:

        bot.send_message(
            m.chat.id,
            "🏭 Лаборатория уже максимального уровня",
            reply_markup=lab_menu()
        )
        return

    price=prices[p["lab_lvl"]]

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
""",
        reply_markup=lab_menu()
    )


@bot.message_handler(func=lambda m:m.text=="🧪 Лаборатория")
def lab(m):

    p=get_player(m.from_user)

    prices={
        1:10000,
        2:30000,
        3:80000,
        4:250000
    }

    images={
        1:"images/laba1.PNG",
        2:"images/laba2.PNG",
        3:"images/laba3.PNG",
        4:"images/laba4.jpg",
        5:"images/laba5.PNG"
    }

    bonus=p["lab_lvl"]*5
    cooldown=p["lab_lvl"]*30

    if p["lab_lvl"]>=5:
        upgrade_text="🏭 Максимальный уровень"
    else:
        upgrade_text=f"💰 Апгрейд лаборатории — {prices[p['lab_lvl']]}₽"

    img=images.get(p["lab_lvl"],"images/laba1.PNG")

    with open(img,"rb") as photo:
        bot.send_photo(
            m.chat.id,
            photo,
            caption=f"""
🧪 Лаборатория Стёпы

👨‍🔬 Стёпа варщик: нанят
🏭 Уровень лаборатории: {p['lab_lvl']}

Бонусы:
+{bonus}% шанс мефа
−{cooldown} сек кулдаун

{upgrade_text}
""",
            reply_markup=lab_menu()
        )


bot.infinity_polling()
