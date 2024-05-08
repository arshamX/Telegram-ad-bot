from pyrogram import filters
from pyromod import Client , Message
from pyromod.helpers import ikb
from pyrogram.types import ReplyKeyboardMarkup
from database import *

adminsGroupID = YOUR_GROUP_NUMERICAL_ID #is a negative integer 
channelID = "YOUR_TELEGRAM_CHANNEL_ID"

database = Database()

keyboard = ReplyKeyboardMarkup(
    [["خرید/تمدید اشتراک 💵","ویرایش اطلاعات 📝"],["بازگشت 🔙","درخواست رفع محدودیت"]],resize_keyboard=True
)

async def BannedUser(_,client:Client,message:Message) -> bool:
    user = await database.FindUser(userid=message.from_user.id)
    if user.Critical > 0:
        return False
    return True

async def NotInChannel(client:Client,usedid:int)->bool:
    try:
       user = await client.get_chat_member(chat_id=channelID,user_id=usedid)
       return False
    except :
        return True

async def IsAdmin(_,client:Client,message:Message)->bool:
    return message.from_user.id == YOUR_TELEGRAM_NUMERICAL_ID # is an integer number 

async def LegitState(text:str) -> bool:
    for i in database.BadWords:
        if i in text:
            return False
    return True

async def IsPermium(_,client:Client,message:Message)->bool:
    try :
        user = await database.FindUser(message.from_user.id)
        if user.AccountType == "VIP":
            return True
        return False
    except:
        return False

async def IsLogedIn(_,client:Client,message:Message)->bool:
    try:
        user = await database.FindUser(userid=message.from_user.id)
        if user.Id == message.from_user.id:
            return True
        else:
             return False
    except Exception as e:
        return False

async def IsNew(_,client:Client,message:Message) -> bool:
    if (message.text).lower() == "new":return True
    return False

async def IsBanned(id:int)->bool:
    user = await database.FindUser(userid= id)
    print(user.Critical)
    if user.Critical > 0:
        return False
    else : return True

Logged = filters.create(IsLogedIn)
Permium = filters.create(IsPermium)
Admin = filters.create(IsAdmin)
Banned = filters.create(BannedUser)
New = filters.create(IsNew)



@Client.on_message(filters.private & filters.command("initdatabase") & Admin)
async def on_init(client,message):
    if await database.ReadBadWords():
        await message.reply_text(text="دیتا بیس با موفقیت اغاز به کار کرد")
@Client.on_message(filters.command("start") & filters.private & Logged & ~filters.media_group)
async def On_start_loggedin(client:Client , message:Message):
    user = await database.FindUser(message.from_user.id)
    m = await database.ReadMessage(message_id=1)
    await message.reply_text(f"{user.FullName} "+"\n"+m,reply_markup=ReplyKeyboardMarkup(
        [["مشخصات 🤵‍♂️","ثبت آگهی 📥"]] , resize_keyboard=True
    ))
@Client.on_message(filters.command("start") & filters.private & ~Logged)
async def On_start_signup(client:Client , message:Message):
   chatid = message.from_user.id
   m = await database.ReadMessage(message_id=2)
   await message.reply_text(m)
   fullname = await client.ask(chat_id= chatid,text="لطفا نام و نام خانوادگی خود را وارد کنید" , filters=filters.text)
   tphonenumber = await client.ask(chat_id= chatid,text="لطفا شماره تلفن خود را وارد کنید (مثال 09123456789)" ,filters=filters.text)
   while len(tphonenumber.text) != 11:
          tphonenumber = await client.ask(chat_id= chatid,text="شماره تلفن وارد شده صحیح نیست دوباره امتحان کنید (مثال 09123456789)" ,filters=filters.text)
   shop = await client.ask(chat_id= chatid,text="لطفا نام فروشگاه خود را وارد کنید" , filters=filters.text)
   tuser = User(id=chatid,fullname=fullname.text,phonenumber=tphonenumber.text,shopName=shop.text)
   if await database.AddUser(tuser):
        if await NotInChannel(client,int(message.from_user.id)):
            await message.reply_text(text="شما در چنل عضو نیستید جهت عضویت از دکمه زیر استفاده کنید" , reply_markup=ikb(
                [[["عضویت در چنل",f"https://t.me/{channelID}",f"url"]]]
            ))
        m2 = await database.ReadMessage(message_id=1)
        await message.reply_text(f"{tuser.FullName} "+"\n"+m2,reply_markup=ReplyKeyboardMarkup(
        [["مشخصات 🤵‍♂️","ثبت آگهی 📥"]],resize_keyboard=True

    ))     
@Client.on_message(filters.private & filters.regex("مشخصات") & Logged)
async def on_information(client:Client , message:Message):
    user = await database.FindUser(message.from_user.id)
    expiredate = user.ExpireDate.split("-")
    if len(expiredate) != 3:
        expiredate = "none"
    else :
        expiredate = f"{user.ExpireDate.split('-')[2]}-{user.ExpireDate.split('-')[1]}-{user.ExpireDate.split('-')[0]}"
    statement = f"""مشخصات شما

    نام و نام خانوادگی : {user.FullName}

    شماره تلفن : {user.PhoneNumber}

    نام فروشگاه : {user.ShopName}

    نوع اشتراک : {user.AccountType}

    تاریخ اتمام اشتراک : {expiredate}

    تعداد خطا : {5-user.Critical}

🤵‍♂️🤵‍♂️🤵‍♂️🤵‍♂️
    """
    await message.reply_text(text=statement , reply_markup=keyboard)
@Client.on_message(filters.private & filters.regex("ویرایش اطلاعات") & Logged)
async def on_editinfo(client:Client , message:Message):
    user = await database.FindUser(message.from_user.id)
    await message.reply(text="در هر مراحله اطلاعات خواسته شده را وارد کنید در صورت عدم تمایل به تغییر\n  یک فیلد خاص دکمه «ردشدن» را فشار دهید درصورت درخواست انصراف دکمه «انصراف» را فشار دهید",
                        reply_markup=ReplyKeyboardMarkup(
                            [["انصراف","رد شدن"]] ,resize_keyboard=True
                        ))
    name = await client.ask(chat_id=user.Id , text="نام و نام خانوادگی خود را وارد کنید" , filters=filters.text)
    if name.text == "انصراف":
        await message.reply_text(text="تغیررات ذخیره نشد",reply_markup=keyboard)
        return
    tphonenumber = await client.ask(chat_id= user.Id,text="لطفا شماره تلفن خود را وارد کنید (مثال 09123456789)" ,filters=filters.text , )
    while len(tphonenumber.text) != 11 and tphonenumber.text != "رد شدن" and tphonenumber.text != "انصراف":
        tphonenumber = await client.ask(chat_id= user.Id,text="شماره تلفن وارد شده صحیح نیست دوباره امتحان کنید (مثال 09123456789)" ,filters=filters.text)
    if tphonenumber.text == "انصراف":
        await message.reply_text(text="تغیررات ذخیره نشد",reply_markup=keyboard)
        return
    shop = await client.ask(chat_id= user.Id,text="لطفا نام فروشگاه خود را وارد کنید" , filters=filters.text)
    if name.text == "رد شدن":
        name = user.FullName
    else:
        name = name.text
    if tphonenumber.text == "رد شدن":
        tphonenumber = user.PhoneNumber
    else:
        tphonenumber = tphonenumber.text
    if shop.text == "رد شدن":
        shop = user.ShopName
    elif shop.text == "انصراف":
        await message.reply_text(text="تغیررات ذخیره نشد",reply_markup=keyboard)
        return
    else:
        shop= shop.text
    tuser = User(id=user.Id,fullname=name,phonenumber=tphonenumber,shopName=shop,accountType=user.AccountType,expireDate=user.ExpireDate,critical=user.Critical)
    if await database.UpdateUser(tuser):
        await message.reply_text(text="تغیررات ذخیره شد",reply_markup=keyboard)
@Client.on_message(filters.private & Logged & filters.regex("بازگشت"))
async def on_back(client:Client,message:Message):
    await message.reply_text(text="منوی اصلی",reply_markup=ReplyKeyboardMarkup(
         [["مشخصات 🤵‍♂️","ثبت آگهی 📥"]] , resize_keyboard=True
    ))
@Client.on_message(filters.private & Logged & filters.regex("خرید"))
async def on_purchase(client:Client,message:Message):
    statement = await database.ReadMessage(message_id= 3)
    statement2 = await database.ReadMessage(message_id= 4)
    await message.reply_text(text=statement )
    await message.reply_text(text=statement2, reply_markup=ReplyKeyboardMarkup(
        [["صرف نظر"]] , resize_keyboard=True))
    user = await database.FindUser(message.from_user.id)
    res = await client.listen(user_id= message.from_user.id , filters=filters.photo | (filters.text & (New|filters.regex("صرف نظر"))) | filters.document | filters.media_group)
    if res.photo or (str(res.text).lower() == "new" and user.IsFirstTime == 1):
        await res.copy(chat_id = adminsGroupID , reply_markup=ikb(
            [[["1 ماه",f"{res.from_user.id}-acc-40"]],[[f"@{res.from_user.username}",f"https://t.me/{res.from_user.username}","url"]],[["رد 🚫",f"{res.from_user.id}-rej-0"]]]
        ) )
        m = await database.ReadMessage(message_id=5)
        await message.reply_text(text=m ,reply_to_message_id=res.id
                                ,reply_markup=ReplyKeyboardMarkup(
                [["مشخصات 🤵‍♂️","ثبت آگهی 📥"]] , resize_keyboard=True 
                                                                ))
    elif (str(res.text).lower() == "new" and user.IsFirstTime == 0):
        m = "کاربر گرامی شما یک بار از اشتراک رایگان استفاده کرده اید"
        await message.reply_text(text=m,reply_markup=keyboard)
    elif res.text == "صرف نظر":
            await message.reply_text(text="منو اطلاعات شخصی",reply_markup=keyboard)
@Client.on_message(filters.private & Logged & Permium & filters.regex("ثبت آگهی") & ~Banned)
async def on_advertise(client:Client,message:Message):
    await message.reply_text("لطفا آگهی خود را ارسال کنید",reply_markup=ReplyKeyboardMarkup(
        [["صرف نظر"]] , resize_keyboard= True
    ))
    res = await client.listen(chat_id=message.from_user.id , filters= filters.photo | filters.text | filters.document)
    if (res.photo or res.document and await LegitState(res.caption)) or (res.text and res.text != "صرف نظر" and await LegitState(res.text)):
        await res.copy(chat_id = adminsGroupID,reply_markup=ikb(
            [[["تایید ✅",f"{res.from_user.id}-pub"],["رد 🚫",f"{res.from_user.id}-deny"]],[[f"@{res.from_user.username}",f"https://t.me/{res.from_user.username}","url"]]]
        ))
        m = await database.ReadMessage(message_id=6)
        await message.reply_text(text=m ,reply_to_message_id=res.id
            ,reply_markup=ReplyKeyboardMarkup(
            [["مشخصات 🤵‍♂️","ثبت آگهی 📥"]] , resize_keyboard=True 
            ))
    elif res.text == "صرف نظر":
        await message.reply_text(text="منو اصلی",reply_markup=ReplyKeyboardMarkup(
        [["مشخصات 🤵‍♂️","ثبت آگهی 📥"]] ,resize_keyboard=True
        ))
    else:
        m1 = await database.ReadMessage(message_id=7)
        await message.reply_text(text= m1,reply_to_message_id=res.id
        ,reply_markup=ReplyKeyboardMarkup(
        [["مشخصات 🤵‍♂️","ثبت آگهی 📥"]] , resize_keyboard=True
        )) 
@Client.on_message(filters.private & Logged & ~Permium & filters.regex("ثبت آگهی"))
async def on_advertise_notPermium(client:Client,message:Message):
    m = await database.ReadMessage(message_id= 8)
    await message.reply_text(text= m)
@Client.on_message(filters.private & Logged & Permium & filters.regex("ثبت آگهی") & Banned)
async def on_advertise_banned(client:Client , message:Message):
    m = await database.ReadMessage(message_id=9)
    await message.reply_text(text=m)
@Client.on_message(filters.private & filters.command("bad") & Admin)
async def on_bad(client:Client,message:Message):
    counter = 0
    while True:
        res = await client.ask(chat_id=message.from_user.id,text=" کلمه ممنوع جدید را بفرستید و در صورت عدم تمایل به ادامه کاراکتر # را ارسال کنید",filters=filters.text)
        if res.text == '#':
            break
        else:
            await database.AddBadWord(res.text)
            counter+=1
    await message.reply_text(text=f"تعداد {counter} کلمه جدید فیلتر شد")
@Client.on_message(filters.private & filters.command("unbad") & Admin)
async def un_bad(client:Client , message:Message):
    wordsStr = "bad word list"
    for i in database.BadWords:
        wordsStr += "\n"
        wordsStr += str(i)
    if len(wordsStr)== 13 :
        await message.reply_text(text="کلمه فیلتر شده ای وجود ندار",reply_markup=keyboard)
    else:
        k = ReplyKeyboardMarkup(
            [["لغو"]],resize_keyboard=True
        )
        await message.reply_text(text=wordsStr , reply_markup=k)
        res = await client.ask(chat_id=message.from_user.id, text="لطفا  کلمه ای که میخواهید از فیلتر خارج کنید را وارد کنید" ,filters=filters.text)
        if(res.text == "لغو"):
            await message.reply_text(text="منو اصلی",reply_markup=keyboard)
            return
        if await database.RemoveBadWord(res.text):
            await message.reply_text("کلمه با موفقیت از لیست فیلتر ها حذف شد",reply_markup=keyboard)
        else:
            await message.reply_text("ایراد در از  فیلتر خارج کردن کلمه",reply_markup=keyboard)
@Client.on_message(filters.private & filters.regex("درخواست رفع محدودیت"))
async def un_ban(client:Client , message:Message):
    if not (await IsBanned(message.from_user.id)):
        await message.reply_text("اکانت شما مصدود نیست" , reply_markup= keyboard)
    else:
        await message.reply_text("نتیجه در خواست بازبینی شما به شما اطلاع داده  خواهد شد " , reply_markup= keyboard)
        await client.send_message(chat_id=adminsGroupID,text="درخواست رفع محدودیت", reply_markup=ikb(
            [[["تایید ✅",f"{message.from_user.id}-unban"],["رد 🚫",f"{message.from_user.id}-banban"]],
             [[f"@{message.from_user.username}",f"https://t.me/{message.from_user.username}","url"]]]
        ))