from pyromod import Client
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from database import *
from datetime import date
from dateutil.relativedelta import relativedelta
alarm_days = 3
database = Database()

plugs = dict(root="plugins")
app = Client(
    name="YOUR_SESSION_NAME",
    api_id=YOUR_API_ID,#this parameter is an integer
    api_hash="YOUR_API_HASH",
    bot_token="YOUR_BOT_TOKEN",
    plugins= plugs
)

async def CheckUsers():
    try:
        today = date.today()
        vipusers = await database.ReadVIPUsers()
        for user in vipusers:
            elements = [int(i) for i in user.ExpireDate.split('-')]
            exdate = date(year=elements[0],month=elements[1],day=elements[2])
            if exdate == today:
                user.AccountType = "معمولی"
                user.ExpireDate = "none"
                if await database.UpdateUser(user):
                    m = f"کاربر عزیز {user.FullName} اشتراک شما به پایان رسید شما میتوانید جهت ارتقاء به منوی مشخصات مراجعه کنید"
                    await app.send_message(chat_id=user.Id,text=m) 
            elif exdate == today + relativedelta(days=alarm_days):
                m = f"""کاربر عزیز {user.FullName} اشتراک شما تا 3 روز آینده به پایان میرسد لطفا در صورت تمایل میتوانید نصبت به ارتقاء مجدد اکانت خود اقدام کنید با تشکر"""
                await app.send_message(chat_id=user.Id,text=m)
    except:
        pass

scheduler = AsyncIOScheduler()
scheduler.add_job(CheckUsers, "interval", seconds=86400)
scheduler.start()
app.run()