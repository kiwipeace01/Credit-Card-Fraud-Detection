from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.utils import translation
from django.views.decorators.csrf import csrf_exempt
from django import forms
from pandas.core.frame import DataFrame
import pymongo
from django.conf import settings
from .forms import AdminForm, LoginForm, SignForm, CardForm, TransactionForm
import random
import string
from json import JSONEncoder
import datetime
import pandas as pd
import json
import math
import numpy as np
import pickle
from sklearn.ensemble import GradientBoostingClassifier

client = pymongo.MongoClient(settings.DB_NAME)
db = client['Bank']
users = db["Users"]

# Create your views here.
from django.http import HttpResponse

@csrf_exempt
def dashboard(request):
    user_data = users.find({'email':request.session['email']})
    return render(request, 'dashboard.html',{'user_data':user_data})


@csrf_exempt
def admin(request):
    if request.method=="POST":
        print("Time to calculate!")
        form = AdminForm(request.POST)
        print(form,"\n")
        details = users.find({'email':form.cleaned_data.get("email")},{'transactions' : 1} )

        df = pd.DataFrame()

        for record in details:
            for x in record["transactions"]:
                print(x)
                df = df.append(x, ignore_index = True)

        df['TX_DATETIME'] = pd.to_datetime(df['TX_DATETIME'], format="%Y-%m-%d %H:%M:%S")

        # print(df.shape)

        df.set_index('TX_DATETIME', drop=True, append=False, inplace=True, verify_integrity=False)

        df = df.sort_index()
        print(df.head(12))

        date_1 = pd.to_datetime("2021-12-07 00:00:00", format="%Y-%m-%d %H:%M:%S")
        date_7 = pd.to_datetime("2021-12-01 00:00:00", format="%Y-%m-%d %H:%M:%S")
        date_30 = pd.to_datetime("2021-11-07 00:00:00", format="%Y-%m-%d %H:%M:%S")

        #df['TX_DATETIME'] = df.index
        df.reset_index(level=0, inplace=True)
        df['TX_AMOUNT'] = df['TX_AMOUNT'].astype(float)
        # print(df.dtypes)

        avg_1 = df.loc[df["TX_DATETIME"] >= date_1,"TX_AMOUNT"].sum()/df.loc[df["TX_DATETIME"] >= date_1,"TX_AMOUNT"].count()
        avg_7 = df.loc[df["TX_DATETIME"] >= date_7,"TX_AMOUNT"].sum()/df.loc[df["TX_DATETIME"] >= date_7,"TX_AMOUNT"].count()
        avg_30 = df.loc[df["TX_DATETIME"] >= date_30,"TX_AMOUNT"].sum()/df.loc[df["TX_DATETIME"] >= date_30,"TX_AMOUNT"].count()

        c1 = df.loc[df["TX_DATETIME"] >= date_1,"TX_AMOUNT"].count()
        c7 = df.loc[df["TX_DATETIME"] >= date_7,"TX_AMOUNT"].count()
        c30 = df.loc[df["TX_DATETIME"] >= date_30,"TX_AMOUNT"].count()

        during_night = 0
        during_weekend = 0

        if(df.iloc[-1]["TX_TIME_SECONDS"] <=21600):
            during_night = 1
        else:
            during_night = 0
        
        if(df.iloc[-1]["TX_DATETIME"].dayofweek >= 5):
            during_weekend = 1
        else:
            during_weekend = 0

        if(math.isnan(avg_1)):
            avg_1=0
        if(math.isnan(avg_7)):
            avg_7=0
        if(math.isnan(avg_30)):
            avg_30=0

        risk1 = np.random.normal(-3.396507 * math.pow(10,-15), 1.000007)
        risk7 = np.random.normal(-3.317571 * math.pow(10,-16), 1.000007)
        risk30 = np.random.normal(-6.552107 * math.pow(10,-16), 1.000007)

        nbterminal1 = int(np.random.normal(1.163451 * math.pow(10,-15), 1.000007))
        nbterminal7 = int(np.random.normal(-8.777878 * math.pow(10,-16), 1.000007))
        nbterminal30 = int(np.random.normal(-6.280875 * math.pow(10,-17), 1.000007))
        
        # print("Risk", risk1, risk7, risk30)
        # print("Nb terminals", nbterminal1, nbterminal7, nbterminal30)

        # print("Averages:",avg_1,avg_7,avg_30)
        # print("Counts:", c1,c7,c30)
        
        with open(r'C:\Users\Ishika Naik\nasscom\home\model_pickle2','rb') as f:
            mp = pickle.load(f)
            print("Model Loaded Successfully!")

        test_df = pd.DataFrame([[df.iloc[-1]["TX_AMOUNT"], during_weekend,during_night, c1,avg_1,c7,avg_7,c30,avg_30,nbterminal1,risk1,nbterminal7,risk7,nbterminal30,risk30]], 
        columns=['TX_AMOUNT', 'TX_DURING_WEEKEND', 'TX_DURING_NIGHT',
       'CUSTOMER_ID_NB_TX_1DAY_WINDOW', 'CUSTOMER_ID_AVG_AMOUNT_1DAY_WINDOW',
       'CUSTOMER_ID_NB_TX_7DAY_WINDOW', 'CUSTOMER_ID_AVG_AMOUNT_7DAY_WINDOW',
       'CUSTOMER_ID_NB_TX_30DAY_WINDOW', 'CUSTOMER_ID_AVG_AMOUNT_30DAY_WINDOW',
       'TERMINAL_ID_NB_TX_1DAY_WINDOW', 'TERMINAL_ID_RISK_1DAY_WINDOW',
       'TERMINAL_ID_NB_TX_7DAY_WINDOW', 'TERMINAL_ID_RISK_7DAY_WINDOW',
       'TERMINAL_ID_NB_TX_30DAY_WINDOW', 'TERMINAL_ID_RISK_30DAY_WINDOW'])

        prediction = mp.predict(test_df)  

        print("Prediction is =>>>>>>>>>>>>>>",prediction)

        if(prediction==1):
            users.update_one({'email':form.cleaned_data.get("email")}, {'$set':
            {'status':"suspicious behaviour"}})
        else:
            users.update_one({'email':form.cleaned_data.get("email")}, {'$set':
            {'status':"normal behaviour"}})          

        all_users = users.find({})
        print(all_users)
        return render(request, 'vysh.html',{'all_users':all_users})
    else:
        all_users = users.find({})
        return render(request, 'vysh.html',{'all_users':all_users})
    

@csrf_exempt
def transaction(request):
    if request.method=="POST":
        form = TransactionForm(request.POST)
        # print(form)

        if form.is_valid():
            print("\n-------------Transaction Processed-----------\n")
            seconds = (str(form.cleaned_data.get("date"))[17:19].lstrip('0'))
            mins = (str(form.cleaned_data.get("date"))[14:16].lstrip('0'))
            hrs = (str(form.cleaned_data.get("date"))[11:13].lstrip('0'))

            if(seconds==""):
                seconds = 0

            if(mins==""):
                mins=0
            if(hrs==""):
                hrs=0
            mins = int(mins)
            hrs = int(hrs)
            print(seconds)
            print(mins)
            print(hrs)

            total_sec = seconds + mins*60 + hrs*60*60
            print(request.session['email'])
            users.update_one({'email':request.session['email']},
            { '$push': { 'transactions': 
            {"TX_DATETIME" : (str(form.cleaned_data.get("date"))[:10])+" "+(str(form.cleaned_data.get("date"))[11:19]), 
            "TX_TERMINAL_ID" : random.randint(1,5),
            "TX_AMOUNT": form.cleaned_data.get("amount"),
            "TX_TIME_SECONDS": total_sec,
            "TX_TIME_DAYS":""}} })
            print((form.cleaned_data.get("date")))
            return HttpResponseRedirect('http://127.0.0.1:8000/home/dashboard/')
    else:
        form = TransactionForm() 
    return render(request, 'checkout.html',{})

@csrf_exempt
def reg_card(request):
    if request.method=="POST":
        form = CardForm(request.POST)
        for field in form:
                print("Field Error:", field.name,  field.errors)
        if form.is_valid():
            cardnum = ''.join(random.choice(string.digits) for _ in range(16))
            cvv = ''.join(random.choice(string.digits) for _ in range(3))
            update_data = users.update_one({'email':request.session['email']}, {'$set':
            {'adr':"null",
            'card_no':cardnum,
            'cv':cvv,
            'exp_date': '12/26',
            'phone':form.cleaned_data.get("phone"),
            'aadhar':form.cleaned_data.get("aadhar"),
            'nationality':form.cleaned_data.get("nation"),
            'dob':form.cleaned_data.get("date")}})

            print(update_data)
            return HttpResponseRedirect('http://127.0.0.1:8000/home/dashboard/')
    else:
        form = CardForm() 

    return render(request, 'creditcard_regis.html',{})


@csrf_exempt
def login(request):
    if request.method=="POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            print(form.cleaned_data.get("your_name"))
            print(form.cleaned_data.get("your_pass"))
            if(form.cleaned_data.get("your_name")!="admin" and form.cleaned_data.get("your_pass")!="admin"):
                request.session['email'] = form.cleaned_data.get("your_name")
                details = users.find({'email':form.cleaned_data.get("your_name")})
                for r in details:
                    if(r["pwd"]==form.cleaned_data.get("your_pass")):
                        print("Login Successful!")
                        return HttpResponseRedirect('http://127.0.0.1:8000/home/dashboard/')
            else:
                request.session['email'] = form.cleaned_data.get("your_name")
                return HttpResponseRedirect('http://127.0.0.1:8000/home/admin/')
    else:
        form = LoginForm() 

    return render(request, 'sign-in.html',{})

@csrf_exempt
def register(request):
    if request.method=="POST":
        form = SignForm(request.POST)
        if form.is_valid():
            print(form.cleaned_data)
            if(form.cleaned_data.get("fpass") == form.cleaned_data.get("re_pass")):
                x = users.find({'email':form.cleaned_data.get("email")})
                if(len(list(x))==0):
                    print("OK")
                    request.session['email'] = form.cleaned_data.get("email")
                    print(form.cleaned_data.get("name"))
                    print(form.cleaned_data.get("email"))
                    print(form.cleaned_data.get("fpass"))

                    data = {
                        "name": form.cleaned_data.get("name"),
                        "status":"unknown",
                        "email" : form.cleaned_data.get("email"),
                        "pwd" : form.cleaned_data.get("fpass"),
                        "transactions":[],
                        "card_no" : "Click Register Card to update these details",
                        "exp_date" : "Click Register Card to update these details",
                        "cv":"Click Register Card to update these details",
                        "add":"Click Register Card to update these details",
                        "aadhar":"Click Register Card to update these details",
                        "phone":"Click Register Card to update these details",
                        "nationality":"Click Register Card to update these details",
                        "dob":""
                    }
                    print(data)
                    users.insert_many([data])
                    return HttpResponseRedirect('http://127.0.0.1:8000/home/login/')
                else:
                    form = SignForm() 
    else:
        print("NOT VALID")
        form = SignForm() 
    return render(request, 'index.html',{})