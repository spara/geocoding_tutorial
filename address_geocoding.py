import urllib.parse
import requests
import json
import sys
from pprint import pprint
from os.path import isfile, expandvars
from here_oauth import here_oauth

# get credentials
def get_credentials():
    path = ''
    operating_system = sys.platform
    if (operating_system == "darwin") or (operating_system == "linux"):
        if isfile(expandvars("$HOME/.here/credentials.properties")) == True:
            path = expandvars("$HOME/.here/credentials.properties")
        else:
            print("The credentials.properties file cannot be found. Please see documentation to set up credentials https://developer.here.com/documentation/sdk-python-v2/dev_guide/topics/credentials.html")
            sys.exit()
    
    if (operating_system == "win32") or (operating_system == "cygwin"):
        if isfile("%USERPROFILE%\.here\credentials.properties") == True:
            path = expandvars("%USERPROFILE%\.here\credentials.properties")
        else:
            print("The credentials.properties file cannot be found. Please see  https://developer.here.com/documentation/sdk-python-v2/dev_guide/topics/credentials.html to set up credentials.")
            sys.exit()

    return path

#get oauth token 
def get_oauth(credentials):
    data = json.loads(here_oauth.get_token(credentials))
    token_type = data["token_type"]
    access_token = data["access_token"]
    oauth = {"token_type": token_type, "access_token": access_token}

    return oauth

# parameters
base_url = "https://geocode.search.hereapi.com"
version = "v1"
geocode_service_endpoint = "geocode"

# get oauth token for API
credentials = get_credentials()
token = get_oauth(credentials)

# add token to headers
headers = {"Authorization": token["token_type"]+" "+token["access_token"]}

# Geocode a street address
address = urllib.parse.quote_plus("4 The Limes, Amersham, HP6 5, United Kingdom").replace(",","")
url = (base_url+"/"+version+"/"+geocode_service_endpoint+"?q="+address)
geocode = json.loads(requests.get(url, headers=headers).text)
print("Address geocoding")
pprint(geocode)
print("\n\n")

# Geocode a street address with the incorrect street name
address = urllib.parse.quote_plus("1 Telephone Hill, San Francisco, CA 94133").replace(",","")
url = (base_url+"/"+version+"/"+geocode_service_endpoint+"?q="+address)
headers = {"Authorization": token["token_type"]+" "+token["access_token"]}
geocode = json.loads(requests.get(url, headers=headers).text)
print("Address geocoding with  incorrect street name")
pprint(geocode)
print("\n\n")

# # Geocode a street address with house number fall back
# address = urllib.parse.quote_plus("1622 Ebbotts Place, Crofton, MD")
# url = (base_url+"/"+version+"/"+geocode_service_endpoint+"?q="+address)
# print(url)
# headers = {"Authorization": token["token_type"]+" "+token["access_token"]}
# geocode_3 = json.loads(requests.get(url, headers=headers).text)

# Geocoding by house number and postal code

# qualified query
house_number = "houseNumber=1"
postal_code = "postalCode=94133-3106"
country="country=USA"
url = (base_url+"/"+version+"/"+geocode_service_endpoint+"?qq="+house_number+";"+postal_code)
geocode_qualified = json.loads(requests.get(url, headers=headers).text)
print("Qualified geocode by house numner and postal code")
pprint(geocode_qualified)
print("\n\n")
# free form query
address = " 1 94133-3106"
url = (base_url+"/"+version+"/"+geocode_service_endpoint+"?q="+address)
geocode_freeform = json.loads(requests.get(url, headers=headers).text)
print("Free form geocode by house numner and postal code")
pprint(geocode_freeform)
print("\n\n")

# Address lookup by postal code in Ireland and Singapore

# Address lookup by Ireland postal code
# Free form query
address = "BT57 8SU"
url = (base_url+"/"+version+"/"+geocode_service_endpoint+"?q="+address)
geocode = json.loads(requests.get(url, headers=headers).text)
print("Address gecoding by Eircode with a free form query:\n\n")
pprint(geocode)
print("\n\n")
# Qualified query
address = "postalCode=BT57 8SU"
url = (base_url+"/"+version+"/"+geocode_service_endpoint+"?qq="+address)
geocode = json.loads(requests.get(url, headers=headers).text)
print("Address gecoding by Eircode with a qualified query:\n\n")
pprint(geocode)
print("\n\n")

# Address lookup by postal code in Singapore
address = "179024"
url = (base_url+"/"+version+"/"+geocode_service_endpoint+"?q="+address+"&in=countryCode:SGP")
geocode = json.loads(requests.get(url, headers=headers).text)
print("Address geocoding for Singapore with a free form query:\n\n")
pprint(geocode)
print("\n\n")

# Area geocoding for a city
address = urllib.parse.quote_plus("San Francisco")
url = (base_url+"/"+version+"/"+geocode_service_endpoint+"?q="+address)
geocode = json.loads(requests.get(url, headers=headers).text)
print("Address gecoding by area with a free form query:")
pprint(geocode)
print("\n\n")

# Area geocoding for an administrative area
address = urllib.parse.quote_plus("county=San Francisco County;state=CA;country=USA")
url = (base_url+"/"+version+"/"+geocode_service_endpoint+"?qq="+address)
geocode = json.loads(requests.get(url, headers=headers).text)
print("Address gecoding for an administrative area:\n\n")
pprint(geocode)
print("\n\n")

address = urllib.parse.quote_plus("county=San Francisco County;state=CA;country=USA")
url = (base_url+"/"+version+"/"+geocode_service_endpoint+"?qq="+address)
geocode = json.loads(requests.get(url, headers=headers).text)
print("Address gecoding by cpounty:\n\n")
pprint(geocode)
print("\n\n")

# Place geocoding
address = urllib.parse.quote_plus("Coit Tower San Francisco")
url = (base_url+"/"+version+"/"+geocode_service_endpoint+"?q="+address)
headers = {"Authorization": token["token_type"]+" "+token["access_token"]}
geocode = json.loads(requests.get(url, headers=headers).text)
print("Address geocoding for a place with a qualified query:\n\n")
pprint(geocode)
