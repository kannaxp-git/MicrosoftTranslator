# -*- coding: utf-8 -*-

#Author: kach@microsoft.com

# This simple app uses the '/translate' resource to translate text from
# one language to another.

# This sample runs on Python 2.7.x and Python 3.x.
# You may need to install requests and uuid.
# Run: pip install requests uuid

#Setting environment variable (powershell command): setx COGNITIVE_SERVICE_KEY "your-key"


import os, requests, uuid, json
import pandas as pd
from datetime import datetime

key_var_name = 'TRANSLATOR_TEXT_SUBSCRIPTION_KEY'
if not key_var_name in os.environ:
    raise Exception('Please set/export the environment variable: {}'.format(key_var_name))
subscription_key = os.environ[key_var_name]
#subscription_key ="XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"

endpoint_var_name = 'TRANSLATOR_TEXT_ENDPOINT'
if not endpoint_var_name in os.environ:
    raise Exception('Please set/export the environment variable: {}'.format(endpoint_var_name))
endpoint = os.environ[endpoint_var_name]
#endpoint = "https://api.cognitive.microsofttranslator.com/"

# If you encounter any issues with the base_url or path, make sure
# that you are using the latest endpoint: https://docs.microsoft.com/azure/cognitive-services/translator/reference/v3-0-translate
path = '/translate?api-version=3.0'
params = '&to=en'
#params = '&to=de&to=it'
constructed_url = endpoint + path + params

headers = {
    'Ocp-Apim-Subscription-Key': subscription_key,
    'Ocp-Apim-Subscription-Region': 'centralindia',
    'Content-type': 'application/json',
    'X-ClientTraceId': str(uuid.uuid4())
}

# # You can pass more than one object in body.
# body = [{
#     'text' : '株式会社 シバタ'
# }]
# request = requests.post(constructed_url, headers=headers, json=body)
# response = request.json()

# print(body)
# print(json.dumps(response, sort_keys=True, indent=4, separators=(',', ': ')))

#############################################################################
### Iterate through company names ###########################################
#############################################################################
df=pd.read_excel('./data/Unicode_Fullset.xlsx')
df['lang']=''
df['score']=0

df['addr_lang']=''
df['addr_score']=0

df['t_OrgName']=''
df['t_Address']=''

IsSeparateCall=False

for idx,row in df.iterrows():
    if idx%1000==0:
        #break
        print(datetime.now(),idx)
        df.to_excel('./data/SS_Translated.xlsx')
        
    if row['lang']=='' or pd.isnull(row['lang']): #excluding previously executed records. incase of error & re-run
        try:
            if IsSeparateCall:
                org = [{'text' : str(row['OrgName'])}]
                request = requests.post(constructed_url, headers=headers, json=org)
                response = request.json()
                
                addr = [{'text' : str(row['Address'])}]
                request1 = requests.post(constructed_url, headers=headers, json=addr)
                response1 = request1.json()
                
                df.loc[idx,'lang']=response[0]['detectedLanguage']['language']
                df.loc[idx,'score']=response[0]['detectedLanguage']['score']
                df.loc[idx,'t_OrgName']=response[0]['translations'][0]['text']
                
                df.loc[idx,'addr_lang']=response1[0]['detectedLanguage']['language']
                df.loc[idx,'addr_score']=response1[0]['detectedLanguage']['score']
                df.loc[idx,'t_Address']=response1[0]['translations'][0]['text']
            else:
                org_addr = [{'text' : str(row['OrgName'])+'\n\n'+str(row['Address'])}]
                request = requests.post(constructed_url, headers=headers, json=org_addr)
                response = request.json()
                
                df.loc[idx,'lang']=response[0]['detectedLanguage']['language']
                df.loc[idx,'score']=response[0]['detectedLanguage']['score']
                
                t_text=response[0]['translations'][0]['text']
                t_text=t_text.split('\n\n')
                df.loc[idx,'t_OrgName']=t_text[0]
                df.loc[idx,'t_Address']=t_text[1]
                
        except:
            pass
    
df.to_excel('./data/SS_Translated.xlsx')


