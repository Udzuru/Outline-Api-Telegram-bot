import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils.helper import Helper, HelperMode, ListItem
from aiocryptopay import AioCryptoPay, Networks
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton,InlineKeyboardMarkup,InlineKeyboardButton
from aiogram.types.web_app_info import WebAppInfo
from aiogram.utils.deep_linking import get_start_link, decode_payload
import sqlite3
from yoomoney import Quickpay
from yoomoney import Client
from datetime import datetime,timedelta
import uuid 
import threading
import asyncio
import time
import json

import buttons,texts
from servermet import *
from DataClass import User,Server,Keys,Crypto_id,Umani_id,refs

#Настройка
conn = sqlite3.connect(texts.database,check_same_thread=False)
cursor = conn.cursor()
crypto = AioCryptoPay(token=texts.crypto_token, network=Networks.TEST_NET)
logging.basicConfig(level=logging.INFO)

# Создаем бота и диспетчер
bot = Bot(token=texts.bot_token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

#Поток для обнуления дней

async def obnul():
    while True:
        await asyncio.sleep(5) 
        print("Работает проверка")
        users = User().fetch_all()
        for user in users:
            col=day_counter(user.date_act)
            if col>0:
                user.days=col
            elif col<=0 and user.status=="active":
                await bot.send_message(user.tel_id,"У вас закончились дни подписки пожайлуста продлите их")
                keys=cursor.execute("SELECT * from Keys where user = ?",(user.tel_id,)).fetchall()
                for k in keys:
                    server = Server(id=k[1]).get()
                    deletekey(server.url,server.sha256,user.tel_id)
                user.days=col
                user.status="inactive"
            
            user.update()
            

def day_counter(day1):
    date2 = datetime.strptime(day1, '%m/%d/%Y, %H:%M:%S')
    date1 =datetime.now()
    delta = date2 - date1
    delta=delta.days
    if delta<=0:
        return 0
    else:
        return delta
@dp.message_handler(commands=['server'])
async def serverMethods(message: types.Message):
    if message.from_user.id != texts.admin_id:
        await dp.bot.send_message(texts.admin_id, "Не правильная команда!!!")
    args = message.get_args().split()
    if args[0]=="show":
        servers=cursor.execute("SELECT * FROM server").fetchall()
        for i in servers:
            await message.answer("id:"+str(i[0])+" "+str(i[3])+" "+str(i[1])+" "+str(i[2]))
        
    elif args[0]=="add":
        y = json.loads(args[2])
        print(y["apiUrl"])
        print(y["certSha256"])
        cursor.execute("""INSERT into server
                       (url,sha256,country)
                       VALUES(?,?,?)
                       """,(y["apiUrl"],y["certSha256"],args[1]))
        conn.commit()
        await message.answer("Сервер успешно добавлен!")
        
    
    elif args[0]=="delete":
        cursor.execute("DELETE FROM server WHERE id = ?",(args[1],))
        conn.commit()
        await message.answer("Успешно удалено")
@dp.message_handler(commands=['change'])
async def r(message: types.Message):
    if message.from_user.id != texts.admin_id:
        await dp.bot.send_message(texts.admin_id, "Не правильная команда!!!")
        return
    args = message.get_args().split(maxsplit=1)
    if len(args) == 2:
        user_id, day = int(args[0]), args[1]
        u=User(tel_id=user_id)
        
        if u.get() ==None:
            await dp.bot.send_message(texts.admin_id, "Такого юзера не существует!!!")
            return
        else:
            date_time = datetime.now()
            date_time = date_time+ timedelta(days=int(day))
            date_time= date_time.strftime("%m/%d/%Y, %H:%M:%S")
            u.date_act =date_time
            u.status="active"
            u.update()
            await dp.bot.send_message(texts.admin_id, "Операция успешно совершена!!!")

            


@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    args = message.get_args()
    if args != None:
        reference = decode_payload(args)
        if str(reference) == str(message.from_user.id):
            await message.answer("Вы не можете быть рефералом самого себя!")
            return 
        
        ref = refs()
        ref.whom = str(message.from_user.id)
        if ref.get() != None:
            await message.answer("У вас уже есть реферал!")
            return 
        
        await message.answer(f"Ваш реферал {reference}. После оплаты вы получите бонус +20 дней") 
        ref = refs()
        ref.who = reference
        ref.whom = str(message.from_user.id)
        ref.status = "active"
        ref.insert()
    user = User(tel_id = message.from_user.id)
    check=user.get()
    if check == None:
        date_time = datetime.now()
        date_time = date_time+ timedelta(days=int(0))
        date_time= date_time.strftime("%m/%d/%Y, %H:%M:%S")
        user.date_act =date_time
        user.status="inactive"
        user.insert()
    await message.reply(texts.Hitext, reply_markup=buttons.main_kb)

@dp.message_handler(lambda message: message.text == texts.but_menu or message.text==texts.but_info)
async def but_handler(message: types.Message):
    await start_command(message)

@dp.message_handler(lambda message: message.text == texts.but_profile )
async def button2_handler(message: types.Message):
    link = await get_start_link(str(message.from_user.username), encode=True)
    user = User(tel_id=message.from_user.id)
    user.get()
    col=day_counter(user.date_act)
    if col>0:
        user.days=col
    else:
        user.days=col
        user.status="inactive"
    user.update()
    if user.status=='active':
        await message.answer('Ваш профиль:'+str(user.tel_id)+'\n Дни подписки: '+str(user.days)+'\n Статус: '+user.status,reply_markup=buttons.profile_kb)
    if user.status=='checking':
        await message.answer("Ваша оплата проходит этап проверки пожайлуста ожидайте!")
    if user.status=='inactive':
        await message.answer("У вас закончились дни подписки нажмите Купить VPN!")


@dp.message_handler(lambda message: message.text == 'Мои ключи')
async def button2_handler(message: types.Message):
    user = User(tel_id=message.from_user.id)
    user.get()
    if user.status=="inactive":
        return
    servers=Server().fetch_all()
    inline_kb2 = InlineKeyboardMarkup()
    for field in servers:
        inline_btn_2 = InlineKeyboardButton(field.country, callback_data='idzav_'+str(field.id))
        inline_kb2.add(inline_btn_2)
    await message.answer("Выберите страну для подключения!",reply_markup=inline_kb2)

@dp.message_handler(lambda message: message.text =='Купить VPN')
async def pay_choice(message:types.Message):
    keyboard = InlineKeyboardMarkup()
    button = InlineKeyboardButton("Крипта",callback_data='Pay_crypto')
    keyboard.add(button)
    button = InlineKeyboardButton("RUB",callback_data='Pay_RUB')
    keyboard.add(button)
    await message.answer("Выберите способ оплаты!",reply_markup=keyboard)

@dp.message_handler(lambda message: message.text ==texts.but_ref)
async def ref_void(message:types.Message):
    link = await get_start_link(str(message.from_user.id), encode=True)
    await message.answer("Здесь реферальная система. Перейдя по вашей ссылке после оплаты вы получите 10 дней, а ваш реферал получит 20 дней.")
    await message.answer(f"Ваша реферальная ссылка \n{link}")

@dp.callback_query_handler(lambda c: c.data.startswith('Pay_RUB'))
async def process_callback_pay_crypto(callback_query: types.CallbackQuery):
    keyboard = InlineKeyboardMarkup()
    for i in texts.lll:
        button = InlineKeyboardButton(i.text,callback_data='oplataRUB_'+str(i.price))
        keyboard.add(button)
    await bot.send_message(callback_query.message.chat.id,text="Варианты подписки:",reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data.startswith('Pay_crypto'))
async def process_callback_pay_crypto(callback_query: types.CallbackQuery):
    keyboard = InlineKeyboardMarkup()
    for i in texts.lll:
        button = InlineKeyboardButton(i.text,callback_data='oplata_'+str(i.price))
        keyboard.add(button)
    await bot.send_message(callback_query.message.chat.id,text="Оплати подписку",reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data.startswith('oplata_'))
async def process_callback_button(callback_query: types.CallbackQuery):
    # Получение ID заявки из callback_data
    price = callback_query.data.split('_')[1]
    await crypto_pay_func(callback_query.message,price)
@dp.callback_query_handler(lambda c: c.data.startswith('oplataRUB_'))
async def process_callback_button(callback_query: types.CallbackQuery):
    # Получение ID заявки из callback_data
    price = callback_query.data.split('_')[1]
    await umoney_pay_func(callback_query.message,price)    



async def crypto_pay_func(message,price):
    fiat_invoice = await crypto.create_invoice(amount=price, fiat='RUB', currency_type='fiat')
    keyboard = InlineKeyboardMarkup()
    button = InlineKeyboardButton('Оплатить!!!', url=fiat_invoice.bot_invoice_url)
    button1 = InlineKeyboardButton('Проверить оплату!',callback_data="pay_"+str(fiat_invoice.invoice_id)+"_"+price)
    keyboard.add(button)
    keyboard.add(button1)
    await message.answer("К оплате "+price+" рублей в криптобот",reply_markup=keyboard)

async def umoney_pay_func(message,price):
    unical=str(uuid.uuid1())
    quickpay = Quickpay(
            receiver="410016016444408",
            quickpay_form="shop",
            targets="Оплата подписки",
            paymentType="SB",
            sum=price,
            label=unical,
            )
    keyboard = InlineKeyboardMarkup()
    button = InlineKeyboardButton('Оплатить!!!', web_app=WebAppInfo(url=quickpay.redirected_url))
    button1 = InlineKeyboardButton('Проверить оплату!',callback_data="payRUB_"+str(unical)+"_"+price)
    keyboard.add(button)
    keyboard.add(button1)
    await message.answer("К оплате "+price+" в Юмани",reply_markup=keyboard)


@dp.callback_query_handler(lambda c: c.data.startswith('pay_'))
async def process_callback_button(callback_query: types.CallbackQuery):
    # Получение ID заявки из callback_data
    id = callback_query.data.split('_')[1]
    price = callback_query.data.split('_')[2]
    idishnik=Crypto_id(paid_id=id).get()
    if(idishnik!=None):
        await bot.send_message(callback_query.from_user.id,text="Нельзя использовать ту же кнопку!")
        return
    invoices = await crypto.get_invoices(invoice_ids=id)
    if (invoices[0].status == "paid"):
        days=0
        for i in texts.lll:
            if int(i.price) == int(price):
                days=i.days
        ref=refs()
        ref.whom = str(callback_query.from_user.id)
        ref.get()
        if ref != None:
            if ref.status=="active":
                await bot.send_message(callback_query.from_user.id,text="Вы получили 20 бонусных дней!")
                days=str(int(days)+20)
                await bot.send_message(ref.who,text="Ваш реферал оплатил и вы получили 10 дней")
                user=User(tel_id=ref.who)
                user.get()
                date_time = datetime.now()
                date_time = date_time+ timedelta(days=int(10)+int(user.days))
                date_time= date_time.strftime("%m/%d/%Y, %H:%M:%S")
                user.date_act =date_time
                user.update()
                ref.status="inactive"
                ref.update()

        user=User(tel_id=callback_query.from_user.id)
        user.get()
        date_time = datetime.now()
        date_time = date_time+ timedelta(days=int(days)+int(user.days))
        date_time= date_time.strftime("%m/%d/%Y, %H:%M:%S")
        user.date_act =date_time
        user.status="active"
        user.update()
        idishnik=Crypto_id()
        idishnik.paid_id=id
        idishnik.user=user.tel_id
        idishnik.insert()
        await bot.send_message(callback_query.from_user.id,text="Ваша оплата прошла успешно!")
    else:
        await bot.send_message(callback_query.message.chat.id,text="Вы еще не оплатили или оплата еще не загрузилась ждите и нажмите проверить еще раз!!!")


@dp.callback_query_handler(lambda c: c.data.startswith('payRUB_'))
async def process_callback_button(callback_query: types.CallbackQuery):
    client = Client(texts.umoney_token)
    id = callback_query.data.split('_')[1]
    price = callback_query.data.split('_')[2]
    idishnik=Umani_id(paid_id=id).get()
    if(idishnik!=None):
        await bot.send_message(callback_query.from_user.id,text="Нельзя использовать ту же кнопку!")
        return
    # Получение ID заявки из callback_data
    

    history = client.operation_history(label=id)
    if history == None:
        await bot.send_message(callback_query.from_user.id,text="В начале надо оплатить!")
        return
    if (history.operations[0].status == "success"):
        days=0
        for i in texts.lll:
            if int(i.price) == int(price):
                days=i.days
        ref=refs()
        ref.whom = str(callback_query.from_user.id)
        ref.get()
        if ref != None:
            if ref.status=="active":
                await bot.send_message(callback_query.from_user.id,text="Вы получили 20 бонусных дней!")
                days=str(int(days)+20)
                await bot.send_message(ref.who,text="Ваш реферал оплатил и вы получили 10 дней")
                user=User(tel_id=ref.who)
                user.get()
                date_time = datetime.now()
                date_time = date_time+ timedelta(days=int(10)+int(user.days))
                date_time= date_time.strftime("%m/%d/%Y, %H:%M:%S")
                user.date_act =date_time
                user.update()
                ref.status="inactive"
                ref.update()
        user=User(tel_id=callback_query.from_user.id)
        user.get()
        date_time = datetime.now()
        date_time = date_time+ timedelta(days=int(days)+int(user.days))
        date_time= date_time.strftime("%m/%d/%Y, %H:%M:%S")
        user.date_act =date_time
        user.status="active"
        user.update()
        idishnik=Umani_id()
        idishnik.paid_id=id
        idishnik.user=user.tel_id
        idishnik.insert()
        await bot.send_message(callback_query.from_user.id,text="Ваша оплата прошла успешно!")
    else:
        await bot.send_message(callback_query.message.chat.id,text="Вы еще не оплатили или оплата еще не загрузилась ждите и нажмите проверить еще раз!!!")

@dp.callback_query_handler(lambda c: c.data.startswith('Regen_'))
async def process_callback_button(callback_query: types.CallbackQuery):
    # Получение ID заявки из callback_data
    zav_id = callback_query.data.split('_')[1]
    server = Server(id=zav_id).get()
    key=Keys(user=callback_query.from_user.id,server = server.id)
    result = deletekey(server.url,server.sha256,key.user)
    key.delete()
    if not result:
        bot.send_message(chat_id=key.user,text="Ошибка при удалении!")
    await process_callback_button(callback_query)    


@dp.callback_query_handler(lambda c: c.data.startswith('idzav_'))
async def process_callback_button(callback_query: types.CallbackQuery):
    # Получение ID заявки из callback_data
    zav_id = callback_query.data.split('_')[1]
    server = Server(id=zav_id).get()
    key = Keys(user=callback_query.from_user.id,server=server.id)
    if key.key=='':
        k=getkey(server.url,server.sha256,callback_query.from_user.id)
        key.key=k.access_url 
        key.insert()
    inline_kb2 = InlineKeyboardMarkup()
    inline_btn_2 = InlineKeyboardButton("Revoke", callback_data='Regen_'+str(server.id))
    inline_kb2.add(inline_btn_2)
    await bot.send_message(callback_query.message.chat.id,text="\n Ваш ключ:\n `"+key.key+"`", parse_mode="MARKDOWN",reply_markup=inline_kb2)

    

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(obnul())
    executor.start_polling(dp, skip_updates=True)
    