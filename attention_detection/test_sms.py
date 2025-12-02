from twilio.rest import Client
from config import TEACHER_PHONE, TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER

print("Testing Twilio SMS...")
print(f"From: {TWILIO_PHONE_NUMBER}")
print(f"To: {TEACHER_PHONE}")
print(f"Account SID: {TWILIO_ACCOUNT_SID}")
print(f"Auth Token: {TWILIO_AUTH_TOKEN[:10]}...")

try:
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    
    message = client.messages.create(
        from_=TWILIO_PHONE_NUMBER,
        body="Test SMS from Attention Detection System",
        to=TEACHER_PHONE
    )
    
    print(f"\n✓ SUCCESS! SMS sent successfully!")
    print(f"Message SID: {message.sid}")
    print(f"Status: {message.status}")
    print(f"\nCheck your phone for the SMS!")
    
except Exception as e:
    print(f"\n✗ ERROR: {e}")
    print("\nPossible issues:")
    print("1. Check if your Twilio phone number is verified")
    print("2. Check if teacher's phone number is verified (for trial accounts)")
    print("3. Verify Account SID and Auth Token are correct")
    print("4. Check if you have SMS credits in your Twilio account")
