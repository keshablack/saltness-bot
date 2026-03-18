from PIL import Image, ImageDraw
import telebot
import random
import time
import json
from telebot.types import ReplyKeyboardMarkup
import os

black_market=False
black_market_end=0

used_promos = {}

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

ADMIN_ID = 7740504336

DATA_FILE = os.getenv("DATA_FILE","players.json")
DISTRICT_FILE = os.getenv("DISTRICT_FILE","data/districts.json")

import os
os.makedirs("data", exist_ok=True)

try:
    with open(DATA_FILE,"r") as f:
        players=json.load(f)
except:
    players={}

def save():
    with open(DATA_FILE,"w") as f:
        json.dump(players,f)


def save_districts():

    with open(DISTRICT_FILE,"w") as f:
        json.dump(districts,f)

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
            "roulette": False,
            "lab_lvl": 1,
            "lab_last": 0,
            "total": 0,
            "ref": None,
            "refs": 0,
            "ref_reward": 0,
            "district_time": 0,
            "promos": [],
            "attack_last": 0,
            "ref_used": False,
            "roulette_rub": False
        }

    p = players[uid]

    p["id"] = uid

    # фиксы старых игроков
    p.setdefault("ref", None)
    p.setdefault("refs", 0)
    p.setdefault("ref_reward", 0)
    p.setdefault("ref_used", False)

    p.setdefault("district_time", 0)
    p.setdefault("attack_last", 0)

    p.setdefault("band", None)

    players[uid]["name"] = user.first_name

    # 💀 РЕФЕРАЛЬНАЯ НАГРАДА
    if p.get("ref") and not p.get("ref_used"):

        if p["lvl"] >= 2:

            ref_id = p["ref"]

            if ref_id in players:
                players[ref_id]["sol"] += 5
                players[ref_id]["refs"] += 1
                players[ref_id]["ref_reward"] += 5

            p["ref_used"] = True

    # 💰 ДОХОД РАЙОНОВ
    district_income(p)

    return players[uid]

try:

    if not os.path.exists(DISTRICT_FILE):
        print("districts.json не найден, создаём новый")

        districts = {
            1: {"name":"Заречье","owner":None,"income":40000,"price":225000},
            2: {"name":"Индустриальный","owner":None,"income":40000,"price":225000},
            3: {"name":"Северный","owner":None,"income":30000,"price":150000},
            4: {"name":"Зашекснинский","owner":None,"income":60000,"price":300000}
        }

        save_districts()

    else:
        with open(DISTRICT_FILE,"r",encoding="utf-8") as f:
            districts = json.load(f)

        districts = {int(k):v for k,v in districts.items()}

except:
    print("Ошибка загрузки districts.json")

    districts = {
        1: {"name":"Заречье","owner":None,"income":40000,"price":225000},
        2: {"name":"Индустриальный","owner":None,"income":40000,"price":225000},
        3: {"name":"Северный","owner":None,"income":30000,"price":150000},
        4: {"name":"Зашекснинский","owner":None,"income":60000,"price":300000}
    }

    save_districts()


# ===== ЧЕРНЫЙ РЫНОК =====
def check_black_market():

    global black_market
    global black_market_end

    now = time.time()

    # закрытие рынка
    if black_market and now > black_market_end:

        black_market = False

        for uid in players:
            try:
                bot.send_message(
                    int(uid),
                    "🚫 <b>ЧЁРНЫЙ РЫНОК</b>\n"
                    "━━━━━━━━━━━━━━\n"
                    "Сейчас рынок закрыт.\n\n"
                    "⏳ Жди следующего открытия.\n\n"
                    "А пока… шкурь клады.\n"
                    "Когда рынок откроется —\n"
                    "ты сможешь продать стафф\n"
                    "💰 <b>по цене выше</b>.",
                    parse_mode="HTML"
                )
            except:
                pass

        return


    # открытие рынка
    if not black_market and random.randint(1,350) == 1:

        black_market = True
        black_market_end = now + 1200

        for uid in players:
            try:
                bot.send_message(
                    int(uid),
                    """
🕶 СТАФФ НА КРАКЕНЕ ПОДОРОЖАЛ

💎 Меф: 3200₽
🧂 Соль: 1500₽

⏱ Через 20 минут снова станет дешевле
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
    kb.add("🗺 Карта города","👥 Банды REMONT")

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

    p = get_player(m.from_user)

    args = m.text.split()

    if len(args) > 1:

        ref_id = args[1]

        if ref_id != str(m.from_user.id) and not p.get("ref"):

            if ref_id in players:

                p["ref"] = ref_id

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


@bot.message_handler(commands=["bc"])
def broadcast(m):

    if m.from_user.id != ADMIN_ID:
        return

    text = m.text.replace("/bc","").strip()

    if not text:
        bot.send_message(m.chat.id,"Напиши сообщение после /bc")
        return

    sent = 0

    import time

    for uid in players:
        try:
            bot.send_message(uid, text)
            time.sleep(0.05)
        except:
            pass
    
    
        bot.send_message(
            m.chat.id,
            f"Рассылка отправлена\nПолучили: {sent}"
        )


@bot.message_handler(commands=["givemoney"])
def give_money(m):

    if m.from_user.id != ADMIN_ID:
        return

    args = m.text.split()

    if len(args) < 3:
        bot.send_message(
            m.chat.id,
            "Использование:\n/givemoney id сумма"
        )
        return

    uid = args[1]
    amount = int(args[2])

    if uid not in players:
        bot.send_message(m.chat.id,"Игрок не найден")
        return

    players[uid]["money"] += amount

    save()

    bot.send_message(
        m.chat.id,
        f"💰 Выдано {amount}₽ игроку {players[uid]['name']}"
    )


@bot.message_handler(commands=["reset_refs"])
def reset_refs(m):

    if m.from_user.id != ADMIN_ID:
        return

    try:
        uid = m.text.split()[1]
    except:
        bot.send_message(m.chat.id, "Напиши: /reset_refs id")
        return

    if uid in players:
        players[uid]["refs"] = 0
        players[uid]["ref_reward"] = 0
        players[uid]["sol"] = 0

        save()

        bot.send_message(m.chat.id, f"💀 обнулил {uid}")

@bot.message_handler(commands=["set_money"])
def set_money(m):

    if m.from_user.id != ADMIN_ID:
        return

    try:
        uid = m.text.split()[1]
        amount = int(m.text.split()[2])
    except:
        bot.send_message(m.chat.id, "Напиши: /set_money id сумма")
        return

    if uid in players:
        players[uid]["money"] = amount

        save()

        bot.send_message(
            m.chat.id,
            f"💀 Установил {amount}₽ игроку {uid}"
        )
    else:
        bot.send_message(m.chat.id, "Игрок не найден")



# ===== ТОП =====

@bot.message_handler(func=lambda m: m.text=="🏆 Топ")
def top(m):

    top_farm = sorted(players.values(), key=lambda x: x.get("total",0), reverse=True)[:10]
    top_refs = sorted(players.values(), key=lambda x: x.get("refs",0), reverse=True)[:10]
    top_money = sorted(players.values(), key=lambda x: x.get("money",0), reverse=True)[:5]

    text = "🏆 Топ шкуроходов\n\n"

    # 💊 топ по стаффу
    for i,p in enumerate(top_farm,1):
        text += f"{i}. {p['name']} — {p.get('total',0)} стаффа\n"

    text += "\n👥 Топ рефералов\n\n"

    # 👥 топ рефералов
    for i,p in enumerate(top_refs,1):
        text += f"{i}. {p['name']} — {p.get('refs',0)} друзей\n"

    text += "\n💰 Топ богатых\n\n"

    # 💰 топ денег
    for i,p in enumerate(top_money,1):
        money = p.get("money",0)
        text += f"{i}. {p['name']} — {money:,}₽\n"

    bot.send_message(
        m.chat.id,
        text,
        reply_markup=menu()
    ) 

@bot.message_handler(commands=["promo"])
def promo(m):

    p = get_player(m.from_user)
    uid = str(m.from_user.id)

    args = m.text.split()

    if len(args) < 2:
        bot.send_message(m.chat.id,"Использование:\n/promo код")
        return

    code = args[1]

    promos = {
        "SORRY": {
            "money":9999,
            "mef":5,
            "sol":15
        }
    }

    if code not in promos:
        bot.send_message(m.chat.id,"❌ Такого промокода нет")
        return

    if code in p["promos"]:
        bot.send_message(m.chat.id,"❌ Ты уже использовал этот промокод")
        return

    reward = promos[code]

    p["money"] += reward["money"]
    p["mef"] += reward["mef"]
    p["sol"] += reward["sol"]

    p["promos"].append(code)

    save()

    bot.send_message(
        m.chat.id,
        f"""
🎁 ВАШ СОЛЕВОЙ ДРУГ НА ШИЗЕ ПОДУМАЛ ЧТО ВЫ МЕНТ, ВЫПРЫГНУЛ В ОКНО ОСТАВИВ БАБКИ И СТАФФ

💰 +{reward['money']}₽
🧊 +{reward['mef']} мефа
🧂 +{reward['sol']} соли
"""
    )



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
Условие: Твой друг должен получить 2 лвл

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

    generate_map()

    text="🗺 Карта города\n\n"

    for i,data in districts.items():

        owner=players.get(data["owner"],{}).get("name","свободно") if data["owner"] else "свободно"

        text+=f"""
{i}️⃣ {data['name']}
Владелец: {owner}
Доход: {data['income']}₽
Цена: {data['price']}₽
"""

    text += """
⚔ Управление районами

💰 купить [номер]
пример: купить 2

💣 напасть [номер]
стоимость атаки: 300000₽
шанс захвата: 30%

📥 доход районов начисляется каждый час
"""

    with open("map_temp.jpg","rb") as photo:

        bot.send_photo(
            m.chat.id,
            photo,
            caption=text
        )


@bot.message_handler(func=lambda m: m.text.startswith("купить"))
def buy_district(m):

    p = get_player(m.from_user)

    try:
        num = int(m.text.split()[1])
    except:
        bot.send_message(m.chat.id,"Напиши: купить номер_района")
        return

    # проверка владеет ли игрок районом
    for d in districts.values():
        if d["owner"] == str(m.from_user.id):
            bot.send_message(
                m.chat.id,
                "❌ Ты уже владеешь районом"
            )
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
    d["owner"]=str(m.from_user.id)

    save()
    save_districts()

    bot.send_message(
        m.chat.id,
        f"🏙 Ты купил район {d['name']}"
    )

def district_income(p):

    now = time.time()

    if now - p["district_time"] < 3600:
        return

    total = 0

    for d in districts.values():

        if d["owner"] == p["id"]:
            total += d["income"]

    if total > 0:

        p["money"] += total
        p["district_time"] = now

        save()

        try:
            bot.send_message(
                p["id"],
                f"🏙 Доход с районов\n\n💰 +{total}₽"
            )
        except:
            pass


@bot.message_handler(commands=["fix_income"])
def fix_income(m):

    for d in districts.values():
        if d["name"] == "Зашекснинский":
            d["income"] = 60000
        elif d["name"] == "Заречье":
            d["income"] = 40000
        elif d["name"] == "Индустриальный":
            d["income"] = 40000
        elif d["name"] == "Северный":
            d["income"] = 30000

    save_districts()

    bot.send_message(m.chat.id, "💀 доходы обновлены")


@bot.message_handler(func=lambda m: m.text.startswith("напасть"))
def attack_district(m):

    p = get_player(m.from_user)

    now = time.time()

    # кулдаун 10 минут
    if now - p["attack_last"] < 3600:
        left = int(3600 - (now - p["attack_last"]))
        bot.send_message(
            m.chat.id,
            f"⏳ Нападать можно через {left} сек"
        )
        return

    try:
        num = int(m.text.split()[1])
    except:
        bot.send_message(m.chat.id, "Напиши: напасть номер")
        return

    if num not in districts:
        bot.send_message(m.chat.id, "Нет такого района")
        return

    d = districts[num]

    if d["owner"] == str(m.from_user.id):
        bot.send_message(m.chat.id, "Это твой район, нападать нельзя")
        return

    if not d["owner"]:
        bot.send_message(m.chat.id, "Район свободен")
        return

    if p["money"] < 300000:
        bot.send_message(m.chat.id, "Нужно 300000₽ для нападения")
        return

    # снимаем деньги
    p["money"] -= 300000
    p["attack_last"] = now

    chance = random.randint(1, 100)

    if chance <= 30:

        uid = str(m.from_user.id)
        old = None

        # ищем старый район
        for dist in districts.values():
            if dist["owner"] == uid:
                old = dist["name"]
                dist["owner"] = None

        # назначаем новый район
        d["owner"] = uid

        if old:
            bot.send_message(
                m.chat.id,
                f"⚔ Ты потерял район {old} и захватил {d['name']}"
            )
        else:
            bot.send_message(
                m.chat.id,
                f"⚔ Ты захватил район {d['name']}"
            )

    else:

        bot.send_message(
            m.chat.id,
            "💀 Солевые нарики этого района дали отпор"
        )

    save()
    save_districts()

BASE_MAP = Image.open("map.jpg")

def generate_map():

    img = BASE_MAP.copy()
    draw = ImageDraw.Draw(img)

    from PIL import ImageFont
    font = ImageFont.truetype("arial.ttf", 30)

    areas = {

1:[
(426,272),
(575,272),
(575,382),
(426,382)
],

2:[
(193,259),
(350,259),
(350,357),
(193,357)
],

3:[
(345,145),
(433,145),
(433,219),
(345,219)
],

4:[
(250,402),
(399,402),
(399,613),
(250,613)
]

}

    for i, d in districts.items():
    
        i = int(i)
    
        if i in areas and d.get("owner"):
    
            poly = areas[i]
    
            draw.polygon(
                poly,
                fill=(255,0,0),
                outline=(0,0,0)
            )
    
            # центр полигона
            cx = sum(p[0] for p in poly) // len(poly)
            cy = sum(p[1] for p in poly) // len(poly)
    
            owner = d["owner"]
    
            if owner and owner in players:
    
                name = players[owner]["name"]
    
                draw.text(
                    (cx, cy),
                    name,
                    fill=(255,255,255),
                    anchor="mm",
                    font=font
                )
    
    img.save("map_temp.jpg")


# ===== РУЛЕТКИ =====

@bot.message_handler(func=lambda m:m.text=="🎰 Рулетка ₽")
def rub_start(m):
    p=get_player(m.from_user)
    bot.send_message(m.chat.id,"🎰 Введи ставку от 100 до 10000")
    p["roulette_rub"]=True
    save()


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


@bot.message_handler(func=lambda m: m.text and m.text.isdigit() and get_player(m.from_user).get("roulette"))
def roulette_mef_play(m):

    p = get_player(m.from_user)
    num = int(m.text)

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
"""
    else:
        text=f"""
🎰 Рулетка Меф

😐 Выпало число {win}
"""

    p["roulette"] = False
    save()

    bot.send_message(m.chat.id,text,reply_markup=kraken_menu())


    # ----- РУЛЕТКА ₽ -----
@bot.message_handler(func=lambda m: m.text and m.text.isdigit() and get_player(m.from_user).get("roulette_rub"))
def roulette_rub_play(m):

    p = get_player(m.from_user)
    bet = int(m.text)

    if bet < 100 or bet > 10000:
        bot.send_message(m.chat.id,"⚠️ Ставка должна быть от 100 до 10000 ₽")
        return

    if p["money"] < bet:
        bot.send_message(m.chat.id,"💸 Недостаточно денег, иди мути бабос")
        return

    p["roulette_rub"] = False

    if random.random() < 0.45:
        p["money"] += bet
        text=f"""
🎰 Рулетка

🎉 Ты выиграл!

💰 +{bet} ₽
"""
    else:
        p["money"] -= bet
        text=f"""
🎰 Рулетка

😐 Ты проиграл

💸 −{bet} ₽
"""

    save()

    bot.send_message(m.chat.id,text,reply_markup=kraken_menu())


# ===== ШКУРКА =====

@bot.message_handler(func=lambda m:m.text=="🧪 Шкурить")
def work(m):

    p = get_player(m.from_user)

    now = time.time()

    # 💀 анти-спам 1 сек
    if now - p.get("last_click", 0) < 1:
        return

    p["last_click"] = now

    cooldown = 180 - (p["lvl"]*4) - (p["lab_lvl"]*10)

    if cooldown < 30:
        cooldown = 30

    if now - p["last"] < cooldown:

        seconds = int(cooldown - (now - p["last"]))

        bot.send_message(
            m.chat.id,
            f"⏱ Ну ты чайка, потерпи еще {seconds} сек",
            reply_markup=menu()
        )
        return

    r = random.randint(1,100)
    amount = random.randint(1,3)

    p["xp"] += 1

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

        p["last"] = now

        p["working"] = False  # 💀 снимаем блок

        save()

    
            # ===== МАСТЕРКЛАД (3%) =====
    if r<=3:
    
        p["mef"] += 10
        p["total"] += 10
    
        username = m.from_user.username
        if username:
            username = "@" + username
        else:
            username = m.from_user.first_name
    
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
    
        # уведомление всем игрокам
        for uid in players:
            if str(uid) == str(m.from_user.id):
                continue
            try:
                bot.send_message(
                    int(uid),
                    f"""
    💎 МАСТЕРКЛАД!
    
    {username} нашёл мастерклад!
    
    🧊 +10 мефа
    """
                )
            except:
                pass
            

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

threading.Thread(target=market_loop, daemon=True).start()

# ===== БАНДЫ =====

BANDS_FILE = "data/bands.json"

try:
    with open(BANDS_FILE, "r", encoding="utf-8") as f:
        bands = json.load(f)
except:
    bands = {}

def save_bands():
    with open(BANDS_FILE, "w", encoding="utf-8") as f:
        json.dump(bands, f)

@bot.message_handler(func=lambda m: m.text=="👥 Банды")
def bands_menu(m):
    p = get_player(m.from_user)

    if p.get("band"):
        b = bands.get(p["band"])
        if not b:
            p["band"] = None
            save()
            return

        text = f"👥 Твоя банда: {b['name']}\n\n"
        text += f"👑 Главный солевой: {players[b['owner']]['name']}\n\n"
        text += "👥 Участники:\n"

        for uid in b["members"]:
            name = players.get(uid, {}).get("name","???")
            text += f"- {name}\n"

        if str(m.from_user.id) == b["owner"]:
            text += f"\n📨 Заявки: {len(b['requests'])}\n"
            text += "✔ принять [номер]\n❌ отклонить [номер]\n"

        text += "\n🚪 выйти"

        bot.send_message(m.chat.id, text)
        return

    text = "👥 Банды\n\n"

    for i,(bid,b) in enumerate(bands.items(),1):
        text += f"{i}. {b['name']}\n"
        text += f"👤 {players.get(b['owner'],{}).get('name','???')}\n"
        text += f"👥 {len(b['members'])}/5\n\n"

    text += "💰 создать\n📥 вступить [номер]"

    bot.send_message(m.chat.id, text)

@bot.message_handler(func=lambda m: m.text=="создать")
def create_band(m):
    p = get_player(m.from_user)

    if p.get("band"):
        bot.send_message(m.chat.id,"Ты уже в банде")
        return

    if p["money"] < 500000:
        bot.send_message(m.chat.id,"Нужно 500000₽")
        return

    bid = str(len(bands)+1)

    bands[bid] = {
        "name": f"Банда {bid}",
        "owner": str(m.from_user.id),
        "members": [str(m.from_user.id)],
        "requests": []
    }

    p["money"] -= 500000
    p["band"] = bid

    save()
    save_bands()

    bot.send_message(m.chat.id,"💀 Банда создана")

@bot.message_handler(func=lambda m: m.text.startswith("вступить"))
def join_band(m):
    p = get_player(m.from_user)

    if p.get("band"):
        bot.send_message(m.chat.id,"Ты уже в банде")
        return

    try:
        num = int(m.text.split()[1]) - 1
    except:
        bot.send_message(m.chat.id,"вступить номер")
        return

    if num >= len(bands):
        bot.send_message(m.chat.id,"Нет такой банды")
        return

    bid = list(bands.keys())[num]
    b = bands[bid]

    b["requests"].append(str(m.from_user.id))
    save_bands()

    bot.send_message(m.chat.id,"📨 заявка отправлена")

@bot.message_handler(func=lambda m: m.text.startswith("принять"))
def accept(m):
    p = get_player(m.from_user)

    if not p.get("band"):
        return

    b = bands.get(p["band"])

    if str(m.from_user.id) != b["owner"]:
        return

    try:
        num = int(m.text.split()[1]) - 1
    except:
        return

    if num >= len(b["requests"]):
        return

    uid = b["requests"].pop(num)

    if len(b["members"]) < 5:
        b["members"].append(uid)
        if uid in players:
            players[uid]["band"] = p["band"]

    save()
    save_bands()

    bot.send_message(m.chat.id,"✔ принят")

@bot.message_handler(func=lambda m: m.text.startswith("отклонить"))
def decline(m):
    p = get_player(m.from_user)

    if not p.get("band"):
        return

    b = bands.get(p["band"])

    if str(m.from_user.id) != b["owner"]:
        return

    try:
        num = int(m.text.split()[1]) - 1
    except:
        return

    if num >= len(b["requests"]):
        return

    b["requests"].pop(num)

    save_bands()

    bot.send_message(m.chat.id,"❌ отклонено")

@bot.message_handler(func=lambda m: m.text=="выйти")
def leave(m):
    p = get_player(m.from_user)

    if not p.get("band"):
        return

    b = bands.get(p["band"])
    uid = str(m.from_user.id)

    if uid == b["owner"]:
        del bands[p["band"]]
    else:
        if uid in b["members"]:
            b["members"].remove(uid)

    p["band"] = None

    save()
    save_bands()

    bot.send_message(m.chat.id,"🚪 ты вышел из банды")

bot.infinity_polling(skip_pending=True)
