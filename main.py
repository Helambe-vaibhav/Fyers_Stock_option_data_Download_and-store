import datetime as dt
import time
import pandas as pd
import os
import warnings
from Fyers_functions import investing
warnings.filterwarnings("ignore")

next_coming_thursday = dt.date.today() + dt.timedelta(days=(3- dt.date.today().weekday()+7)%7)

def This_week():
    print(f"{dt.datetime.now()} Next Thursday: {next_coming_thursday} ")
    cur_path =f'datafiles/{next_coming_thursday}'
    if not os.path.exists(cur_path):
        os.mkdir(cur_path)
        os.mkdir(f'data/{next_coming_thursday}')
        fyers_fo = "https://public.fyers.in/sym_details/NSE_FO.csv"
        df_symbols = pd.read_csv(fyers_fo, index_col=False, header=None)
        df_symbols.drop([5,14,17],axis=1,inplace=True)
        df_symbols.columns=['Fytoken', 'Symbol Details', 'Exchange Instrument type', 'Minimum lot size', 'Tick size', 'ISIN', 'Last update date', 'Expiry date', 'Symbol ticker', 'Exchange', 'Segment', 'Scrip code', 'Underlying scrip code', 'Strike price', 'Option type']
        df_symbols = df_symbols[df_symbols['Underlying scrip code'] =='NIFTY' ]
        df_symbols.reset_index(drop=True, inplace=True)
        df_symbols['Expiry date'] = pd.to_datetime(df_symbols['Expiry date'],unit='s').dt.date
        expiry_list = sorted(df_symbols['Expiry date'].unique())
        next_expiry = expiry_list[0]
        print(f"{dt.datetime.now()} Expiry: {next_expiry} ")
        df_symbols = df_symbols[df_symbols['Expiry date']==next_expiry]
        # lot_size = df_symbols.loc[0,'Minimum lot size']
        df_symbols = df_symbols.sort_values(by=['Strike price'])
        df_symbols.reset_index(drop=True, inplace=True)
        df_symbols.set_index('Fytoken',inplace=True)
        with open(f'datafiles/{next_coming_thursday}/ExpirySymbols{next_coming_thursday}.csv','w') as f:
            df_symbols.to_csv(f)
This_week()
trading = investing()
main_df = pd.read_csv(f'datafiles/{next_coming_thursday}/ExpirySymbols{next_coming_thursday}.csv')
for i in range(0,len(main_df.index)):
    try:
        trading.download_data(symbol=str(main_df.loc[i,'Symbol ticker']))
        # time.sleep(1)
    except Exception as e:
        print(f"Error in {main_df.loc[i,'Symbol ticker']} : {e}")
        pass




