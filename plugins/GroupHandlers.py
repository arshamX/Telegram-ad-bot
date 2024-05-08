
from datetime import date
from pyromod import Client , Message
from pyrogram.types import CallbackQuery
from pyrogram import filters 
from database import *
from pyromod.helpers import ikb
from dateutil.relativedelta import relativedelta
from pyrogram.types import ReplyKeyboardMarkup ,ReplyKeyboardRemove

database = Database()
channelID = "YOUR_TELEGRAM_CHANNEL_ID"

async def IsAd(_,client:Client , callback:CallbackQuery)->bool:
    content = callback.data.split('-')
    return ("deny" in content)or("pub" in content)
async def IsPurchase(_,client:Client , callback:CallbackQuery)->bool:
    content = callback.data.split('-')
    return ("acc" in content)or("rej" in content)
async def IsRequest(_,client:Client,callback:CallbackQuery)->bool:
    if callback.data.split("-")[1] == "unban" or callback.data.split("-")[1] == "banban":
        return True
    return False
Req = filters.create(IsRequest)
Ad = filters.create(IsAd)
Pur = filters.create(IsPurchase)
@Client.on_callback_query(Ad)
async def advertise_query(client:Client , callback:CallbackQuery):
    content = callback.data.split('-')
    user= await database.FindUser(int(content[0]))
    username = await client.get_chat(user.Id)
    if content[1] == "pub":
        await callback.message.copy(chat_id=channelID,reply_markup=ikb(
            [[["شماره تلفن",f"https://t.me/+98{int(user.PhoneNumber)}","url"]],
             [["چت تلگرام",f"https://t.me/{username.username}","url"]]]
        ))
        m = await database.ReadMessage(message_id=12)
        await client.send_message(chat_id=int(content[0]),text=m)
    else:
        user.Critical -=1
        if await database.UpdateUser(user):
            m1 = await database.ReadMessage(message_id=13)
            await client.send_message(chat_id=int(content[0]),text=m1)
    await callback.message.delete()
@Client.on_callback_query(Pur)
async def purchase_query(client:Client , callback:CallbackQuery):
    content = callback.data.split('-')
    content[0] = int(content[0])
    content[2] = int(content[2])
    if content[1] == "acc":
        user = await database.FindUser(content[0])
        user.AccountType = "VIP"
        if user.ExpireDate == "none":
            ex = date.today()+relativedelta(days=content[2])
            user.ExpireDate = str(ex)
        else:
            splited = [int(i) for i in user.ExpireDate.split('-')]
            cu = date(year=splited[0],month=splited[1],day=splited[2]) + relativedelta(days=content[2])
            user.ExpireDate = cu
        if await database.UpdateUser(user):
            m = await database.ReadMessage(message_id=10)
            await client.send_message(chat_id=content[0],text=m)
            if user.IsFirstTime == 1 and (str(callback.message.text).lower() == "new"):
                user.IsFirstTime = 0
                await database.UpdateUser(user)
        else:
            await client.send_message(chat_id=content[0],text="درخواست ارتقاء شما با مشکل مواجه شد لطفا با پشتیبانی درتماس باشید")
    else:
        m1 = await database.ReadMessage(message_id= 11)
        await client.send_message(chat_id=content[0],text=m1)
    await callback.message.delete()


@Client.on_callback_query(Req)
async def unban_query(client:Client , callback:CallbackQuery):
    info = callback.data.split("-")
    if info[1] == "unban":
        user = await database.FindUser(int(info[0]))
        user.Critical = 5
        if await database.UpdateUser(user=user):
            await client.send_message(chat_id=int(info[0]),text="درخواست رفع محدودیت شما پذیرفته شد و شما میتوانید آگهی های خود را ارسال کنید")
    else:
        await client.send_message(chat_id=int(info[0]),text="با درخواست رفع محدودیت شما موافقت نشد")
    await callback.message.delete()


@Client.on_message(filters.group&filters.command("change"))
async def change_message(client:Client , message:Message):
   id = await client.ask(chat_id=message.chat.id,text="شماره پیام را وارد کنید",user_id=message.from_user.id,filters=filters.text)
   currentmessage = await database.ReadMessage(message_id=int(id.text))
   await message.reply_text(text="پیام فعلی"+"\n\n"+currentmessage,reply_markup=ReplyKeyboardMarkup(
       [["لغو"]] , resize_keyboard=True 
   ))
   newmessage= await client.ask(chat_id=message.chat.id,user_id=message.from_user.id,text="پیام جدید را وارد کنید در صورت درخواست برای لغو لغو را انتخاب کنید")
   if newmessage == "لغو":await message.reply_text(text="عملیات با موفقیت لغو شد",reply_markup=ReplyKeyboardRemove())
   elif await database.UpdateMessage(message_id=int(id.text),new_message=newmessage.text):await message.reply_text(text="عملیات با موفقیت انجام شد",reply_markup=ReplyKeyboardRemove())