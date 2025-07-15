import os

print("--- Checking for environment variables ---")

api_key = os.getenv('AMADEUS_API_KEY')
api_secret = os.getenv('AMADEUS_API_SECRET')

print(f"Value read for AMADEUS_API_KEY: {api_key}")
print(f"Value read for AMADEUS_API_SECRET: {api_secret}")

if not api_key or not api_secret:
    print("\n❌ RESULT: FAILED. Python cannot see the variables.")
    print("   This confirms the issue is with how the variables are being set in your terminal.")
else:
    print("\n✅ RESULT: SUCCESS! Python can see your variables.")
    print("   If you see this message, you can now try running the main 'find_flights.py' script again.")