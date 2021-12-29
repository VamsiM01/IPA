from __future__ import print_function

import datetime
import os.path
import dateutil.parser
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/calendar']


def getEvents():
    """
    Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    eventList = []
    try:
        service = build('calendar', 'v3', credentials=creds)

        now = datetime.datetime.utcnow().isoformat() + 'Z'
        print('Getting the upcoming 5 events')
        events_result = service.events().list(calendarId='primary', timeMin=now, maxResults=5, singleEvents=True,
                                                orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            print('No upcoming events found.')
            return

        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            # print(start, event['summary'])

            sentence = event['summary'] + ' on '

            d = dateutil.parser.parse(start)
            print(type(d))
            day = d.day
            month = d.strftime("%B")
            year = d.year
            hour = d.hour
            minute = d.minute

            readableDate = str(day) + ' ' + str(month) + ' ' + str(year) + ' at ' + str(hour) + ' hours ' + str(minute) + ' minutes.'

            sentence += readableDate
            eventList.append(sentence)

    except HttpError as error:
        print('An error occurred: %s' % error)

    return eventList


def createEvent(title,day,monthName,year,hours,minutes):
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    monthDict = {
        "jan" : 1, "january" : 1, "feb" : 2, "february" : 2,"march" : 3,"april" : 4,"may" : 5,"june" : 6,"july" : 7,"august" : 8,"september" : 9,"october" : 10, "november" : 11, "december": 12 
    }
    finalDay = ""
    
    for char in day:
        if char >= '0' and char <= '9':
            finalDay += char
    finalDay = int(finalDay)
    finalMonth = monthDict[monthName]
    finalYear = int(year)

    hours = int(hours)
    minutes = int(minutes)
    try:
        service = build('calendar','v3',credentials=creds)

        start_time = datetime.datetime(year=finalYear,month=finalMonth,day=finalDay,hour=hours,minute=minutes)
        end_time = start_time + datetime.timedelta(hours=1)
        timezone = 'Asia/Kolkata'

        event = {
            'summary' : title,
            'start' : {
                'dateTime' : start_time.strftime("%Y-%m-%dT%H:%M:%S"),
                'timeZone' : timezone,
            },
            'end' : {
                'dateTime' : end_time.strftime("%Y-%m-%dT%H:%M:%S"),
                'timeZone' : timezone,
            }
        }
        service.events().insert(calendarId='primary',body=event).execute()

    except HttpError as error:
        print('Error occurred:',error)


def listHolidays():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('calendar','v3',credentials=creds)
        now = datetime.datetime.utcnow().isoformat() + 'Z'
        events_result = service.events().list(calendarId='en.indian#holiday@group.v.calendar.google.com',timeMin=now,maxResults=5,singleEvents=True,orderBy='startTime').execute()

        # j = json.dumps(events_result,indent=4)
        # print(j)

        events = events_result.get('items',[])

        if not events:
            print("No upcoming holidays.")
            return

        monthMapping = {1 : 'January',2 : 'February',3:'March',4:'April',5:'May',6:'June',7:'July',8:'August',9:'September',10:'October',11:'November',12:'December'}

        holidayList = []

        for holiday in events:
            res = ""

            res += holiday.get('summary')
            start = holiday.get('start').get('date')
            year = start[0:4]
            # print(year)
            month = int(start[5:7])
            day = int(start[8:])
            # print(month)
            # print(day)

            res += ' on '
            res += str(day) + ' ' + monthMapping.get(month) + ' ' + year

            # print(res)
            holidayList.append(res)

    except HttpError as error:
        print("Error : " + error)

    return holidayList
