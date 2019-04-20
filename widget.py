
import tkinter as tk
import socket
import requests as req
from random import randint
import json
def day_of_week(day_in_week):
    if (day_in_week == 1 ):
        return 'Monday'
    elif (day_in_week == 2 ):
        return 'Tuesday'
    elif (day_in_week == 3 ):
        return 'Wednesday'
    elif (day_in_week == 4 ):
        return 'Thursday'
    elif (day_in_week == 5 ):
        return 'Friday'
    elif (day_in_week == 6 ):
        return 'Saturday'
    elif (day_in_week == 7 ):
        return 'Sunday'
    else:
        return "Can't get day"
####################################
###GUI
####
window = tk.Tk()
window.title("Welcome to LikeGeeks app")
window.geometry('1280x720')
window.configure(background='black')

#Show clock
clock=tk.Label(window, text='Clock',font=('Arial',30),fg='white',bg='black')
clock.place(relx=0.05,rely=0.2,anchor="center")
#Show day of week
dayOfweek=tk.Label(window, text='Day of Week',font=('Arial',20),fg='white',bg='black')
dayOfweek.place(relx=0.05,rely=0.05,anchor="center")
#Show day, month, year
day=tk.Label(window, text='Day',font=('Arial',15),fg='white',bg='black')
day.place(relx=0.05,rely=0.12,anchor="center")

#Show welcome text
lbl = tk.Label(window, text="Hello",font=('Arial',70),fg='white',bg='black')
lbl.place(relx=.5, rely=.5, anchor="center")
##Greeting 
#Hey/Hi/Hello  #How's it going #How are you doing #What's up What's going on What's new 
greeting=['Hey','Hi','Hello',"How's it going", 'How are you doing', "What's up", "What's going on", "What's new" ]

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
def call_back():
   
        lbl.configure(text=greeting[randint(0,len(greeting)-1)],fg='white',bg='black')

button=tk.Button(window,text='Click',command=call_back)
button.place(relx=0,rely=0,anchor='center')
#Get Time from Internet
try:
    resp = req.get("http://worldtimeapi.org/api/timezone/Asia/Ho_Chi_Minh")
    json_time=json.loads(resp.text)
except ConnectionError as e:
    dayOfweek.configure(text="Can't get time",fg='white',bg='black')
    



#Configure day
dayOfweek.configure(text=day_of_week(json_time['day_of_week']),fg='white',bg='black')
#Configure Time
time_GMT=json_time['datetime']
day.configure(text=''+time_GMT[8:10]+'/'+time_GMT[5:7]+'/'+time_GMT[0:4],fg='white',bg='black')

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
window.mainloop()
#