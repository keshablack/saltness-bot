from PIL import Image, ImageDraw
import telebot
import random
import time
import json
from telebot.types import ReplyKeyboardMarkup
import os

black_market=False
black_market_end=0

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
            "ref_reward":0,
            "district_time":0,
            "roulette_rub":False
        }

    p = players[uid]

    # фикс старых игроков
    p.setdefault("ref",None)
    p.setdefault("refs",0)
    p.setdefault("ref_reward",0)

    p.setdefault("district_time",0)

    players[uid]["name"]=user.first_name

    return players[uid]

districts={

1:{
"name":"Заречье",
"owner":None,
"income":10000,
"price":225000
},

2:{
"name":"Индустриальный",
"owner":None,
"income":10000,
"price":225000
},

3:{
"name":"Северный",
"owner":None,
"income":6000,
"price":150000
},

4:{
"name":"Зашекснинский",
"owner":None,
"income":14000,
"price":300000
}

}


# ===== ЧЕРНЫЙ РЫНОК =====
def check_black_market():

    global black_market
    global black_market_end

    now=time.time()

    # закрытие рынка
    if black_market and now>black_market_end:
        black_market=False

        for uid in players:
            try:
                bot.send_message(
                    uid,
                    "🚫 ЧЕРНЫЙ РЫНОК ЗАКРЫТ"
                )
            except:
                pass


    # открытие рынка
    if not black_market and random.randint(1,200)==1:
        black_market=True
        black_market_end=now+1200

        for uid in players:
            try:
                bot.send_message(
                    uid,
                    """
🕶 ЧЕРНЫЙ РЫНОК ОТКРЫТ

💎 Меф: 3200₽
🧂 Соль: 1500₽

⏱ Работает 20 минут
"""
                )
            except:
                pass


# ===== МЕНЮ =====

def menu():

    kb=ReplyKeyboardMarkup(resize_keyboard=True)

    kb.row("🧪 Шкурить")
    kb.row("📦 Инвентарь","🐙 Кракен")
    kb.row("🧪 Лаборатория","🏆 Топ")
    kb.add("🗺 Карта города")

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

    check_black_market()

    p=get_player(m.from_user)

    if black_market:
        mef_price=3300
        sol_price=1500
    else:
        mef_price=2200
        sol_price=900

    money=(p["mef"]*mef_price)+(p["sol"]*sol_price)

    if money==0:

        bot.send_message(m.chat.id,"Нечего продавать",reply_markup=kraken_menu())
        return


    tax=int(money*0.20)
    profit=money-tax

    p["money"]+=profit
    p["mef"]=0
    p["sol"]=0

    save()

    bot.send_message(
        m.chat.id,
        f"""
💰 Продажа стаффа

Выгрузил клады на: {money}₽
Комиссия кракена: {tax}₽

Ты получил: {profit}₽
""",
        reply_markup=kraken_menu()
    )

@bot.message_handler(func=lambda m: m.text=="🗺 Карта города")
def city_map(m):

    text="🗺 Карта города\n\n"

    for i,data in districts.items():

        owner = data["owner"] if data["owner"] else "свободно"

        text += f"""
{i}️⃣ {data['name']}
Владелец: {owner}
Доход: {data['income']}₽
Цена: {data['price']}₽

"""

    # команды добавляем ОДИН РАЗ после цикла
    text += """
⚔ Управление районами

💰 купить [номер]
пример: купить 2

💣 напасть [номер]
стоимость атаки: 100.000₽
шанс захвата: 30%

📥 доход районов начисляется каждый час
"""

    with open("map.jpg","rb") as photo:
        bot.send_photo(
            m.chat.id,
            photo,
            caption=text
        )

    with open("map_temp.jpg","rb") as photo:
        bot.send_photo(m.chat.id,photo,caption=text)
        


@bot.message_handler(func=lambda m:m.text.startswith("купить"))
def buy_district(m):

    p=get_player(m.from_user)

    try:
        num=int(m.text.split()[1])
    except:
        bot.send_message(m.chat.id,"Напиши: купить номер_района")
        return

    if num not in districts:
        bot.send_message(m.chat.id,"Такого района нет")
        return

    d=districts[num]

    if d["owner"]:
        bot.send_message(m.chat.id,"Район уже занят")
        return

    if p["money"]<d["price"]:
        bot.send_message(m.chat.id,"Недостаточно денег")
        return

    p["money"]-=d["price"]
    d["owner"]=p["name"]

    save()

    bot.send_message(
        m.chat.id,
        f"🏙 Ты купил район {d['name']}"
    )

def district_income(p):

    now=time.time()

    if now-p["district_time"]<3600:
        return

    total=0

    for d in districts.values():

        if d["owner"]==p["name"]:
            total+=d["income"]

    if total>0:

        p["money"]+=total
        p["district_time"]=now

        print(f"Игрок получил доход районов: {total}")


@bot.message_handler(func=lambda m: m.text.startswith("напасть"))
def attack_district(m):

    p = get_player(m.from_user)

    try:
        num = int(m.text.split()[1])
    except:
        bot.send_message(m.chat.id, "Напиши: напасть номер")
        return

    if num not in districts:
        bot.send_message(m.chat.id, "Нет такого района")
        return

    d = districts[num]

    if d["owner"] == p["name"]:
        bot.send_message(
            m.chat.id,
            "Это твой район, нападать нельзя"
        )
        return

    if not d["owner"]:
        bot.send_message(m.chat.id, "Район свободен")
        return

    if p["money"] < 100000:
        bot.send_message(m.chat.id, "Нужно 100000₽ для нападения")
        return

    p["money"] -= 100000

    chance = random.randint(1, 100)

    if chance <= 30:

        d["owner"] = p["name"]

        bot.send_message(
            m.chat.id,
            f"⚔ Ты захватил район {d['name']}"
        )

    else:

        bot.send_message(
            m.chat.id,
            "💀 Солнвые нарики этого района дали отпор"
        )

    save()


def generate_map():

    img = Image.open("map.jpg")
    draw = ImageDraw.Draw(img)

    areas = {
        1: [(550,650),(850,650),(850,900),(550,900)],
        2: [(500,450),(800,450),(800,650),(500,650)],
        3: [(800,250),(1050,250),(1050,450),(800,450)],
        4: [(1050,450),(1350,450),(1350,700),(1050,700)]
    }

    for i, d in districts.items():

        if d["owner"]:

            draw.polygon(
                areas[i],
                fill=(255,0,0,120)
            )

    img.save("map_temp.jpg")


# ===== РУЛЕТКА ₽ =====

@bot.message_handler(func=lambda m:m.text=="🎰 Рулетка ₽")
def rub_start(m):

    p=get_player(m.from_user)

    bot.send_message(
        m.chat.id,
        "🎰 Введи ставку от 1000 до 10000"
    )

    p["roulette_rub"]=True
    save()


@bot.message_handler(func=lambda m:m.text.isdigit())
def roulette_rub_play(m):

    p=get_player(m.from_user)

    if not p.get("roulette_rub"):
        return

    bet=int(m.text)

    if bet<1000 or bet>10000:

        bot.send_message(
            m.chat.id,
            "⚠️ Ставка должна быть от 1000 до 10000 ₽"
        )
        return

    if p["money"]<bet:

        bot.send_message(
            m.chat.id,
            "💸 Недостаточно денег"
        )
        return

    p["roulette_rub"]=False

    if random.random()<0.45:

        win=bet*2
        p["money"]+=bet

        text=f"""
🎰 Рулетка

🎉 Ты выиграл!

💰 +{bet} ₽

Баланс: {p['money']} ₽
"""

    else:

        p["money"]-=bet

        text=f"""
🎰 Рулетка

😐 Ты проиграл

💸 −{bet} ₽

Баланс: {p['money']} ₽
"""

    save()

    bot.send_message(
        m.chat.id,
        text,
        reply_markup=kraken_menu()
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


@bot.message_handler(func=lambda m: True)
def roulette_play(m):

    if not m.text:
        return

    p = get_player(m.from_user)

    if not p["roulette"]:
        return

    text = m.text.strip()

    if not text.isdigit():
        bot.send_message(m.chat.id,"🎰 Напиши число от 1 до 10")
        return

    num = int(text)

    if num < 1 or num > 10:
        bot.send_message(m.chat.id,"🎰 Нужно число от 1 до 10")
        return

    win = random.randint(1,10)

    if num == win:

        p["mef"] += 5

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

    p["roulette"] = False
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

    if p["xp"]>=need:

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

        p["last"]=now
        save()

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
        1:15000,
        2:45000,
        3:120000,
        4:350000
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

import threading

def market_loop():
    while True:
        check_black_market()
        time.sleep(10)

threading.Thread(target=market_loop).start()
bot.infinity_polling()
