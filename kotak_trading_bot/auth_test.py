from neo_api_client import NeoAPI

client = NeoAPI(
    consumer_key="T_Urk1YFcgmjcyYeJkjz8JtyLIoa",
    consumer_secret="m8SJ3NlzeX0ZlROST0MdROKtsf0a",
    environment="prod"
)

client.login(mobilenumber="+919986090402", password="Priti@2711")
client.session_2fa("5787")

print("🔐 Access Token:", client.access_token)
