According to use this scripts u need to change some lines of scripts at the begining
in __main__.py lines 11 to 15 you need to fill this information with your own .
in  PrivateHandlers.py lines 7,8 and 27
in GroupHandlers.py line 12

this bot will work in some steps dicribed below:
    1- the user will submit to the robot
    2- user must upgrade his account to be able to publish advertises on your channel this upgrade has following steps:
        2:1- user goes to information (مشخصات) menu 
        2:2- user selects purchase/renew account (خرید/تمدید اشتراک) and sends 'VIP' or recipe of the money transfer for u and you
        2:3- this message will be sent to your Admins group with 2 inline keyboard markups (accept and reject) 
        2:4- if you or your admins press accept the user which sent the recipe will be upgraded to vip user for 40 days 
    3- after user being upgraded to VIP member user could select submit advertise (ثبت/آگهی) and publishing the advertize goes trough these steps :
        3:1- user sends his/her ad to robot in this step robot ckecks if the text of the ad contains any bad word or not (these words will be manually added by Admin) if not the message will be copied to admins group
        3:2 the copied message in admins group will have 3 inline buttons consist of :
            *:accept
            **: username of the sender wich is linked to his/her profile 
            ***: reject
        in this step admins will check the ad image and the text will be checked in second time if admins press accept botton the message will be deleted from admins group and will be copied in the ad channel by to new inline buttons :
            *: the sender user name 
            **: the sender phonenumber
        and user will be notified in robot  that his ad is now pulished on channel
        if admins press reject button the message will be deleted from admins group and the user will be notified that his ad was deleted by admins and he received a negative point 
        (user with 5 negative points will be banned from bot)

featuers of robot :
    1: after submit in robot user can edit his infromation in inforamation->edit information 
    (ویرایش مشخصات <- مشخصات)
    2: each day app will check all of vip users and if the VIP priod is close to end (3 days remaining) or its over the user will be notified in case of end the user account will Degrade to regular user 

admin commadns : 
    1: /change this command only works in the admins group and is used to change communication messages of robot
    2: /bad this message is only use able in robot private chat with admin and is used to add badwords to robots data base