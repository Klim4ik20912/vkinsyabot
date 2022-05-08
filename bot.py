import random

from vkbottle.bot import Bot, Message
from vkbottle import Keyboard, KeyboardButtonColor, \
                                  Text, OpenLink, Location, EMPTY_KEYBOARD, \
                                  template_gen, TemplateElement, Callback
from vkbottle import GroupEventType, GroupTypes, VKAPIError
from vkbottle.modules import json
import sqlite3
from vkbottle import PhotoMessageUploader, VoiceMessageUploader, DocMessagesUploader
from datetime import date, datetime
from vkbottle.api import API
import time, math

bot = Bot(token="4c67c62573d20bc73ae4b2f442e116e6edac9642c84077af20ea4850ab95621611507dd99a1c68444e7fc")

# db initialize
db = sqlite3.connect("data.db")
sql = db.cursor()
db.commit()

@bot.on.private_message(text=["Начать", "Start", "Старт"])
async def reg_handler(message: Message):
    peer_id = message.peer_id
    sql.execute(f"SELECT * FROM users WHERE user_id = {peer_id}")
    if sql.fetchone() is None:
        sql.execute(f"INSERT INTO users VALUES ({peer_id}, 'NULL', {0}, {0}, {500}, {0}, 'NULL')")
        db.commit()
        keyboard = Keyboard()
        keyboard.add(Text("в меню", {"cmd": "menu"}), color=KeyboardButtonColor.POSITIVE)
        await message.answer("ты успешно зарегестрирован в боте! у тебя есть 500$ для старта.", keyboard=keyboard)
        print(" + рег ")

def snus_draw(peer_id):
    snus = sql.execute(f"SELECT snus FROM users WHERE user_id = {peer_id}").fetchone()[0]
    if snus == "ALFA":
        return "alfa.jpg"
    elif snus == "MAD":
        return "mad.jpg"
    else:
        return "garage.jpg"

@bot.on.private_message(payload={"cmd": "menu"})
@bot.on.private_message(text=["меню", "перейти в главное меню", "я"])
async def menu_handler(message: Message):
    peer_id = message.peer_id
    keyboard = Keyboard()
    keyboard.add(Text("вкинутся", {"cmd": "vkid"}), color=KeyboardButtonColor.POSITIVE)
    keyboard.row()
    keyboard.add(Text("банды", {"cmd": "clan"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Text("шоп", {"cmd": "shop"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Text("🔄", {"cmd": "menu"}), color=KeyboardButtonColor.SECONDARY)
    for i in sql.execute(f"SELECT balance, snus, jmixov, pakov, vtoryakov FROM users WHERE user_id = {peer_id}"):
        balance = i[0]
        snus = i[1]
        jmixov = i[2]
        pakov = i[3]
        vtor = i[4]
        photo_att = PhotoMessageUploader(bot.api)
        url = snus_draw(peer_id)
        photo = await photo_att.upload(url)
        user = await bot.api.users.get(message.from_id)
        if snus == "NULL":
            await message.answer("здарова " + str(user[0].first_name) + ". на счету у тебя: " + str(balance) + "$" "\nу тебя: нету снюса" + "\nна твоем счету: " + str(jmixov) + " жмыхов", keyboard=keyboard, attachment=photo)
        else:
            await message.answer("здарова " + str(user[0].first_name) + ". на счету у тебя: " + str(balance) + "$" "\nу тебя: " + str(snus) + " " + str(pakov) + " паков. " + str(vtor) + " вторяков" + "\n на твоем счету: " + str(jmixov) + " жмыхов", keyboard=keyboard, attachment=photo)


@bot.on.private_message(payload={"cmd": "top"})
@bot.on.private_message(text="топ")
async def top_handler(message: Message):
    peer_id = message.peer_id
    user = await bot.api.users.get(message.peer_id)
    counter = 0
    for row in sql.execute("SELECT jmixov, user_id FROM users ORDER BY jmixov DESC LIMIT 3"):
            counter += 1
            ids = row[1]
            user = await bot.api.users.get(ids)
            jmixov = f' #{counter} | жмыхов: {row[0]}'
            await message.answer(user[0].first_name + str(jmixov))

@bot.on.raw_event(GroupEventType.LIKE_REMOVE, dataclass=GroupTypes.LikeRemove)
async def remove_like_handler(event: GroupTypes.LikeRemove):
    peer_id = event.object.liker_id
    for i in sql.execute(f"SELECT balance, pakov, snus FROM users WHERE user_id = {peer_id}"):
        balance = i[0]
        pakov = i[1]
        snus = i[2]
        if snus != "NULL" or pakov > 0:
            pakov -= 2
            balance -= 25
            sql.execute(f"UPDATE users SET balance = {balance} WHERE user_id = {peer_id}")
            sql.execute(f"UPDATE users SET pakov = {pakov} WHERE user_id = {peer_id}")
            db.commit()
            await bot.api.messages.send(
                peer_id=event.object.liker_id,
                message="💔 я у тебя все отнимаю...",
                random_id=0
            )
        else:
            balance -= 25
            sql.execute(f"UPDATE users SET balance = {balance} WHERE user_id = {peer_id}")
            db.commit()
            await bot.api.messages.send(
                peer_id=event.object.liker_id,
                message="💔 я у тебя все отнимаю...",
                random_id=0
            )

@bot.on.raw_event(GroupEventType.LIKE_ADD, dataclass=GroupTypes.LikeAdd)
async def like_handler(event: GroupTypes.LikeAdd):
    peer_id = event.object.liker_id
    for i in sql.execute(f"SELECT balance, pakov, snus FROM users WHERE user_id = {peer_id}"):
        balance = i[0]
        pakov = i[1]
        snus = i[2]
        if snus != "NULL":
            pakov += 2
            balance += 25
            sql.execute(f"UPDATE users SET balance = {balance} WHERE user_id = {peer_id}")
            sql.execute(f"UPDATE users SET pakov = {pakov} WHERE user_id = {peer_id}")
            db.commit()
            await bot.api.messages.send(
                peer_id=event.object.liker_id,
                message="❤ за лайка поста ты получаешь: 25" + "$ \n и " + " 2 пака",
                random_id=0
            )
        else:
            balance += 25
            sql.execute(f"UPDATE users SET balance = {balance} WHERE user_id = {peer_id}")
            db.commit()
            await bot.api.messages.send(
                peer_id=event.object.liker_id,
                message="❤ за лайка поста ты получаешь: 25$ \n а снюса у тебя нету(",
                random_id=0
            )

@bot.on.message(text='/mail <txt>')
async def lsmsg(ans: Message, txt):
    for user in sql.execute("SELECT user_id FROM users"):
        for_users = user[0]
        await bot.api.messages.send(peer_id=for_users, random_id=0, message=txt)

@bot.on.private_message(payload={"cmd": "clan"})
@bot.on.private_message(text=["банды", "банда"])
async def clan_handler(message: Message):
    peer_id = message.peer_id
    keyboard = Keyboard(one_time=True).add(Text("назад в меню", {"cmd": "menu"}))
    await message.answer("банды...", keyboard=keyboard)

@bot.on.private_message(payload={"cmd": "shop"})
@bot.on.private_message(text=["магазин", "магаз", "шоп"])
async def shop_handler(message: Message):
    peer_id = message.peer_id
    user = await bot.api.users.get(message.from_id)
    await message.answer("дарова, " + str(user[0].first_name) + ". все что есть:\n RED(150$) \n MAD(150$ \n чтобы купить напиши: /buy name \n например: /buy RED")

@bot.on.private_message(text=["/buy <name>", "/buy"])
async def buy_handler(message: Message, name=None):
    peer_id = message.peer_id
    for i in sql.execute(f"SELECT balance, pakov, snus FROM users WHERE user_id = {peer_id}"):
        balance = i[0]
        pakov = i[1]
        snus = i[2]
    if name is not None:
        if snus == "NULL":
            if name == "RED" and balance >= 150:
                balance -= 150
                pakov += 20
                sql.execute(f"UPDATE users SET balance = {balance} WHERE user_id = {peer_id}")
                sql.execute(f"UPDATE users SET snus = 'RED' WHERE user_id = {peer_id}")
                sql.execute(f"UPDATE users SET pakov = {pakov} WHERE user_id = {peer_id}")
                db.commit()
                keyboard = Keyboard()
                keyboard.add(Text("в меню", {"cmd": "menu"}), color=KeyboardButtonColor.POSITIVE)
                await message.answer("ты успешно приобрел RED. \n на счету у тя: " + str(balance) + "$", keyboard=keyboard)
            elif name == "MAD" and balance >= 150:
                balance -= 150
                pakov += 20
                sql.execute(f"UPDATE users SET balance = {balance} WHERE user_id = {peer_id}")
                sql.execute(f"UPDATE users SET snus = 'MAD' WHERE user_id = {peer_id}")
                sql.execute(f"UPDATE users SET pakov = {pakov} WHERE user_id = {peer_id}")
                db.commit()
                keyboard = Keyboard()
                keyboard.add(Text("в меню", {"cmd": "menu"}), color=KeyboardButtonColor.POSITIVE)
                await message.answer("ты успешно приобрел MAD. \n на счету у тя: " + str(balance) + "$", keyboard=keyboard)
            if balance < 150:
                keyboard = Keyboard()
                keyboard.add(Text("в меню", {"cmd": "menu"}), color=KeyboardButtonColor.POSITIVE)
                await message.answer("у тебя не хватает на этот снюс", keyboard=keyboard)
            elif balance <150:
                keyboard = Keyboard()
                keyboard.add(Text("в меню", {"cmd": "menu"}), color=KeyboardButtonColor.POSITIVE)
                await message.answer("у тебя уже есть снюс", keyboard=keyboard)
    else:
        keyboard = Keyboard()
        keyboard.add(Text("в меню", {"cmd": "menu"}), color=KeyboardButtonColor.POSITIVE)
        await message.answer("ты ввел неккоретное название снюса!", keyboard=keyboard)

@bot.on.private_message(payload={"cmd": "vkid"})
@bot.on.private_message(text=["вкинутся", "вкид", "оформить"])
async def vkid_handler(message: Message):
    peer_id = message.peer_id
    keyboard = Keyboard()
    keyboard.add(Text("свежак"), color=KeyboardButtonColor.POSITIVE)
    keyboard.add(Text("вторяк"), color=KeyboardButtonColor.NEGATIVE)
    keyboard.row()
    keyboard.add(Text("назад в меню", {"cmd": "menu"}), color=KeyboardButtonColor.PRIMARY)

    await message.answer("выбери какой пак кидаем.", keyboard=keyboard)

    @bot.on.private_message(text="свежак")
    async def svejak_handler(message: Message):
        for i in sql.execute(f"SELECT pakov, snus FROM users WHERE user_id = {peer_id}"):
            pakov = i[0]
            snus = i[1]
            if pakov != 0:
                global need
                need = random.randint(7, 10)
                print(need)
                pakov -= 1
                sql.execute(f"UPDATE users SET pakov = {pakov} WHERE user_id = {peer_id}")
                db.commit()
                keyboard = Keyboard()
                keyboard.add(Text("скинуть пак", {"cmd": "skinut"}), color=KeyboardButtonColor.POSITIVE)
                keyboard.row()
                keyboard.add(Text("обновить время", {"cmd": "update_time"}), color=KeyboardButtonColor.PRIMARY)
                await message.answer("ты вкинул пак! \n острожно, пак можно недодержать или передержать. \n "
                                     "чтобы этого не случилось тебе нужно вытащить его \n через: " + str(need) + " сек.", keyboard=keyboard)
                global vkid_time
                vkid_time = datetime.now()
                print("вкид тайм " + str(vkid_time))
            else:
                sql.execute(f"UPDATE users SET snus = 'NULL' WHERE user_id = {peer_id}")
                db.commit()
                keyboard = Keyboard()
                keyboard.add(Text("в меню", {"cmd": "menu"}), color=KeyboardButtonColor.POSITIVE)
                await message.answer("у тебя закончились паки(", keyboard=keyboard)


    @bot.on.private_message(text="вторяк")
    async def vtoryak_handler(message: Message):
        for i in sql.execute(f"SELECT vtoryakov, snus FROM users WHERE user_id = {peer_id}"):
            pakov = i[0]
            snus = i[1]
            if pakov != 0:
                rand = random.randint(1, 2)
                if rand == 1:
                    global need
                    need = random.randint(7, 10)
                    print(need)
                    pakov -= 1
                    sql.execute(f"UPDATE users SET pakov = {pakov} WHERE user_id = {peer_id}")
                    db.commit()
                    keyboard = Keyboard()
                    keyboard.add(Text("скинуть пак", {"cmd": "skinut"}), color=KeyboardButtonColor.POSITIVE)
                    keyboard.row()
                    keyboard.add(Text("обновить время", {"cmd": "update_time"}), color=KeyboardButtonColor.PRIMARY)
                    await message.answer("ты вкинул пак! \n острожно, пак можно недодержать или передержать. \n "
                                        "чтобы этого не случилось тебе нужно вытащить его \n через: " + str(need) + " сек.", keyboard=keyboard)
                    global vkid_time
                    vkid_time = datetime.now()
                    print("вкид тайм " + str(vkid_time))
                else:
                    keyboard = Keyboard()
                    keyboard.add(Text("в меню", {"cmd": "menu"}), color=KeyboardButtonColor.POSITIVE)
                    await message.answer("вторяк поступил как гнида и порвался", keyboard=keyboard)
                    pakov -= 1
                    sql.execute(f"UPDATE users SET pakov = {pakov} WHERE user_id = {peer_id}")
                    db.commit()
            else:
                keyboard = Keyboard()
                keyboard.add(Text("в меню", {"cmd": "menu"}), color=KeyboardButtonColor.POSITIVE)
                await message.answer("у тебя закончились паки(", keyboard=keyboard)


@bot.on.private_message(payload={"cmd": "skinut"})
@bot.on.private_message(text="высунуть пак")
async def visunut_handler(message: Message):
    peer_id = message.peer_id
    skid_time = datetime.now()
    count = skid_time - vkid_time
    print(count)
    if count.seconds == need:
        for i in sql.execute(f"SELECT balance, vtoryakov, jmixov FROM users WHERE user_id = {peer_id}"):
            balance = i[0]
            vtoryakov = i[1]
            jmixov = i[2]
            vtoryakov += 1
            balance += 30
            jmixov += 1
            sql.execute(f"UPDATE users SET vtoryakov = {vtoryakov} WHERE user_id = {peer_id}")
            sql.execute(f"UPDATE users SET balance = {balance} WHERE user_id = {peer_id}")
            sql.execute(f"UPDATE users SET jmixov = {jmixov} WHERE user_id = {peer_id}")
            db.commit()
            keyboard = Keyboard()
            keyboard.add(Text("кинуть еще", {"cmd": "vkid"}), color=KeyboardButtonColor.POSITIVE)
            keyboard.add(Text("назад в меню", {"cmd": "menu"}), color=KeyboardButtonColor.PRIMARY)
            await message.answer("все получилось, + 1 жмых, + вторяк, + 30$", keyboard=keyboard)

    if count.seconds > need:
        keyboard = Keyboard()
        keyboard.add(Text("кинуть еще", {"cmd": "vkid"}), color=KeyboardButtonColor.POSITIVE)
        keyboard.add(Text("назад в меню", {"cmd": "menu"}), color=KeyboardButtonColor.PRIMARY)
        await message.answer("не получилось, ты передержал пак...", keyboard=keyboard)
    if count.seconds < need:
        keyboard = Keyboard()
        keyboard.add(Text("кинуть еще", {"cmd": "vkid"}), color=KeyboardButtonColor.POSITIVE)
        keyboard.add(Text("назад в меню", {"cmd": "menu"}), color=KeyboardButtonColor.PRIMARY)
        await message.answer("не получилось, ты недодержал пак...", keyboard=keyboard)

@bot.on.private_message(payload={"cmd": "update_time"})
@bot.on.private_message(text="обновить время")
async def update_handler(message: Message):
    now_time = datetime.now()
    up_counter = now_time.second - vkid_time.second - need
    await message.answer("тебе нужно скинуть через " + str(up_counter * -1) + " сек")


@bot.on.chat_message(text="я")
async def ya_handler(message: Message):
    peer_id = message.from_id
    for i in sql.execute(f"SELECT balance, pakov, snus, jmixov FROM users WHERE user_id = {peer_id}"):
        balance = i[0]
        pakov = i[1]
        snus = i[2]
        jmixov = i[3]
        photo_att = PhotoMessageUploader(bot.api)
        url = snus_draw(peer_id)
        photo = await photo_att.upload(url)
        user = await bot.api.users.get(message.from_id)
        if snus == "NULL":
            await message.answer("приветсвую " + str(user[0].first_name) + ". на счету у тебя: " + str(balance) + "$" "\nу тебя: нету снюса" + "\nна твоем счету: " + str(jmixov) + " жмыхов", attachment=photo)
        else:
            await message.answer("здарова " + str(user[0].first_name) + ". на счету у тебя: " + str(balance) + "$" "\nу тебя: " + str(snus) + " " + str(pakov) + " паков" + "\nна твоем счету: " + str(jmixov) + " жмыхов", attachment=photo)


@bot.on.chat_message(text="топ")
async def chat_top_handler(message: Message):
    peer_id = message.from_id
    user = await bot.api.users.get(message.from_id)
    counter = 0
    for row in sql.execute("SELECT jmixov, user_id FROM users ORDER BY jmixov DESC LIMIT 3"):
            counter += 1
            ids = row[1]
            user = await bot.api.users.get(ids)
            jmixov = f' #{counter} | жмыхов: {row[0]}'
            await message.answer(user[0].first_name + str(jmixov))

bot.run_forever()
