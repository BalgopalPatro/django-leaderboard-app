from __future__ import absolute_import, unicode_literals

import os
from django.shortcuts import render
from challenge_leaderboard.settings import BASE_DIR
#import for Scrapings

from bs4 import BeautifulSoup
from urllib.request import urlopen
import pandas as pd
import csv
import json
import datetime

# Create your views here.
from django.http import HttpResponse,HttpResponseNotFound  
from django.views.decorators.http import require_http_methods  
from django.template import loader

dataset=pd.read_csv('qwiklabs_url.csv')
urls=dataset['Qwiklabs Profile URL'].values
track1=[
    'Getting Started: Create and Manage Cloud Resources',
    'Perform Foundational Infrastructure Tasks in Google Cloud',
    'Set up and Configure a Cloud Environment in Google Cloud',
    'Deploy and Manage Cloud Environments with Google Cloud',
    'Build and Secure Networks in Google Cloud',
    'Deploy to Kubernetes in Google Cloud'
    ]
track2 = [
    'Getting Started: Create and Manage Cloud Resources',
    'Perform Foundational Data, ML, and AI Tasks in Google Cloud',
    'Insights from Data with BigQuery',
    'Engineer Data in Google Cloud',
    'Integrate with Machine Learning APIs',
    'Explore Machine Learning Models with Explainable AI'
    ]



last_update_time = datetime.datetime.now()

#task scheduling
from celery import shared_task
import time

@shared_task
def updateList():
    allProfiles = []
    for i in range(len(urls)):
        url = urls[i]
        profile = {}
        page = urlopen(url)
        html=page.read().decode("utf-8")
        soup = BeautifulSoup(html, "html.parser")
        name=soup.title.string
        n=name.split('|')
        profile['name'] = n[0]
        profilezz = soup.findAll('div', attrs = {'class':'public-profile__hero'})[0]
        dp = profilezz.img['src']
        profile['pic'] = dp
        contentTable  = soup.find('p', { "class" : "public-profile__hero__details l-mbm"})
        x=contentTable.get_text()
        res = [int(i) for i in x.split() if i.isdigit()]
        x=x.replace(" . ","\n")
        profile['labs'] = res[0]
        profile['quests'] = res[1]
        badge  = soup.findAll('ql-badge')
        t1 = []
        t2 = []
        bg = []
        for b in badge:
            l = json.loads(str(b['badge']))
            sb = l['title']
            if sb in track1:
                t1.append(sb)
            if sb in track2:
                t2.append(sb)
        profile['track1'] = len(t1)
        profile['track2'] = len(t2)
        profile['total'] = len(t1) + len(t2)
        allProfiles.append(profile)
    allProfiles.sort(key=lambda x: x['total'], reverse=True)
    allProfiles.append({'time' : str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))})
    # PUBLIC_DIR =  os.path.join(BASE_DIR, 'webapp')
    print(allProfiles)
    last_update_time = datetime.datetime.now()
    with open("my.json" ,"w") as f:
        json.dump(allProfiles,f)


# updateList()
# print(allProfiles)

# @periodic_task(run_every=crontab(minute='*/1'))


def Hello():
    last_update_time = datetime.datetime.now()
    print("Hello World",last_update_time)

def index(request):
    template = loader.get_template('index.html')
    print(BASE_DIR)
    with open('my.json') as f:
        allData = json.load(f)
    # print(allData)
    data = {
       'data' : allData[:-1],
       'time' : allData[-1]['time']
    }
    return HttpResponse(template.render(data))
