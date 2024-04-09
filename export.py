import csv
import sys
import re
import hashlib
import os
import requests
import json
import time

# Load environment variables from a .env file
from dotenv import load_dotenv

load_dotenv()


# Python function to cache an API call in a folder called export, using an md5 hash of the request url as the filename
def cache_api_call(url, headers, params):
    
    # Create a hash of the url and params
    m = hashlib.md5()
    m.update(url.encode('utf-8'))
    m.update(json.dumps(params).encode('utf-8'))
    hash = m.hexdigest()
    print(hash)

    # Check if the file exists
    if os.path.exists(f'export/{hash}'):
        with open(f'export/{hash}', 'r') as f:
            return json.load(f)

    # If the file doesn't exist, make the API call
    response = requests.get(url, headers=headers, params=params)

    while response.status_code != 200:
      
        print("Sleeping for "+response.headers['Retry-After']+" seconds")
        time.sleep( int( response.headers['Retry-After']) )

        response = requests.get(url, headers=headers, params=params)
        
        # {'Date': 'Tue, 09 Apr 2024 18:21:52 GMT', 'Content-Type': 'application/json; charset=utf-8', 
        # 'Content-Length': '122', 'Connection': 'keep-alive', 
        # 'X-RateLimit-Limit': '100', 'X-RateLimit-Remaining': '-1', 'X-RateLimit-Reset': '1712686931.13', 
        # 'Retry-After': '20', 'ETag': 'W/"7a-TRpqLw623CAF21+iRL/aH+UKD2s"', 'X-Front-Time': '21'}
        
        # status_code 429

    # Write the response to the file
    with open(f'export/{hash}', 'w') as f:
        json.dump(response.json(), f)
    
    return response.json()



# Python code to make API call to API endpoint

url = "https://api2.frontapp.com/contacts"

headers = {
    "accept": "application/json",
    "authorization": "Bearer "+os.environ["FRONT_API_KEY"],
}

while url:

    response = cache_api_call(url, headers=headers, params=[])

    # print variable type of response
    # print(response["_pagination"]["next"])

    for contact in response["_results"]:
        # print(contact["_links"]["related"]["notes"])
        url = contact["_links"]["related"]["notes"]
        notes = cache_api_call(url, headers=headers, params=[])

    if  response["_pagination"]["next"]:
        print("There are more pages")
        url = response["_pagination"]["next"]
    else:
        url = False


