import argparse
import json
import sys
import os

import jwt


# The token that is to be provided as the single argument to this script is
#  generated using the OpsUI.  In the Users section, find the user whose PW needs resetting
#  click the button to Generate Refresh Token and use the resulting token as an argument here.

try:
    token = sys.argv[1]
except IndexError:
    print("Rerun script with one argument, the Java Web Token for the Password Reset")
    sys.exit(1)

decoded_token = jwt.decode(token, verify=False)


print("\n\n##############")
print("Decoded Token:")
print(json.dumps(decoded_token, indent=2))
print("##############")


url_base = 'hxxps://alpha.randori.io/activate?token='

pw_reset_url = url_base + token

print("\n##############")
print("Password Reset URL:")
print(pw_reset_url)
print("##############\n\n")

print("Note:  Replace 'hxxps' with 'https' to make the URL work.  I am sending the URL with 'hxxps' \
because the password reset token is a one-time use token and some email security gateways \
visit every link in an email as a protection measure and this should prevent that behavior.\n")

