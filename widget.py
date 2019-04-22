
import tkinter as tk
import socket
import requests as req
from random import randint
import json
import datetime
import time
def day_of_week(day_in_week):
    if (day_in_week == 0 ):
        return 'Monday'
    elif (day_in_week == 1 ):
        return 'Tuesday'
    elif (day_in_week == 2 ):
        return 'Wednesday'
    elif (day_in_week == 3 ):
        return 'Thursday'
    elif (day_in_week == 4 ):
        return 'Friday'
    elif (day_in_week == 5 ):
        return 'Saturday'
    elif (day_in_week == 6 ):
        return 'Sunday'
    else:
        return "Can't get day"
def time_format(_minute):
    if (_minute<10):
        return '0'+str(_minute)
    else:
        return str(_minute)
####################################
###GUI
####
window = tk.Tk()
window.title("Welcome to LikeGeeks app")
window.geometry('1280x720')
window.configure(background='black')
    #Show clock
clock=tk.Label(window, text='Clock',font=('Arial',30),fg='white',bg='black')
clock.place(relx=0.1,rely=0.2,anchor="center")
    #Show day of week
dayOfweek=tk.Label(window, text='Day of Week',font=('Arial',20),fg='white',bg='black')
dayOfweek.place(relx=0.05,rely=0.05,anchor="center")
    #Show day, month, year
day=tk.Label(window, text='Day',font=('Arial',15),fg='white',bg='black')
day.place(relx=0.1,rely=0.12,anchor="center")
today = datetime.datetime.now()
time1=''
##############
def tick():
    global time1
    # get the current local time from the PC
    time2 = time.strftime('%H:%M:%S')
    # if time string has changed, update it
    if time2 != time1:
        time1 = time2
        clock.config(text=time2)
    # calls itself every 200 milliseconds
    # to update the time display as needed
    # could use >200 ms, but display gets jerky
    clock.after(200, tick)
date_=''
def day_update():
    global date_
    date=time.strftime('%a, %d %b %Y')
    if date != date_:
        date_=date
        day.config(text=date)
    day.after(1000,day_update)
###############
def update_clock():

    clock.configure(text=(time_format(today.hour)+':'+time_format(today.minute)+':'+time_format(today.second)))
    day.configure(text=str(today.day)+'/'+str(today.month)+'/'+str(today.year))
    dayOfweek.configure(text=day_of_week(datetime.datetime.today().weekday()))
    window.after(500, update_clock)
#Show welcome text
lbl = tk.Label(window, text="Hello",font=('Arial',70),fg='white',bg='black')
lbl.place(relx=.5, rely=.5, anchor="center")
##Greeting 
#Hey/Hi/Hello  #How's it going #How are you doing #What's up What's going on What's new 
greeting=['Hey','Hi','Hello',"How's it going", 'How are you doing', "What's up", "What's going on", "What's new" ]
hello=greeting[0]
def update_greeting():
    global hello
    hello_=greeting[randint(0,len(greeting)-1)]
    if hello != hello_:
        hello = hello_
        lbl.config(text=hello)
    lbl.after(2000,update_greeting)

#Show news
news = tk.Label(window, text="News",font=('Arial',15),fg='white',bg='black')
news.place(relx=.5, rely=.9, anchor="center")

#Show notification
notifi = tk.Label(window, text="Notification",font=('Arial',20),fg='white',bg='black')
notifi.place(relx=.05, rely=.3, anchor="center")

#Show Temprature
temp = tk.Label(window, text="Temp",font=('Arial',30),fg='white',bg='black')
temp.place(relx=.9, rely=.05, anchor="center")

#Voice Regconize State
voice = tk.Label(window, text="Voice",font=('Arial',20),fg='white',bg='black')
voice.place(relx=.5, rely=.9, anchor="center")


    



#Configure day



#Get info about location
#https://api.ipgeolocation.io/ipgeo?apiKey=28bf9038d7544bf08e24ecd59aa54edd
#http://api.ipstack.com/check?access_key=ab8205afa89f4541cc3e87cec32e9d04
location=req.get("https://api.ipgeolocation.io/ipgeo?apiKey=28bf9038d7544bf08e24ecd59aa54edd") 
location_json=json.loads(location.text)
print(location_json['state_prov'],location_json['district'])

#Get weather from OpenWeatherMap
str="https://samples.openweathermap.org/data/2.5/weather?lat="+str(location_json['latitude'])+"&lon="+str(location_json['longitude'])+"&appid=b6907d289e10d714a6e88b30761fae22"
weather=req.get(str)
print(weather.text)
weather_json=json.loads(weather.text)
print (weather_json['main']['temp'])
temp.configure(text=weather_json['main']['temp'],fg='white',bg='black')
tick()
day_update()
update_greeting()
window.mainloop()
#