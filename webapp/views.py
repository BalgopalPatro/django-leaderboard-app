from django.shortcuts import render

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

dataset=pd.read_csv('qq_urls.csv')
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

allProfiles = []

last_update_time = datetime.datetime.now()

def updateList():
    for i in range(len(urls)):
        url = urls[i]
        profile = {}
        page = urlopen(url)
        html=page.read().decode("utf-8")
        soup = BeautifulSoup(html, "html.parser")
        name=soup.title.string
        n=name.split('|')
        # print(n[0])
        profile['name'] = n[0]
        profilezz = soup.findAll('div', attrs = {'class':'public-profile__hero'})[0]
        dp = profilezz.img['src']
        profile['pic'] = dp
        contentTable  = soup.find('p', { "class" : "public-profile__hero__details l-mbm"})
        x=contentTable.get_text()
        res = [int(i) for i in x.split() if i.isdigit()]
        x=x.replace(" . ","\n")
        # print(res)
        profile['labs'] = res[0]
        profile['quests'] = res[1]
        badge  = soup.findAll('div', { "class" : "public-profile__badge"})
        t1 = []
        t2 = []
        bg = []
        for b in badge:
            sb = b.findAll('div')[1].get_text().replace('\n',"")
            bg.append(b.findAll('div')[1].get_text().replace('\n',""))
            if sb in track1:
                t1.append(sb)
            if sb in track2:
                t2.append(sb)
        profile['track1'] = len(t1)
        profile['track2'] = len(t2)
        profile['total'] = len(t1) + len(t2)
        allProfiles.append(profile)
    allProfiles.sort(key=lambda x: x['total'], reverse=True)
    last_update_time = datetime.datetime.now()

updateList()
print(allProfiles)

with open("my.json","w") as f:
    json.dump(allProfiles,f)

def index(request):  
   template = loader.get_template('index.html')
   data = {
       'data' : allProfiles,
       'time' : last_update_time
   }
   return HttpResponse(template.render(data))