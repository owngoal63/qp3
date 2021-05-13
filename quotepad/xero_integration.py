import json
import requests
import webbrowser
import base64

from django.conf import settings
from pathlib import Path

client_id = settings.YH_XERO_CLIENT_ID
client_secret = settings.YH_XERO_CLIENT_SECRET
redirect_url = settings.YH_XERO_REDIRECT_URL
scope = settings.YH_XERO_SCOPE
b64_id_secret = base64.b64encode(bytes(client_id + ':' + client_secret, 'utf-8')).decode('utf-8')

def XeroFirstAuthStep1():
    # 1. Send a user to authorize your app
    auth_url = ('''https://login.xero.com/identity/connect/authorize?''' +
                '''response_type=code''' +
                '''&client_id=''' + client_id +
                '''&redirect_uri=''' + redirect_url +
                '''&scope=''' + scope +
                '''&state=123''')
    #webbrowser.open_new(auth_url)
    #print(auth_url)
    return auth_url
    #print(stop)

def XeroFirstAuthStep1x():      # Not used curently
    
    # 2. Users are redirected back to you with a code
    auth_res_url = input('What is the response URL? ')
    start_number = auth_res_url.find('code=') + len('code=')
    end_number = auth_res_url.find('&scope')
    auth_code = auth_res_url[start_number:end_number]
    print(auth_code)
    print('\n')
    return(auth_code)


def XeroFirstAuthStep2(auth_code):
    # 3. Exchange the code
    #print("bd64",b64_id_secret)
    #print("authcode", auth_code)
    exchange_code_url = 'https://identity.xero.com/connect/token'
    response = requests.post(exchange_code_url, 
                            headers = {
                                'Authorization': 'Basic ' + b64_id_secret
                            },
                            data = {
                                'grant_type': 'authorization_code',
                                'code': auth_code,
                                'redirect_uri': redirect_url
                            })
    #print(response)
    json_response = response.json()
    #print(json_response)
    #print('\n')
    return(json_response)

def XeroRefreshToken(refresh_token):
    token_refresh_url = 'https://identity.xero.com/connect/token'
    response = requests.post(token_refresh_url,
                            headers = {
                                'Authorization' : 'Basic ' + b64_id_secret,
                                'Content-Type': 'application/x-www-form-urlencoded'
                            },
                            data = {
                                'grant_type' : 'refresh_token',
                                'refresh_token' : refresh_token
                            })
    json_response = response.json()
    #print(json_response)
    
    new_refresh_token = json_response['refresh_token']

    xero_token_filename = Path(settings.BASE_DIR + "/google_creds/user_yourheatx/xero_refresh_token.txt")
    with open(xero_token_filename, 'w') as out:
        out.write(new_refresh_token)
    return(json_response)



def XeroTenants(access_token):
    connections_url = 'https://api.xero.com/connections'
    response = requests.get(connections_url,
                           headers = {
                               'Authorization': 'Bearer ' + access_token,
                               'Content-Type': 'application/json'
                           })
    json_response = response.json()
    #print("tenant response", json_response)
    
    for tenants in json_response:
        json_dict = tenants
    return json_dict['tenantId']

def XeroCreateContact(access_token, xero_tenant, name):
    print("Function: XeroCreateContact")
    post_url = 'https://api.xero.com/api.xro/2.0/Contacts'

    json_object = json.dumps({'Name': name })

    response = requests.post(post_url,
                           headers = {
                              'Authorization': 'Bearer ' + access_token,
                               'Xero-tenant-id': xero_tenant,
                               'Accept': 'application/json',
                               'Content-Type': 'application/json'
                           },
                          data = 
                             json_object
                            )
    json_response = response.json()
    #print(json_response)
    return(json_response)

def XeroCreateInvoice(access_token, xero_tenant, contact_id, amount, due_date):
    print("Function: XeroCreateInvoice")
    post_url = 'https://api.xero.com/api.xro/2.0/Invoices'

    json_object = json.dumps({
                "Type": "ACCREC",
                "Contact": { 
                    "ContactID": contact_id
                },
                "DueDate":  due_date,
                "LineItems": [
                    {
                    "Description": "Services as agreed",
                    "Quantity": "1",
                    "UnitAmount": amount,
                    "AccountCode": "200"
                    }
                ],
                "Status": "AUTHORISED"
                }
                )
    response = requests.post(post_url,
                           headers = {
                              'Authorization': 'Bearer ' + access_token,
                               'Xero-tenant-id': xero_tenant,
                               'Accept': 'application/json',
                               'Content-Type': 'application/json'
                           },
                          data = 
                             json_object
                            )
    json_response = response.json()
    #print(json_response)
    
    return(json_response)
