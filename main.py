# SYSTEM LIBRARY IMPORTS
import json
import os
import random
import speech_recognition as sr
import pyttsx3
from tkinter import *
from threading import Thread
import webbrowser
import yagmail
from bs4 import BeautifulSoup
import requests
import urllib.parse
from config import *
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Say
# GLOBALS

ASSISTANT_NAME = 'Bruno'.lower()
loop = ["Could you speak a bit louder","Sorry, I didn't get that one. Could you please repeat","Could you try that again"]

# COLORS
WINDOW_BG = '#203645'
CHAT_BG = '#344c5c'
BOT_CHAT_BG = "#128c7e"
USER_CHAT_BG = '#075E54'
TEXT_COLOR = '#ffffff'
CURRENT_STATUS_LABEL_BG = '#dfdfdf'


if os.path.exists('userData') == False:
    os.mkdir('userData')

#########################################################################################
# SETTING UP TEXT TO SPEECH ENGINE 
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)

def speak(text):
    bot_chat = Label(chat_frame,text=text, bg=BOT_CHAT_BG, fg=TEXT_COLOR,justify=LEFT, wraplength=250,font=('Montserrat',12,'bold'))
    bot_chat.pack(anchor='w',ipadx=2,ipady=2,pady=10,padx=10)    
    engine.say(text)
    engine.runAndWait()


# SETTING UP SPEECH TO TEXT
def takeCommand(first):
    global status_label,chat_frame
    r = sr.Recognizer()
    r.pause_threshold = 1
    query=""
    with sr.Microphone() as source:
        print("Listening...")
        status_label['text'] = "Listening..."
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)

    try:
        print("Processing...")
        status_label['text'] = "Processing..."
        query = r.recognize_google(audio,language='en-in')
        
    except Exception as e:
        print(e)
    if(not first and len(query)==0):
        speak(loop[random.randint(0,2)])
        return takeCommand(False)
        
    if first:
        for widget in chat_frame.winfo_children():
            widget.destroy()

    user_chat = Label(chat_frame, text=query, bg=USER_CHAT_BG,fg=TEXT_COLOR, justify=RIGHT,wraplength=250,font=('Montserrat',12,'bold'))
    user_chat.pack(anchor='e',ipadx=2,ipady=2,pady=10,padx=10)  
    return query.lower()
#######################################################################################

############################### ADD CONTACT #########################################

popup_window = None
name = None
number = None
email = None
newContactName = None

def CT_Popup():
    global popup_window,name,number,email
    popup_window = Tk()
    popup_window.title('Add Contact')
    popup_window.iconbitmap('./static/images/contacts.ico')

    popup_window.configure(bg='white',width=300,height=400)
    popup_window.pack_propagate(False)


    Label(popup_window,text='Name',font=('Montserrat',12),bg='white').pack(padx=5,pady=5)
    name = Entry(popup_window,font=('Montserrat',12),relief=FLAT,bd=5,bg='#DCDCDC')
    name.pack(padx=5,pady=5)

    Label(popup_window,text='Number(with Country Code)',font=('Montserrat',12),bg='white').pack(padx=5,pady=5)
    number = Entry(popup_window,font=('Montserrat',12),relief=FLAT,bd=5,bg='#DCDCDC')
    number.pack(padx=5,pady=5)
    
    Label(popup_window,text='Email',font=('Montserrat',12),bg='white').pack(padx=5,pady=5)
    email = Entry(popup_window,font=('Montserrat',12),relief=FLAT,bd=5,bg='#DCDCDC')
    email.pack(padx=5,pady=5)
    
    Button(popup_window,text='Add Contact',bg='#14A769',font=('Montserrat',12),relief=FLAT,fg='white',command=storeContact).pack(padx=20,pady=10)
    popup_window.mainloop()


def storeContact():
    global popup_window,name,number,newContactName,email
    contacts[name.get().lower()] = []
    contacts[name.get().lower()]+=[number.get(), email.get()]
    newContactName = name.get().lower()
    with open('./userData/contacts.json','w') as f:
        json.dump(contacts,f)

    popup_window.destroy()


###############################  WHATSAPP ####################################

def handleWhatsapp():
    global newContactName
    contactsFile = open('./userData/contacts.json','r')
    contacts = json.load(contactsFile)
    contactsFile.close()
    speak("Sure. Who do you want to send the message to?")
    person = takeCommand(False)
    
    print(contacts)
    if person in contacts:
        sendMessage(person)
    else:
        speak(person+" is not in my contacts list. Please fill the details to add a new contact.")
        CT_Popup()
        sendMessage(newContactName)

def sendMessage(person):
    phoneNo = contacts[person][0]
    speak("What text do you want to send?")
    text = takeCommand(False)
    url = "https://web.whatsapp.com/send?phone=" + phoneNo + "&text=" + text

    speak("Sending message : " + text + " to " + person)

    webbrowser.open(url)
    import time
    from pynput.keyboard import Key, Controller
    time.sleep(10)
    k = Controller()
    k.press(Key.enter)

    speak("Your message has been sent")

#################################  WHATSAPP ENDS ################################################

################################# EMAIL AUTOMATION ##############################################

def handleEmail():
    
    global newContactName

    contactsFile = open('./userData/contacts.json','r')
    contacts = json.load(contactsFile)
    contactsFile.close()

    speak("Sure. Who do you want to send the mail to?")
    person = takeCommand(False)

    if person in contacts:
        sendEmail(person)
    else:
        speak(person+" is not in my contacts list. Please fill the details to add a new contact.")
        CT_Popup()
        sendEmail(newEmailName)

def sendEmail(person):
    recipient = contacts[person][1]

    yag = yagmail.SMTP(GMAIL_USERNAME,GMAIL_PASSWORD)

    speak("What is the subject of the mail?")

    subject = takeCommand(False)

    speak("What is content of the mail?")

    content = takeCommand(False)

    yag.send(to=recipient,subject=subject,contents=content)

    speak("The mail has been sent")


#################################  QUERY INTERPRETATION #########################################
def wordExists(listOfWords,query):
    for word in listOfWords:
        if word in query:
            return True
    return False

################################# VOICE MESSAGE BY CALL #########################################
contactsFile = open('./userData/contacts.json','r')
contacts = json.load(contactsFile)
contactsFile.close()

def handleCall():
    global contacts,newContactName
    speak("Sure. Who do you want to make a voice call to?")
    person = takeCommand(False)
    print(person)
    print(contacts)
    if person in contacts:
        makeACall(person)
    else:
        speak(person+" is not in my contacts list. Please fill the details to add a new contact.")
        CT_Popup()
        makeACall(newContactName)

def makeACall(person):
    
    speak("What voice message do you want to send?")
    voice_m = takeCommand(False)
    DIAL_NUMBER = contacts[person]

    response = VoiceResponse()
    response.say(voice_m, voice='alice', language='en-IN')
    
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

    client.calls.create(to=DIAL_NUMBER, from_=TWILIO_PHONE_NUMBER, twiml=str(response))
    speak('Your voice message has been sucessfully sent to '+person)

###############################################################################################

def interpretCommand():

    while True:
        query = takeCommand(True).lower()
        if "weather" in query:
            ip = requests.get('https://api.ipify.org').text
            url = 'http://ip-api.com/json/'
            url += ip

            location = requests.get(url).json()

            city = location['city']
            country = location['country']
            weatherQuery = "How is weather in " + city + ", " + country + "?"

            Wurl = "http://api.wolframalpha.com/v1/result?"
            Wurl += 'appid=' + APP_ID
            Wurl += '&i=' + weatherQuery

            res = requests.get(Wurl)
            print(res.text)
            speak(res.text)

        elif "holidays" in query:
            from googleCalendar import listHolidays
            holidays = listHolidays()
            if not holidays:
                speak("No upcoming holidays")
            else:
                speak("Here are the upcoming holidays")
                for holiday in holidays:
                    speak(holiday)          

        elif "calendar" in query:
            speak("Sure, what do you want to do in the calendar? Create an event or get list of events?")
            calendarCommand = takeCommand(False)
            from googleCalendar import getEvents,createEvent
            if "list" in calendarCommand:
                events = getEvents()
                if not events:
                    speak("You have no upcoming events.")
                else:
                    speak("Here are your upcoming events")
                    for event in events:
                        speak(event)
            elif "create" in calendarCommand:
                speak("What is the title of the event?")
                title = takeCommand(False)
                speak("When is the event? Please respond in the format day, month name and year")
                date = takeCommand(False).split(' ')
                speak("At what time? Example : 16 hours 30 minutes")
                time = takeCommand(False).split(' ')

                if len(date) != 3 or len(time) != 4:
                    speak("Datetime format error, try again")

                else:
                    day,month,year = date[0],date[1],date[2]
                    hours,minutes = time[0], time[2]
                    createEvent(title,day,month,year,hours,minutes)
                    speak("The event has been created.")
                    speak(title + ' on ' + day + ' ' + month + ' ' + year + ' at ' + hours + ' hours ' + minutes + ' minutes.')

                    


        elif wordExists(['maps','google maps'],query):
            query = query.replace('google maps','')
            query = query.replace('maps','')
            query = query.replace('google','')
            query = query.replace('search','')
            query = query.replace(' for ','')
            query = query.replace(' in ','')

            webbrowser.open('https://www.google.com/maps/place/' + query)

            speak("Opening google maps")

        elif wordExists(["message","whatsapp"],query):
            handleWhatsapp()

        elif wordExists(["call","voice call"],query):
            handleCall()
            
        elif wordExists(["email","mail","gmail"],query):
            handleEmail()

        elif "youtube" in query:
            from youtube_search import YoutubeSearch
            query = query.replace('search','')
            query = query.replace('play','')
            query = query.replace('on youtube','')
            query = query.replace('youtube','')

            results = YoutubeSearch(query,max_results=1).to_dict()
            print(results)
            webbrowser.open('https://youtube.com/watch?v=' + results[0]['id'])

            speak("Opening youtube")

        elif "google" in query:
            query = query.replace('search in google','')
            query = query.replace('search','')
            query = query.replace('google','')
            
            query = urllib.parse.quote_plus(query)

            url = 'https://www.google.com/search?q=' + query
            
            webbrowser.open(url)
            
            speak("Searching in google")
        

        elif "wikipedia" in query:
            import wikipedia
            query = query.replace('search in wikipedia','')
            query = query.replace('wikipedia','')
            query = query.replace('search','')
            query = query.replace('find','')
            result = wikipedia.summary(query,sentences=2)
            print(result)
            speak(result)
        
        elif wordExists(["how","what","when","where","why","who","which","tell"],query):
            urlquery = urllib.parse.quote_plus(query)

            url = "http://api.wolframalpha.com/v1/result?"
            url += 'appid=' + APP_ID
            url += '&i=' + urlquery

            res = requests.get(url)
            if "Wolfram|Alpha" in res.text:
                speak("Here's what I found")
                webbrowser.open('https://www.google.com/search?q=' + query)
            else:
                speak(res.text)


        elif wordExists(['solve','math','problem','equation'],query):
            query = query.replace('solve','')
            query = query.replace('math','')
            query = query.replace('equation','')
            query = query.replace('this','')
            query = query.replace('the','')

            query = urllib.parse.quote_plus(query)

            url = "http://api.wolframalpha.com/v1/result?"
            url += 'appid=' + APP_ID
            url += '&i=' + query
            
            res = requests.get(url)
            resText = res.text
            resText = resText[1:-1]

            resText = resText.replace('->','=')

            print(resText)
            speak(resText)

        elif wordExists(["news","latest"],query):
            url = 'https://www.indianexpress.com/latest-news'
            result = requests.get(url)

            src = result.content

            soup = BeautifulSoup(src,'html.parser')

            headlineLinks = []
            headlines = []
            print(soup)

            divs = soup.find_all('div',{'class' : 'title'})
            
            count = 0

            for div in divs:
                count += 1
                if(count > 5):
                    break
                a_tag = div.find('a')
                headlineLinks.append(a_tag.attrs['href'])
                headlines.append(a_tag.text)

            for head in headlines:
                speak(head)

        elif wordExists(["thank you","thanks"],query):
            speak("No worries. I am here to help")

        elif wordExists(['exit','goodbye','shutdown','stop'],query):
            speak("Goodbye. Have a nice day.")
            global status_label
            status_label['text'] = 'No longer listening...'
            break
        elif len(query)==0:
            speak(loop[random.randint(0,2)])
        else:
            webbrowser.open('https://www.google.com/search?q=' + query)
            speak("Here's what I found")


window = None
th = None
# GUI
if __name__ == "__main__":
    window = Tk()
    window.title('Bruno')
    window.geometry('400x600')
    window.configure(bg=WINDOW_BG)
    window.resizable(False,False)

    chat_frame = Frame(window,width=400,height=500, bg=WINDOW_BG)
    chat_frame.pack_propagate(False)
    chat_frame.pack()

    # scroll = Scrollbar(chat_frame,orient='vertical')
    # scroll.pack(side=RIGHT,fill=Y)  

    status_label = Label(width=400,height=100,text="Listening...",bg=CURRENT_STATUS_LABEL_BG,font=('Montserrat',20))
    status_label.pack()

    # user_chat = Label(chat_frame, text="Lorem ipsum", bg=USER_CHAT_BG,fg=TEXT_COLOR, justify=RIGHT,wraplength=250,font=('Montserrat',12,'bold'))
    # user_chat.pack(anchor='e',ipadx=2,ipady=2,pady=10,padx=10)

    # bot_chat = Label(chat_frame,text="Lorem ipsum 2.0", bg=BOT_CHAT_BG, fg=TEXT_COLOR,justify=LEFT, wraplength=250,font=('Montserrat',12,'bold'))
    # bot_chat.pack(anchor='w',ipadx=2,ipady=2,pady=10,padx=10)
    

    th = Thread(target=interpretCommand)
    th.start()

    window.mainloop()
    






    






