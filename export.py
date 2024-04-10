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
from crisp_api import Crisp
from datetime import datetime


load_dotenv()

client = Crisp()

identifier = os.environ["CRISP_IDENTIFIER"]
key = os.environ["CRISP_API_KEY"]

website_id = os.environ["CRISP_WEBSITE_ID"]

client.set_tier("plugin")
client.authenticate(identifier, key)

# /v1/website/{website_id}

# session_id = "session_1cfe5a44-ea05-4ae6-937d-37c0030019bd"

# client.website.send_message_in_conversation(
#   website_id, session_id,

#   {
#     "type": "text",
#     "content": "This message was sent from python-crisp-api! :)",
#     "from": "operator",
#     "origin": "chat"
#   }
# )

# 37f8a814-52d5-4cdf-afba-ac0cbc82fbcf

# people_id = "37f8a814-52d5-4cdf-afba-ac0cbc82fbcf"

# data = client.website.get_people_data(website_id, people_id)

# data = client.website.get_people_statistics(website_id)

# page_number = 1

# data = client.website.list_people_profiles(website_id, page_number)

# results = client.website.get_people_profile(website_id, people_id);

# data = {
#     "notepad": "Favorite Number: 10197\n\
# by: John Doe - 10:41am 04/10/2024\n\
# \n\
# Favorite Color: Blue\n\
# by: John Doe - 05:41pm 12/03/2023"
# }

# results = client.website.update_people_profile(website_id, people_id, data)

# people_id = "christopher.moyer@westerncpe.com"

# results = client.website.get_people_profile(website_id, people_id)

# print(results)

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

# url = False

while url:

    response = cache_api_call(url, headers=headers, params=[])

    # print variable type of response
    # print(response["_pagination"]["next"])

    for contact in response["_results"]:

        # print(contact["name"])
        # print(contact["handles"][0]["handle"])
        # print(contact["handles"])
        email = False

        for handle in contact["handles"]:
            if handle["source"] == "email":
                email = handle["handle"]
                break

        print(email)
        if not email:
            # print("No email found for contact")
            continue

        

        # print(contact["_links"]["related"]["notes"])
        url = contact["_links"]["related"]["notes"]
        notes = cache_api_call(url, headers=headers, params=[])

        # print(notes["_results"])
        # [{'_links': {'related': {'author': 'https://wcpe.api.frontapp.com/teammates/tea_amqtw', 'owner': None}}, 
        # 'author': {'_links': {'self': 'https://wcpe.api.frontapp.com/teammates/tea_amqtw', 
        # 'related': {'inboxes': 'https://wcpe.api.frontapp.com/teammates/tea_amqtw/inboxes', 
        # 'conversations': 'https://wcpe.api.frontapp.com/teammates/tea_amqtw/conversations'}}, 
        # 'id': 'tea_amqtw', 'email': 'cary.miller@westerncpe.com', 'username': 'cary.miller', 
        # 'first_name': 'Cary', 'last_name': 'Miller', 'is_admin': False, 'is_available': False, 'is_blocked': True, 
        # 'custom_fields': {}}, 'body': 'General inquiry on certificates from Global. did not provide name.', 
        # 'created_at': 1712013870.996, 'is_private': False}]

        if len(notes["_results"]):

            # email = "christopher.moyer@westerncpe.com"
            
            try:
                profile = client.website.get_people_profile(website_id, email)
            except:
                print("No profile found for email: "+email)
                continue

            print(profile["people_id"])
            people_id = profile["people_id"]
            notepad = []
            if "notepad" in profile and profile["notepad"] != "":
                notepad.append(profile["notepad"])

            print(email)

            for note in notes["_results"]:
                # print(note["body"])
                # print(note["author"]["first_name"])
                # print(note["author"]["last_name"])
                # print(note["author"]["email"])
                # print(note["created_at"])

                # # convert the timestamp to a datetime object in the local timezone
                # dt_object = datetime.fromtimestamp(note["created_at"])

                # # print the datetime object and its type
                # print(dt_object)
                notepad.append( note["body"] + "\n" + note["author"]["first_name"] + " " + note["author"]["last_name"] + 
                " (" + note["author"]["email"] + ")" + "\n" + str(datetime.fromtimestamp(note["created_at"]).strftime("%x %I:%M%p")) + "\n" )
            print(notepad)
            # people_id = "37f8a814-52d5-4cdf-afba-ac0cbc82fbcf"
            data = {
                "notepad": "\n".join(notepad)
            }
            results = client.website.update_people_profile(website_id, people_id, data)
            print(results)


    # url = False
    if  response["_pagination"]["next"]:
        print("There are more pages")
        url = response["_pagination"]["next"]
    else:
        url = False


