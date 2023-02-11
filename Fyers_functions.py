import time

# from functionsList import *
from fyers_api import fyersModel
from fyers_api import accessToken
import warnings
import datetime as dt
import pandas as pd
import os
import numpy as np
warnings.filterwarnings("ignore")


class investing():
    def __init__(self):
        self.client_id='Enter your client id'
        self.base_access_token = self.get_access_token()
        self.fyers = fyersModel.FyersModel(client_id=self.client_id, token=self.base_access_token ,log_path='logfiles')
        self.download_data(symbol='NSE:NIFTY50-INDEX',Nifty50=True)

    def get_access_token(self):
        # Variables
        secret_key ='Enter your secret key'
        redirect_uri = 'Enter your redirect uri'
        response_type = 'code'

        today_date = str(dt.datetime.now().date())
        if not os.path.exists(f'accessToken/access_token{today_date}.txt'):
            for file in os.listdir('accessToken'):
                os.remove(f'accessToken/{file}')
            session= accessToken.SessionModel(client_id=self.client_id,secret_key=secret_key,redirect_uri=redirect_uri, response_type=response_type, grant_type='authorization_code')
            response = session.generate_authcode()
            print('Login Url:',response)
            # send_message('Login Url:'+response)
            auth_url = input('Enter the URL: ')
            auth_code = auth_url.split('auth_code=')[1].split('&state')[0]
            session.set_token(auth_code)
            access_token = session.generate_token()['access_token']
            with open(f'accessToken/access_token{today_date}.txt', 'w') as f:
                f.write(access_token)
        else:
            with open(f'accessToken/access_token{today_date}.txt', 'r') as f:
                access_token = f.read()
        return access_token

    def download_data(self,symbol,Nifty50=False):
        next_coming_thursday = dt.date.today() + dt.timedelta(days=(3- dt.date.today().weekday()+7)%7)
        till_today = str(dt.datetime.today().date())
        from_date = str(dt.datetime.today().date()- dt.timedelta(days=40))
        data  = {"symbol":symbol,"resolution":"3","date_format":"1","range_from":from_date,"range_to":till_today}
        df= pd.DataFrame(self.fyers.history(data)['candles'],columns=['Datetime','Open','High','Low','Close','Volume'])
        if df.shape[0]==0:
            print('No Data')
            return
        df['Datetime'] = pd.to_datetime(df['Datetime'],unit='s').dt.tz_localize('UTC').dt.tz_convert('Asia/Kolkata')
        if Nifty50:
            self.date_range = df['Datetime']
        if not Nifty50:
            df['Datetime'] = self.date_range
            df.fillna(method='ffill',inplace=True)

        df['Date'] = df['Datetime'].dt.date
        df['Time'] = df['Datetime'].dt.time
        df.drop('Datetime',axis=1,inplace=True)
        # rearrange columns
        df = df[['Date','Time','Open','High','Low','Close','Volume']]
        save_path = f'./data/{next_coming_thursday}/{symbol[4:]}.csv'
        df.to_csv(save_path,index=False)
        print('Data Downloaded for',symbol[4:])