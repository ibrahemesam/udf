import requests
from datetime import datetime

def get_date():
    return datetime.strptime(\
        requests.get('https://adservice.google.com/adsid/google/ui')\
            .headers['Date'], "%a, %d %b %Y %H:%M:%S GMT")
    # uses google.com: so:-
    #   it is fast, reliable 
    #   & hacker cant actually modify google.com inside hosts file 
    #       because he supposed to use google alot,
    #           so it is hard to him to continuously change the hosts file

date = get_date()

"""
# keep track of get_date() method to detect crack
on every call of this method, the result will be saved to a list.
there is abnormal cases: when:-
    - [future_date, past_date]: the past came after the future: 
                                    that means the user changed the date to the past
    - there is big difference between datetime.now() and get_date() [rather than timezone diff]
    - get_date() allways return the same value
    - [FINALLY]: getting ip address of google.com is localhost || 127.0.0.7 || …etc
        if `socket.gethostbyname_ex("google.com")[2]` contains 127.0.0.1 || any other private ip
            also, test some URLs of that domain: eg:
                https://www.google.com/favicon.ico

"""
# using usb-key as auth instead of hdd-drive is good in case of that app license can be moved accross  multiple devces of the same user [ie: usb-key is movable, but hdd-drive is NoT]
"""
for offline permanent auth: use the serial number of the USB key
NB: initial licensing requires internet

0- I add the usb-serial-number to the github list
1- user runs the app
2- the app get hwids from github & get list of serials of connected devices
    then check common items of the two lists
        there is one common item
            which is the serial number of usb key

    [if no common item: that means: either the app is not licensed or the usb-key is not connected]:
        in this situation:-
            the app asks the user to insert the usb-key
a              (هيطلب منه مفتاح usb: ف هو لو معاه المفتاح هيحطه، لكن لو مش معاه: هيفهم انهلازم يشتريه)
3- the app saves the serial number (as encrypted string) into config.db



when regulary run the app:-
1- the app read config.db and decrypt the serial-number of usb-key
2- the app get list of serial-numbers of connected drives
3- the app checks if the serial-number is in that list
    [if true: app runs; if false: app asks the user to insert the usb-key]



#TODO: make procedure to change the usb-key in case that it is lost || user of hdd-drive want to move license to another pc [ie: to another hdd-drive]
1- user contacts me: "I lost my usb-key"
2- I ask him to buy any usb-drive and connect it to the pc to make it the new usb-key
3- this process requires internet connection
4- I remove the old usb-key 's serial-number from github
5- the user clicks on an option on the app-ui
    that option deletes the encrypted-serial-number from config.db
        then displays the new usb's serial number[faked] to the user
6- I add the new usb-key 's serial-number to github
7- the app closes
8- when the app run again, it follows the initial licensing process


---------------
for timed license: use Legend-Master 's auth.py
NB: timed license must be online to work


"""

# NB: refer: gnome-sound-recorder: "Decompiler is bad"

#In future releases I will create a licensing NodeJS websocket server [after learniing nodeJS udemy course]


#usb-key have to be connected just on startup during authentication
#   I can use builtin HDD/SSD instead
#       ,but: usb-key is more portable [ie: movable license]


#e-stock solution alternative:=> running app as client dows NoT require auth, but running it as server does

#TODO: make DNS-lockup verification on github when GET hwids.txt