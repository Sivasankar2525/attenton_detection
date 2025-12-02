# Face Position Detection

Detects face position in real-time using webcam and sends SMS notifications to teacher when students are not listening.

## Features

- Multi-face detection (up to 4 faces)
- Real-time status tracking:
  - Listening Sincerely (Green) - Eyes straight, mouth closed, face straight/slightly down
  - Speaking (Cyan) - Mouth open
  - Turning (Blue) - Head turned left/right
  - Using Mobile (Orange) - Eyes looking away
  - Distracted (Red) - Head heavily down
  - Sleeping (Purple) - Eyes closed
- SMS notifications to teacher for non-listening activities

## Setup

```bash
conda env create -f environment.yml
conda activate attention_detection
pip install twilio
```

## SMS Configuration

1. Sign up at https://www.twilio.com/try-twilio (free trial available)

2. Get your credentials from Twilio Console:
   - Account SID
   - Auth Token

3. Get a Twilio phone number:
   - Go to Phone Numbers > Manage > Buy a number
   - Select a number with SMS capability

4. Edit `config.py` and update:
   - `TEACHER_PHONE`: Teacher's phone with country code (e.g., +919876543210)
   - `TWILIO_ACCOUNT_SID`: Your Account SID
   - `TWILIO_AUTH_TOKEN`: Your Auth Token
   - `TWILIO_PHONE_NUMBER`: Your Twilio phone number

## Run

```bash
python detect_face.py
```

Press 'q' to quit.

## Notes

- Notifications have a 60-second cooldown per person to avoid spam
- Each face is tracked independently
- SMS messages are sent when any non-listening activity is detected
- Free Twilio trial includes credits for testing



