import aiosqlite
class User():
    def __init__(self,id:int,fullname:str,phonenumber:str,shopName:str,accountType:str = "معمولی",expireDate:str = "none",
                 critical:int = 5 , firsttime:int=1) -> None:
        """
        this class will be used to crate instances from Users stored in Useres table of Database
        Id -> numerical id of an account in telegram which is unique for each account in telegram so is primary key of Table
        FullName -> FirstName + LastName of the user
        PhoneNumber -> the phonenumber of user this number will be shown to users of advertises channel beside users username for contact
        ShopName -> the ShopName of user
        AccountType -> by logic of this bot will recive to types 1-'regular translated to Farsi' 2-'VIP'
        ExpireDate -> expration of the Vip period wich take whether 'none' or a date 
        Critical -> the number of usres rejected ad's which is defualted to 5 at first and will redused if usre takes rejected ad's and if this number redused to 0 the user will periminitly ban from bot and cant publish any new ad
        FirstTime -> each user could get vip promotion onece and this field will show if user used this or not 1 means this user never used this opportunity and can still use it and 0 means the user used it and cant any more
        """
        self.Id = id
        self.FullName = fullname
        self.ShopName = shopName
        self.PhoneNumber = phonenumber
        self.AccountType = accountType
        self.ExpireDate = expireDate
        self.Critical = critical
        self.IsFirstTime = firsttime
class Database():
    def __init__(self) -> None:
        """
        this class will hanndel the DataBase stuff and consist the functions for data base 
        which will CURD oprations on data base all of functions will work synchronously for the best 
        performance on the data base except ReadBadWords function wich is not like other functions this
        function only called once in PrivateHandlers.py line 11. according to my calculations for redusing 
        attemps to DataBase BadWords list is created and for checking the message wich is sent to robot 
        to does not contain the filtered word (badwords) we will check this list and never(execpt first lunch)
        read the words from DataBase and if new words will be filtered by admins the word at first will be added to
        DataBase synchronously and then will be appended to this list.
        """
        self.BadWords = list()    
    async def FindUser(self,userid:int)->User:
        """
        Finds a user by his Telegram numrical id (which will be passed to function as userid parameter) from Users tabel in 
        DataBase and creates an instace of User class according to metioned row from DataBase
        """
        try:
            user = None
            async with aiosqlite.connect("database.db") as connection:
                async with connection.execute(f"SELECT * FROM User WHERE id = {userid};") as cursor:
                    temp = await cursor.fetchone()
                    if temp != None:
                        user = User(id=int(temp[0]),fullname=temp[1],phonenumber=temp[2],
                                shopName=temp[3],accountType=temp[4],expireDate=temp[5],critical=int(temp[6]),firsttime=int(temp[7]))
            if user == None:raise Exception("not found")
            else: return user
        except Exception as e: raise e
    async def AddUser(self,user:User)->bool:
        """
        receives a User calss instance as a parameter and will add this user to DataBase returns True if opration ends successful 
        and returns False if something goes wrong during process
        """
        try:
            async with aiosqlite.connect("database.db") as connection:
                async with connection.execute(f"INSERT INTO User VALUES ({user.Id},'{user.FullName}','{user.PhoneNumber}','{user.ShopName}','{user.AccountType}','{user.ExpireDate}',{user.Critical},{user.IsFirstTime});") as cursor:
                    await connection.commit()
            return True
        except Exception as e:
            return False        
    async def AddBadWord(self,badword:str)->bool:
        """
        receives a string  as a parameter and will add this word to DataBase returns True if opration ends successful 
        and returns False if something goes wrong during process
        """
        try:
            async with aiosqlite.connect("database.db") as connection:
                async with connection.execute(f"INSERT INTO BadWord VALUES ('{badword}');") as cursor:
                    await connection.commit()
            self.BadWords.append(badword)
            return True
        except:
            return False
    async def UpdateUser(self,user:User)->bool:
        """
        receives a User calss instance as parameter this user logicaly was existed in DataBase bofore but some fields of this user
        for some reasons(end of VIP period or ....) was changed during the time so this user needs to be changed on DataBase to
        returns True if opration ends successful and returns False if something goes wrong during process
        """
        try:
            async with aiosqlite.connect("database.db") as connection:
                async with connection.execute(f"UPDATE User SET fullName='{user.FullName}' , phoneNumber='{user.PhoneNumber}' , shopName='{user.ShopName}' , accountType='{user.AccountType}' , expireDate = '{user.ExpireDate}' , critical = {user.Critical} , firstTime={user.IsFirstTime} WHERE id = {user.Id};") as cursor:
                    await connection.commit()
            return True
        except Exception as e:
            return False
    def ReadBadWords(self)->bool:
        """
        this function will read all of filtered words From BadWord Table of DataBase and will update BadWord list of instance 
        this list will be used when a user wants to publish a Advertise on the channel if the ad sent by user does have one of these
        words the ad will not be sent to admins to aprove the picture or the rest of things in this case the user will not recive a critical 
        but if admins reject his/her add the user will recive a critical
        returns True if oprations ends successful and returns False if something goes wrong during process
        """
        try:
            with aiosqlite.connect("database.db") as connection:
                with connection.execute(f"SELECT * FROM BadWord;") as cursor:
                    for i in cursor.fetchall():
                        self.BadWords.append(i[0])
            return True
        except: return False
    async def ReadVIPUsers(self)->list:
        """
        this function will read all of users with VIP field from Users table from Database
        and will return a list of these users this opration will be done once a day using an Scheduler in __main__.py file 
        becuse this users needs to be chacked for their expiration VIP date and the action will be taken by their condion in mentioned 
        Scheduler.
        """
        try:
            users = list()
            async with aiosqlite.connect("database.db") as connection:
                async with connection.execute(f"SELECT * FROM User WHERE accountType = 'VIP';") as cursor:
                    temp = await cursor.fetchall()
                    if temp != None:
                        for i in temp:
                            users.append(User(id=int(i[0]),fullname=i[1],phonenumber=i[2],
                                shopName=i[3],accountType=i[4],expireDate=i[5],critical=int(i[6]),firsttime=int(i[7])))
            if len(users) != 0:
                return users
            else: return list()
        except Exception as e: raise Exception(e)
    async def ReadMessage(self,message_id:int)->str:
        """
        there is 13 messges which are used in the robot to communicate with users so admins will need to change these messages 
        by considering the situation (ex. changeing the cost of Vip account) this function will find a specific message by its id (1-13)
        and shows the admin the message to prevent any miss changes in messages rises an exception in case some thing goes wrong
        """
        try:
            async with aiosqlite.connect("database.db") as connection:
                async with connection.execute(f"SELECT message FROM Messages WHERE id = {message_id};") as cursor:
                    temp = await cursor.fetchone()
                    return str(temp[0])
        except Exception as e:
            raise Exception(e)      
    async def UpdateMessage(self,message_id:int,new_message:str) ->bool:
        """
        gets id of an message as parameter and update the paired message in DataBase.
        returns True of opration is successful and returns False if not
        """
        try:
            async with aiosqlite.connect("database.db") as connection:
                async with connection.execute(f"UPDATE Messages SET message = '{new_message}' WHERE id = {message_id};") as cursor:
                    await connection.commit()
            return True
        except:
            return False