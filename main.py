# SYSTEM LIBRARY IMPORTS
import json
import os
import speech_recognition as sr
import pyttsx3
from tkinter import *
from threading import Thread
import webbrowser
import yagmail
from bs4 import BeautifulSoup
import requests
import urllib.parse
import sys

# GLOBALS

ASSISTANT_NAME = 'Bruno'.lower()

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

def speak(text):
    bot_chat = Label(chat_frame,text=text, bg=BOT_CHAT_BG, fg=TEXT_COLOR,justify=LEFT, wraplength=250,font=('Montserrat',12,'bold'))
    bot_chat.pack(anchor='w',ipadx=2,ipady=2,pady=10,padx=10)    
    engine.say(text)
    engine.runAndWait()


# SETTING UP SPEECH TO TEXT
def takeCommand(first):
    global status_label,chat_frame
    r = sr.Recognizer()
    # r.pause_threshold = 1

    with sr.Microphone() as source:
        print("Listening...")
        status_label['text'] = "Listening..."
        audio = r.listen(source)

        try:
            print("Processing...")
            status_label['text'] = "Processing..."
            query = r.recognize_google(audio,language='en-in')
            # print(query)
        except Exception as e:
            print(e)
    
    if first:
        for widget in chat_frame.winfo_children():
            widget.destroy()

    user_chat = Label(chat_frame, text=query, bg=USER_CHAT_BG,fg=TEXT_COLOR, justify=RIGHT,wraplength=250,font=('Montserrat',12,'bold'))
    user_chat.pack(anchor='e',ipadx=2,ipady=2,pady=10,padx=10)  
    return query.lower()
#######################################################################################

###############################  WHATSAPP ####################################

contactsFile = open('./userData/contacts.json','r')
contacts = json.load(contactsFile)
contactsFile.close()

popup_window = None
name = None
number = None

newContactName = None

def handleWhatsapp():
    global contacts,newContactName
    speak("Sure. Who do you want to send the message to?")
    person = takeCommand(False)
    
    print(contacts)
    if person in contacts:
        sendMessage(person)
    else:
        speak("I dont have the contact. Please fill the details so I can message the contact directly next time.")
        WA_Popup()
        sendMessage(newContactName)

def WA_Popup():
    global popup_window,name,number
    popup_window = Tk()
    popup_window.title('Whatsapp service')
    popup_window.iconbitmap('./static/images/whatsapp.ico')

    popup_window.configure(bg='white',width=300,height=220)
    popup_window.pack_propagate(False)


    Label(popup_window,text='Name',font=('Montserrat',12),bg='white').pack(padx=5,pady=5)
    name = Entry(popup_window,font=('Montserrat',12),relief=FLAT,bd=5,bg='#DCDCDC')
    name.pack(padx=5,pady=5)

    Label(popup_window,text='Number(with Country Code)',font=('Montserrat',12),bg='white').pack(padx=5,pady=5)
    number = Entry(popup_window,font=('Montserrat',12),relief=FLAT,bd=5,bg='#DCDCDC')
    number.pack(padx=5,pady=5)

    Button(popup_window,text='Send',bg='#14A769',font=('Montserrat',12),relief=FLAT,fg='white',command=storeContact).pack(padx=20,pady=10)
    popup_window.mainloop()


def storeContact():
    global popup_window,name,number,newContactName
    # print(name.get())
    # print(number.get())
    contacts[name.get()] = number.get()
    newContactName = name.get()
    with open('./userData/contacts.json','w') as f:
        json.dump(contacts,f)

    popup_window.destroy()

def sendMessage(person):
    phoneNo = contacts[person]
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

emailFile = open('./userData/emails.json','r')
emails = json.load(emailFile)
emailFile.close()

email_window = None
emailName = None
email = None
newEmailName = None
def handleEmail():
    global emails,newEmailName

    speak("Sure. Who do you want to send the mail to?")
    person = takeCommand(False)

    if person in emails:
        sendEmail(person)
    else:
        speak("I dont have the email. Please fill the details so that I can email directly the next time")
        Email_Popup()
        sendEmail(newEmailName)

def Email_Popup():
    global email_window,email,emailName

    email_window = Tk()
    email_window.title('Email service')
    email_window.iconbitmap('./static/images/email.ico')

    email_window.configure(bg='white',width=300,height=220)
    email_window.pack_propagate(False)


    Label(email_window,text='Name',font=('Montserrat',12),bg='white').pack(padx=5,pady=5)
    emailName = Entry(email_window,font=('Montserrat',12),relief=FLAT,bd=5,bg='#DCDCDC')
    emailName.pack(padx=5,pady=5)

    Label(email_window,text='Email',font=('Montserrat',12),bg='white').pack(padx=5,pady=5)
    email = Entry(email_window,font=('Montserrat',12),relief=FLAT,bd=5,bg='#DCDCDC')
    email.pack(padx=5,pady=5)

    Button(email_window,text='Send',bg='#14A769',font=('Montserrat',12),relief=FLAT,fg='white',command=storeEmail).pack(padx=20,pady=10)
    email_window.mainloop()

def storeEmail():
    global email_window, emailName,email,newEmailName,emails

    emails[emailName.get()] = email.get()
    newEmailName = emailName.get()
    with open('./userData/emails.json','w') as f:
        json.dump(emails,f)

    email_window.destroy()


def sendEmail(person):
    from userData.config import GMAIL_USERNAME, GMAIL_PASSWORD
    recipient = emails[person]

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

#################################################################################################


def interpretCommand():

    while True:
        query = takeCommand(True).lower()

        if "weather" in query:
            from userData.config import APP_ID
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

        if "whatsapp" in query:
            handleWhatsapp()
        
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
        
        elif wordExists(["how","what","when","where","why"],query):
            from userData.config import APP_ID

            query = urllib.parse.quote_plus(query)

            url = "http://api.wolframalpha.com/v1/result?"
            url += 'appid=' + APP_ID
            url += '&i=' + query

            res = requests.get(url)
            print(res.text)
            speak(res.text)

        elif wordExists(['solve','math','problem','equation'],query):
            from userData.config import APP_ID

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
            url = 'https://indianexpress.com/latest-news/'
            result = requests.get(url)

            src = result.content

            soup = BeautifulSoup(src,'html.parser')

            headlineLinks = []
            headlines = []

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

        elif wordExists(['exit','goodbye','shutdown'],query):
            global window
            speak("Goodbye. Have a nice day.")
            window.destroy()
            return
            
            

        

            




        

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

    scroll = Scrollbar(chat_frame,orient='vertical')
    scroll.pack(side=RIGHT,fill=Y)  

    status_label = Label(width=400,height=100,text="Listening...",bg=CURRENT_STATUS_LABEL_BG,font=('Montserrat',20))
    status_label.pack()

    # user_chat = Label(chat_frame, text="Lorem ipsum", bg=USER_CHAT_BG,fg=TEXT_COLOR, justify=RIGHT,wraplength=250,font=('Montserrat',12,'bold'))
    # user_chat.pack(anchor='e',ipadx=2,ipady=2,pady=10,padx=10)

    # bot_chat = Label(chat_frame,text="Lorem ipsum 2.0", bg=BOT_CHAT_BG, fg=TEXT_COLOR,justify=LEFT, wraplength=250,font=('Montserrat',12,'bold'))
    # bot_chat.pack(anchor='w',ipadx=2,ipady=2,pady=10,padx=10)

    th = Thread(target=interpretCommand)
    th.start()

    window.mainloop()





