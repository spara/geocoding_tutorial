# Geocoding with HERE

Geocoding takes a text description and converts it to map coordinates. For example, geocoding **1 Telegraph Hill Blvd, San Francisco, CA 94133** returns latitude: 37.80266, longitude: -122.40594. In addition to complete addresses, geocoding can resolve places, areas, and partial addresses. This tutorial demonstrates the different uses of HERE platform geocoding service.

## Pre-requisites

This tutorial requires a HERE plaform account, HERE credentials properly set up, and Python 3.6 or greater. We recommend using a virtual environment with the `requests` and `here_oauth` packages installed.

```bash
$ python3 -m venv venv
$ source venv/bin/activate
$ pip -r requirements.txt
```

### Authenticating to the Geocoding API

Sending a request to the geocpder API requires an oauth token. To simplify getting an oauth token, you can use the open source [here_oauth](https://pypi.org/project/here-oauth/0.0.2/) package to request a token using your HERE credentials.

```python
def get_oauth(credentials):
    data = json.loads(here_oauth.get_token(credentials))
    token_type = data["token_type"]
    access_token = data["access_token"]
    oauth = {"token_type": token_type, "access_token": access_token}

    return oauth

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

credentials = get_credentials()
token = get_oauth(credentials)
```

### Querying the geocoder API

Geocoder queries are HTTP GET requests. This [address geocoding example](./address_geocoding.py) demonstrates how to call the geocoding API. Note that the GET request headers include the oauth token.

```python
# URL encode the query
address = urllib.parse.quote_plus("1 Telegraph Hill, San Francisco, CA 94133")

# build the URL with the address
url = (base_url+"/"+version+"/"+geocode_service_endpoint+"?q="+address)

# add the oauth token to the header
headers = {"Authorization": token["token_type"]+" "+token["access_token"]}

# send the query to the geocoder
response = json.loads(requests.get(url, headers=headers).text)
```

In the previous example, the request was a free form query, using **=q** as the query parameter:

```
GET https://geocode.search.hereapi.com/v1/geocode?q=1+Telegraph+Hill%2C+San+Francisco%2C+CA+94133
```

The API also accepts qualified queries when the address comes from a form or structured input. A qualified query uses **=qq** as the query parameter.

```
GET https://geocode.search.hereapi.com/v1/geocode?
       qq=
           houseNumber=1;
           street=Telegraph+Hill;
           city=San+Francisco;
           state=CA;
           postalCode=94133;
           country=United+States
```

The API also accepts the house number and street name as a single input:

```
GET https://geocode.search.hereapi.com/v1/geocode?
       qq=
           street=1+ Telegraph+Hill;
           city=San+Francisco;
           state=CA;
           postalCode=94133;
           country=United+States
```

The geocoder also accepts hybrid queries that use both free form and qualified queries in the same request.

```
GET https://geocode.search.hereapi.com/v1/geocode?
        q=1+ Telegraph+Hill
        &qq=postalCode=94133

### Applying query types

When to use a query type depends on the use case. For example, geocoding a list of addresses from a file would apply to a free-form query, and structured input from a form could use a qualified or hybrid query.

## Address Geocoding Results

The geocoding API returns data from a geocoding request as a JSON document. Let's take a look at the different parts of the document.


- The 'access` element is the access point (or navigation coordinates), which is the point to start or end a drive.

```json
'access': [{'lat': 37.80266, 'lng': -122.40594}]
```

- Address geocoder can clean and normalize an address and return it in a well-structured format. For example, the address omits the street suffix and provides a 5 digit zip code. Note that the address geocoder returns the country code and name, ZIP+4, and adds the street suffix.  In addition, the geocoding API returns a standardized address suitable for mailing purposes.

```json
'address': {'city': 'San Francisco',
            'countryCode': 'USA',
            'countryName': 'United States',
            'county': 'San Francisco',
            'district': 'Telegraph Hill',
            'houseNumber': '1',
            'label': '1 Telegraph Hill Blvd, San Francisco, CA '
                        '94133-3106, United States',
            'postalCode': '94133-3106',
            'state': 'California',
            'stateCode': 'CA',
            'street': 'Telegraph Hill Blvd'},
```

- The `houseNumberType` is the  method of geocoding. The responses are PA for Point Address, Interpolated for a position based on street address range.

```json
'houseNumberType': 'PA',
```

- The geocoder also returns a 'mapView' which is a bounding box for the address and can be used to set the view in a mapping application.

```json
'mapView': {'east': -122.4048,d
                        'north'dd: 37.80356,
                        'south': 37.80176,
                        'west': -122.40708},
                        'west': -d122.40708},
```

- In the case of point addresses, a `position` can be the rooftop point, a point close to the building entry, a point close to the building or driveway, or a parking lot that belongs to the building.

```json
'position': {'lat': 37.80266, 'lng': -122.40594},
```

- The geocoding API provides a score for the quality of the geocode. The overall, or queryScore, is 0.99 because the address did not include the street suffix.

```json
'position': {'lat': 37.80266, 'lng': -122.40594},
'resultType': 'houseNumber',
'scoring': {'fieldScore': {'city': 1.0,
                            'houseNumber': 1.0,
                            'postalCode': 1.0,
                            'state': 1.0,
                            'streets': [0.9]},
            'queryScore': 0.99},
```

Even if the address is incorrect, e.g., **1 Telephone Hill, San Francisco, CA 94133**, the geocoder API provides a score that lets you evaluate the results.  The coordinates of both geocoded addresses (Telegraph Hill vs. Telephone Hill) are the same despite the incorrect street name.

```json
'position': {'lat': 37.80266, 'lng': -122.40594},
'resultType': 'houseNumber',
'scoring': {'fieldScore': {'city': 1.0,
                            'houseNumber': 1.0,
                            'postalCode': 1.0,
                            'state': 1.0,
                            'streets': [0.51]},
            'queryScore': 0.85},
    ```


## Address Geocoding Types

HERE geocoding supports many types of geocoding. This tutorial addresses HERE's geocoding options.

### Street address geocoding

Geocoding by street  is the most common method of finding a location by an address. The following example returns the geocoding result for Coit Tower in San Francisco, CA.

```python
address = urllib.parse.quote_plus("1 Telegraph Hill, San Francisco, CA 94133").replace(",","")
url = (base_url+"/"+version+"/"+geocode_service_endpoint+"?q="+address)
geocode = json.loads(requests.get(url, headers=headers).text)
print("Street address geocoding:")
pprint(geocode)
```

The geocoder returns the result:

```sh
Street address geocoding:
{'items': [{'access': [{'lat': 37.80266, 'lng': -122.40594}],
            'address': {'city': 'San Francisco',
                        'countryCode': 'USA',
                        'countryName': 'United States',
                        'county': 'San Francisco',
                        'district': 'Telegraph Hill',
                        'houseNumber': '1',
                        'label': '1 Telegraph Hill Blvd, San Francisco, CA '
                                 '94133-3106, United States',
                        'postalCode': '94133-3106',
                        'state': 'California',
                        'stateCode': 'CA',
                        'street': 'Telegraph Hill Blvd'},
            'houseNumberType': 'PA',
            'id': 'here:af:streetsection:uYm6skTu83XDOaI5FuOZpD:CggIBCD0nvTlAhABGgEx',
            'mapView': {'east': -122.4048,
                        'north': 37.80356,
                        'south': 37.80176,
                        'west': -122.40708},
            'position': {'lat': 37.80266, 'lng': -122.40594},
            'resultType': 'houseNumber',
            'scoring': {'fieldScore': {'city': 1.0,
                                       'houseNumber': 1.0,
                                       'postalCode': 1.0,
                                       'state': 1.0,
                                       'streets': [0.9]},
                        'queryScore': 0.99},
            'title': '1 Telegraph Hill Blvd, San Francisco, CA 94133-3106, '
                     'United States'}]}
```

### Geocoding by house number and postal code

In countries with precise postal codes, where the postal code is only associated with a few addresses on the same street, it is possible to geocode an address by only providing the house number and postal code. This way of geocoding is a common  practice in transport and parcel logistics.

This feature is available for Canada, the United Kingdom, the Netherlands, the United States of America (ZIP+4), Israel, Ireland, and Singapore. In Ireland and Singapore, where postal codes are precise to the unique house number, the /geocode endpoint also supports address lookup by postal code.

The `/geocode` endpoint supports this use case with qualified and freeform queries. The example includes both types of queries with the free form query commented out.

```python
# Geocoding by house number and postal code
# qualified query
house_number = "houseNumber=1"
postal_code = "postalCode=94133-3106"
country="country=USA"
url = (base_url+"/"+version+"/"+geocode_service_endpoint+"?qq="+house_number+";"+postal_code)
geocode_qualified = json.loads(requests.get(url, headers=headers).text)
print("Qualified geocode by house numner and postal code)
pprint(geocode_qualified)
print("\n\n)
# free form query
address = " 1 94133-3106"
url = (base_url+"/"+version+"/"+geocode_service_endpoint+"?q="+address)
geocode_freeform = json.loads(requests.get(url, headers=headers).text)
print("Free form geocode by house numner and postal code)
pprint(geocode_freeform)
```

In either case, the geocoder API returns the address of Coit Tower in San Francisco, CA, USA.

```json
{'items': [{'access': [{'lat': 37.80266, 'lng': -122.40594}],
            'address': {'city': 'San Francisco',
                        'countryCode': 'USA',
                        'countryName': 'United States',
                        'county': 'San Francisco',
                        'district': 'Telegraph Hill',
                        'houseNumber': '1',
                        'label': '1 Telegraph Hill Blvd, San Francisco, CA '
                                 '94133-3106, United States',
                        'postalCode': '94133-3106',
                        'state': 'California',
                        'stateCode': 'CA',
                        'street': 'Telegraph Hill Blvd'},
            'houseNumberType': 'PA',
            'id': 'here:af:streetsection:uYm6skTu83XDOaI5FuOZpD:CggIBCD0nvTlAhABGgEx',
            'mapView': {'east': -122.4048,
                        'north': 37.80356,
                        'south': 37.80176,
                        'west': -122.40708},
            'position': {'lat': 37.80266, 'lng': -122.40594},
            'resultType': 'houseNumber',
            'scoring': {'fieldScore': {'houseNumber': 1.0, 'postalCode': 1.0},
                        'queryScore': 1.0},
            'title': '1 Telegraph Hill Blvd, San Francisco, CA 94133-3106, '
                     'United States'}]}
```

### Geocoding by postal code in Singapore and Ireland

The Irish national postcode system, Eircode, assigns a unique postal code for every home and business address. In Singapore, postal codes are also as precise as addresses. People can use the postal code to find a specific address and location in both countries - without a street name, city or neighborhood, or even house number. The /geocode endpoint supports this use case. It can find a complete address for a freeform or qualified query, including only a postal code. This feature is available for these two countries only.

The postal codes should for Ireland must use the seven character [Eircode](https://www.eircode.ie/).


For example, the user can find an address of the Giant's Causeway at "44 Causeway Road, Bushmills, County Antrim, BT57 8SU" by specifying only postal code - either as qualified query or a free form query. 

```python
# Address lookup by postal code in Ireland
# Free form query
address = "BT57 8SU"
url = (base_url+"/"+version+"/"+geocode_service_endpoint+"?q="+address)
geocode = json.loads(requests.get(url, headers=headers).text)
print("Address gecoding by Eircode with a free form query:\n\n")
pprint(geocode)
# Qualified query
address = "postalCode=BT57 8SU"
url = (base_url+"/"+version+"/"+geocode_service_endpoint+"?qq="+address)
geocode = json.loads(requests.get(url, headers=headers).text)
print("Address gecoding by Eircode with a qualified query:\n\n")
pprint(geocode)
```

Either query returns the following:

```json
'items': [{'address': {'city': 'Bushmills',
                        'countryCode': 'GBR',
                        'countryName': 'United Kingdom',
                        'county': 'County Antrim',
                        'countyCode': 'ATM',
                        'label': 'BT57 8, Bushmills, Northern Ireland, United '
                                 'Kingdom',
                        'postalCode': 'BT57 8',
                        'state': 'Northern Ireland'},
            'id': 'here:cm:namedplace:22224736',
            'localityType': 'postalCode',
            'mapView': {'east': -6.38881,
                        'north': 55.25208,
                        'south': 55.14162,
                        'west': -6.6032},
            'position': {'lat': 55.20478, 'lng': -6.5232},
            'resultType': 'locality',
            'scoring': {'fieldScore': {'postalCode': 0.95}, 'queryScore': 0.71},
            'title': 'BT57 8, Bushmills, Northern Ireland, United Kingdom'}]}
```

Postal codes in Singapore consist of six digits. To ensure results from Singapore, provide either a spatial reference with an `at` parameter or with an `in` parameter with the Singapore country name or upper-case country code, "SGP". For example, the address "3 River Valley Rd, Singapore 179024" add the qualified field with the parameter in=countryCode:SGP:

```python
# Address lookup by postal code in Singapore
address = "179024"
url = (base_url+"/"+version+"/"+geocode_service_endpoint+"?q="+address+"&in=countryCode:SGP")
geocode = json.loads(requests.get(url, headers=headers).text)
print("Address gecoding by Singapore postal code:\n\n")
pprint(geocode)
```

The geocoding API returns:

```json
{'items': [{'access': [{'lat': 1.29129, 'lng': 103.84588}],
            'address': {'building': 'Clarke Quay',
                        'city': 'Singapore',
                        'countryCode': 'SGP',
                        'countryName': 'Singapore',
                        'county': 'Singapore',
                        'district': 'Central Business District',
                        'houseNumber': '3E',
                        'label': 'Clarke Quay, 3E River Valley Rd, Singapore '
                                 '179024, Singapore',
                        'postalCode': '179024',
                        'street': 'River Valley Rd'},
            'houseNumberType': 'PA',
            'id': 'here:af:streetsection:pSyqW--YhBZ8Pm7x2WgDHA:CgcIBCCH6YpyEAEaAjNFIgtDbGFya2UgUXVheQ',
            'mapView': {'east': 103.84742,
                        'north': 1.29149,
                        'south': 1.28957,
                        'west': 103.8455},
            'position': {'lat': 1.29053, 'lng': 103.84646},
            'resultType': 'houseNumber',
            'scoring': {'fieldScore': {'postalCode': 1.0}, 'queryScore': 1.0},
            'title': 'Clarke Quay, 3E River Valley Rd, Singapore 179024, '
                     'Singapore'}]}
```

## Area geocoding

You can also use the/geocode endpoint to find geo-coordinates of an area, such as city, district of a city, postal code, county, state, or country. The geo-coordinates are a routing destination for this area. In the case of administrative areas, it can be a 'well-known' street, the main railway station, or some other significant road that allows autos.

For example, a free-form text query returns geo-coordinates of San Francisco:

```python
# Area geocoding for a city
address = urllib.parse.quote_plus("San Francisco")
url = (base_url+"/"+version+"/"+geocode_service_endpoint+"?q="+address)
geocode = json.loads(requests.get(url, headers=headers).text)
print("Address gecoding by area with a free form query:")
pprint(geocode)
```

The geocoder returns "San Francisco" as city for `localityType` and `resultType` as a locality.

```json
{'items': [{'address': {'city': 'San Francisco',
                        'countryCode': 'USA',
                        'countryName': 'United States',
                        'county': 'San Francisco',
                        'label': 'San Francisco, CA, United States',
                        'postalCode': '94102',
                        'state': 'California',
                        'stateCode': 'CA'},
            'id': 'here:cm:namedplace:21010233',
            'localityType': 'city',
            'mapView': {'east': -122.34945,
                        'north': 37.83214,
                        'south': 37.60402,
                        'west': -122.51429},
            'position': {'lat': 37.77712, 'lng': -122.41964},
            'resultType': 'locality',
            'scoring': {'fieldScore': {'city': 1.0}, 'queryScore': 1.0},
            'title': 'San Francisco, CA, United States'}]}
```

If we want to geocode San Francisco County, we can use a qualified query to return and administrative area. We add the `state` and `country` to get the exact response.

```python
# Area geocoding for an administrative area
address = urllib.parse.quote_plus("county=San Francisco County;state=CA;country=USA")
url = (base_url+"/"+version+"/"+geocode_service_endpoint+"?qq="+address)
geocode = json.loads(requests.get(url, headers=headers).text)
print("Address gecoding for an administrative area:\n\n")
pprint(geocode)
```

The geocoder responds to the request with the `resultType` as administrativeArean and `administrativeAreaType` as county. 

```json
{'items': [{'address': {'countryCode': 'USA',
                        'countryName': 'United States',
                        'county': 'San Francisco',
                        'label': 'San Francisco, CA, United States',
                        'state': 'California',
                        'stateCode': 'CA'},
            'administrativeAreaType': 'county',
            'id': 'here:cm:namedplace:21010232',
            'mapView': {'east': -122.28178,
                        'north': 37.92894,
                        'south': 37.69514,
                        'west': -123.01366},
            'position': {'lat': 37.78228, 'lng': -122.41429},
            'resultType': 'administrativeArea',
            'scoring': {'fieldScore': {'country': 1.0,
                                       'county': 1.0,
                                       'state': 1.0},
                        'queryScore': 0.74},
            'title': 'San Francisco, CA, United States'}]}
```

## Place geocoding

The `/geocode` endpoint supports finding the coordinates of a known place. It supports geocoding business addresses, including business names, the same way as residential addresses.

If we request a geocode for "Coit Tower", the API will return a list of places with named "Coit." Adding "San Francisco" as a place will return the exact result.

```python
# Place geocoding
address = urllib.parse.quote_plus("Coit Tower San Francisco")
url = (base_url+"/"+version+"/"+geocode_service_endpoint+"?q="+address)
headers = {"Authorization": token["token_type"]+" "+token["access_token"]}
geocode = json.loads(requests.get(url, headers=headers).text)
print("Address geocoding for a place with a qualified query:\n\n")
pprint(geocode)
```

The response to the above request consists of a single result and looks like the following:

```json
'items': [{'access': [{'lat': 37.80266, 'lng': -122.40594}],
            'address': {'city': 'San Francisco',
                        'countryCode': 'USA',
                        'countryName': 'United States',
                        'county': 'San Francisco',
                        'district': 'Telegraph Hill',
                        'houseNumber': '1',
                        'label': 'Coit Tower, 1 Telegraph Hill Blvd, San '
                                 'Francisco, CA 94133-3106, United States',
                        'postalCode': '94133-3106',
                        'state': 'California',
                        'stateCode': 'CA',
                        'street': 'Telegraph Hill Blvd'},
            'categories': [{'id': '400-4100-0042',
                            'name': 'Bus Stop',
                            'primary': True}],
            'id': 'here:pds:place:8409q8zn-0d9e4e4d5a3c482ba6bbbdd2a574b0d2',
            'position': {'lat': 37.80266, 'lng': -122.40594},
            'resultType': 'place',
            'scoring': {'fieldScore': {'city': 1.0, 'placeName': 1.0},
                        'queryScore': 1.0},
            'title': 'Coit Tower'},
           {'access': [{'lat': 37.80266, 'lng': -122.40594}],
            'address': {'city': 'San Francisco',
                        'countryCode': 'USA',
                        'countryName': 'United States',
                        'county': 'San Francisco',
                        'district': 'Telegraph Hill',
                        'houseNumber': '1',
                        'label': 'Coit Tower, 1 Telegraph Hill Blvd, San '
                                 'Francisco, CA 94133-3106, United States',
                        'postalCode': '94133-3106',
                        'state': 'California',
                        'stateCode': 'CA',
                        'street': 'Telegraph Hill Blvd'},
            'categories': [{'id': '300-3000-0023',
                            'name': 'Tourist Attraction',
                            'primary': True},
                           {'id': '300-3000-0000',
                            'name': 'Landmark-Attraction'},
                           {'id': '300-3000-0025',
                            'name': 'Historical Monument'}],
            'id': 'here:pds:place:8409q8zn-cf21a8d50518480d9d0ddeb553a628ec',
            'position': {'lat': 37.80266, 'lng': -122.40594},
            'resultType': 'place',
            'scoring': {'fieldScore': {'city': 1.0, 'placeName': 1.0},
                        'queryScore': 1.0},
            'title': 'Coit Tower'}]}
```

## Summary

The HERE geocoding API supports a variety of methods for retrieving coordinates from text input. An address can be a complete street address, a street name and number with a postal code, only a postal code in countries that support a unique code for a location such as Ireland or Singapore, an administrative area or locality, and a place such as a landmark. In addition, the geocoder accepts free form and structured input, which supports multiple use cases ranging from batch geocoding to form input validation.

For more information and example about HERE's geocoding API, visit the [HERE Geocoding and Search API Guide](https://developer.here.com/documentation/geocoding-search-api/dev_guide/index.html).