# reader365
This is a Streamlit alarm clock application that helps to customize and enables healthy reading habits for the readers.

## Features
- Set custom reading reminders and alarms
- Schedule daily reading sessions
- Track reading habits
- Customize alarm times and messages
- Persistent storage of reading schedules
- **Alarm sound notifications** (with test button)
- **Eye wellness reminders** with customizable intervals (minimum 5 minutes)
- **Auto-refresh** every 30 seconds to check for alarms
- **Manual refresh** button for instant updates

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
streamlit run app.py
```

## How Alarms Work

1. **Auto-Check**: The app automatically refreshes every 30 seconds to check for alarms
2. **Manual Refresh**: Click the "🔄 Refresh Now" button to check immediately
3. **Test Sound**: Use the "🔊 Test Alarm Sound" button in the sidebar to verify audio works
4. **Debug Info**: Expand the "🔍 Debug Info" section to see current time, active alarms, and system status
5. **Once Per Day**: Each alarm triggers only once per day at the specified time

## Troubleshooting

- If alarms don't sound, click "🔊 Test Alarm Sound" to verify audio is working
- Check the Debug Info section to ensure your alarm is scheduled for today
- Make sure the alarm time matches the current time format (24-hour format: HH:MM)
- Verify audio libraries are installed: `pip install pygame numpy`

## Requirements
- Python 3.7+
- Streamlit
- Pygame (for alarm sounds)
- NumPy (for sound generation) 
