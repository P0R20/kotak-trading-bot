from neo_api_client import NeoAPI

# 🧠 Replace with your actual mobile number and login password
client = NeoAPI(
    consumer_key="T_Urk1YFcgmjcyYeJkjz8JtyLIoa",
    consumer_secret="m8SJ3NlzeX0ZlROST0MdROKtsf0a",
    environment="prod"
)

# 🔐 STEP 1: Login with mobile + password
client.login(mobilenumber="+919986090402", password="Priti@2711")

# 🔐 STEP 2: Enter the OTP you received on mobile
client.session_2fa("5787")

# 🎯 Print Access Token
print("🔐 Access Token:", client.access_token)
