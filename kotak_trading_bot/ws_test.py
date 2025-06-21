import asyncio
import websockets
import json

ACCESS_TOKEN = "eyJ4NXQiOiJNbUprWWpVMlpETmpNelpqTURBM05UZ3pObUUxTm1NNU1qTXpNR1kyWm1OaFpHUTFNakE1Tmc9PSIsImtpZCI6ImdhdGV3YXlfY2VydGlmaWNhdGVfYWxpYXMiLCJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJjbGllbnQ3MzQyOUBjYXJib24uc3VwZXIiLCJhcHBsaWNhdGlvbiI6eyJvd25lciI6ImNsaWVudDczNDI5IiwidGllclF1b3RhVHlwZSI6bnVsbCwidGllciI6IlVubGltaXRlZCIsIm5hbWUiOiJEZWZhdWx0QXBwbGljYXRpb24iLCJpZCI6ODE5OTksInV1aWQiOiIzOTM2OWMxZS05NjFhLTQxMzktOTExYi0zYzNhZGJmZTMxOGYifSwiaXNzIjoiaHR0cHM6XC9cL25hcGkua290YWtzZWN1cml0aWVzLmNvbTo0NDNcL29hdXRoMlwvdG9rZW4iLCJ0aWVySW5mbyI6eyJTUkxQT3JkZXJzIjp7InRpZXJRdW90YVR5cGUiOiJyZXF1ZXN0Q291bnQiLCJncmFwaFFMTWF4Q29tcGxleGl0eSI6MCwiZ3JhcGhRTE1heERlcHRoIjowLCJzdG9wT25RdW90YVJlYWNoIjp0cnVlLCJzcGlrZUFycmVzdExpbWl0IjoyMCwic3Bpa2VBcnJlc3RVbml0Ijoic2VjIn19LCJrZXl0eXBlIjoiUFJPRFVDVElPTiIsInBlcm1pdHRlZFJlZmVyZXIiOiIiLCJzdWJzY3JpYmVkQVBJcyI6W3sic3Vic2NyaWJlclRlbmFudERvbWFpbiI6ImNhcmJvbi5zdXBlciIsIm5hbWUiOiJCcm9rZXJhZ2UiLCJjb250ZXh0IjoiXC9hcGltXC9icm9rZXJhZ2VcLzEuMCIsInB1Ymxpc2hlciI6ImtvdGFrYWRtaW4iLCJ2ZXJzaW9uIjoiMS4wIiwic3Vic2NyaXB0aW9uVGllciI6IlNSTFBPcmRlcnMifSx7InN1YnNjcmliZXJUZW5hbnREb21haW4iOiJjYXJib24uc3VwZXIiLCJuYW1lIjoiSFNORU9BUEkiLCJjb250ZXh0IjoiXC9PcmRlcnNcLzIuMCIsInB1Ymxpc2hlciI6ImtvdGFrYWRtaW4iLCJ2ZXJzaW9uIjoiMi4wIiwic3Vic2NyaXB0aW9uVGllciI6IlNSTFBPcmRlcnMifSx7InN1YnNjcmliZXJUZW5hbnREb21haW4iOiJjYXJib24uc3VwZXIiLCJuYW1lIjoiTG9naW4iLCJjb250ZXh0IjoiXC9sb2dpblwvMS4wIiwicHVibGlzaGVyIjoia290YWthZG1pbiIsInZlcnNpb24iOiIxLjAiLCJzdWJzY3JpcHRpb25UaWVyIjoiU1JMUE9yZGVycyJ9LHsic3Vic2NyaWJlclRlbmFudERvbWFpbiI6ImNhcmJvbi5zdXBlciIsIm5hbWUiOiJNYXN0ZXJzY3JpcEZpbGVzIiwiY29udGV4dCI6IlwvRmlsZXNcLzEuMCIsInB1Ymxpc2hlciI6ImtvdGFrYWRtaW4iLCJ2ZXJzaW9uIjoiMS4wIiwic3Vic2NyaXB0aW9uVGllciI6IlNSTFBPcmRlcnMifSx7InN1YnNjcmliZXJUZW5hbnREb21haW4iOiJjYXJib24uc3VwZXIiLCJuYW1lIjoiUG9ydGZvbGlvIiwiY29udGV4dCI6IlwvUG9ydGZvbGlvXC8xLjAiLCJwdWJsaXNoZXIiOiJrb3Rha2FkbWluIiwidmVyc2lvbiI6IjEuMCIsInN1YnNjcmlwdGlvblRpZXIiOiJTUkxQT3JkZXJzIn0seyJzdWJzY3JpYmVyVGVuYW50RG9tYWluIjoiY2FyYm9uLnN1cGVyIiwibmFtZSI6IlF1b3Rlcy1BUEkiLCJjb250ZXh0IjoiXC9hcGltXC9xdW90ZXNcLzEuMCIsInB1Ymxpc2hlciI6ImtvdGFrYWRtaW4iLCJ2ZXJzaW9uIjoiMS4wIiwic3Vic2NyaXB0aW9uVGllciI6IlNSTFBPcmRlcnMifV0sInRva2VuX3R5cGUiOiJhcGlLZXkiLCJwZXJtaXR0ZWRJUCI6IiIsImlhdCI6MTc1MDQ0NTY1OSwianRpIjoiMzI3MDc0MTItMWQ4Yy00ZjNlLWI0YzQtYmRhOGViMTI0M2NlIn0=.gsTrPQSEWL_9xalcwDJcStAXgR7KIZaajwuwoV90o3dzaWI4ZrWHxLJac19HyskLfnKObQVCRvWERrgNKI2lpOThx99APlvlAtYyghzuAq7Zlxz8CsZv2iRaouc5ANguCRXFzCZTkMFSSOmTzyAS89e3zrEf0Z9ChCqzqD1ZGnTQQ2muqPcVpPDmO_iTvgelvG-7BKr9T6ljCzXX3wZWSPjVs_Hlg08w-j47HUzeDRbY7sM10LKS-ezth1lvAfzEfRa4-tEXw7pVAspetEQ8wNMjqiqTS8dyxRZVZZqigNwsJsaevn4UF7DK4XDXO7blOmVGKNrYybppTwMD3swR6g=="
WS_URL = "wss://feed.kotaksecurities.com/hypersync"  # ✅ Corrected WebSocket URL

async def kotak_ws():
    try:
        async with websockets.connect(WS_URL) as websocket:
            print("🔗 Connected to WebSocket.")

            # Step 1: Send authentication message
            auth_payload = {
                "type": "cn",
                "x-access-token": ACCESS_TOKEN,
                "source": "WEB"
            }
            await websocket.send(json.dumps(auth_payload))
            print("✅ Sent authentication payload.")

            # Step 2: Wait for server response
            while True:
                response = await websocket.recv()
                print("📨", response)

    except Exception as e:
        print("❌ WebSocket error:", e)

asyncio.run(kotak_ws())
