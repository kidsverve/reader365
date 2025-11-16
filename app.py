import streamlit as st
import json
import os
from datetime import datetime, time
import pandas as pd
import threading
import time as time_module
try:
    import pygame
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False

# Configure the page
st.set_page_config(
    page_title="Reader365 - Reading Habit Alarm Clock",
    page_icon="📚",
    layout="wide"
)

# File to store reading schedules
SCHEDULES_FILE = "reading_schedules.json"

# Initialize pygame mixer for audio if available
if AUDIO_AVAILABLE:
    try:
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        # Test if mixer is actually working
        pygame.mixer.get_init()
    except Exception as e:
        AUDIO_AVAILABLE = False
        print(f"Audio initialization failed: {e}")

def load_schedules():
    """Load reading schedules from JSON file"""
    if os.path.exists(SCHEDULES_FILE):
        with open(SCHEDULES_FILE, 'r') as f:
            return json.load(f)
    return []

def save_schedules(schedules):
    """Save reading schedules to JSON file"""
    with open(SCHEDULES_FILE, 'w') as f:
        json.dump(schedules, f, indent=2)

def play_alarm_sound(sound_type="beep", duration=3):
    """Play alarm sound"""
    if not AUDIO_AVAILABLE:
        print("⚠️ Audio not available - alarm will show visually only")
        return
    
    def play_in_thread():
        try:
            # Generate a beep sound
            sample_rate = 22050
            frequency = 440  # A4 note
            duration_ms = duration * 1000
            
            # Generate sine wave
            import numpy as np
            samples = int(sample_rate * duration)
            wave = np.sin(2 * np.pi * frequency * np.linspace(0, duration, samples))
            
            # Convert to 16-bit integer
            wave = (wave * 32767).astype(np.int16)
            
            # Create stereo sound
            stereo_wave = np.column_stack((wave, wave))
            
            # Play sound
            sound = pygame.sndarray.make_sound(stereo_wave)
            sound.play()
            pygame.time.wait(duration_ms)
            print(f"✅ Alarm sound played for {duration} seconds")
        except Exception as e:
            print(f"❌ Failed to play sound: {e}")
    
    # Play sound in background thread to not block UI
    thread = threading.Thread(target=play_in_thread)
    thread.daemon = True
    thread.start()

def check_current_alarms(schedules):
    """Check if any alarms should trigger now"""
    current_time = datetime.now().strftime("%H:%M")
    current_day = datetime.now().strftime("%A")
    
    active_alarms = []
    for schedule in schedules:
        if schedule.get('enabled', True):
            if current_day in schedule.get('days', []):
                if schedule.get('time') == current_time:
                    active_alarms.append(schedule)
    
    return active_alarms

def test_alarm_sound():
    """Test the alarm sound"""
    play_alarm_sound(duration=2)
    return True

# Initialize session state
if 'schedules' not in st.session_state:
    st.session_state.schedules = load_schedules()
if 'alarm_played' not in st.session_state:
    st.session_state.alarm_played = {}  # Changed to dict to track by date
if 'eye_wellness_enabled' not in st.session_state:
    st.session_state.eye_wellness_enabled = True
if 'eye_break_interval' not in st.session_state:
    st.session_state.eye_break_interval = 20  # minutes
if 'eye_break_duration' not in st.session_state:
    st.session_state.eye_break_duration = 5  # minimum 5 minutes
if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = time_module.time()

# Header
st.title("📚 Reader365 - Reading Habit Alarm Clock")
st.markdown("*Cultivate healthy reading habits with customized reminders*")

# Display current time and auto-refresh
current_time_str = datetime.now().strftime('%I:%M %p - %A, %B %d, %Y')
current_time_24h = datetime.now().strftime('%H:%M')
current_day = datetime.now().strftime('%A')

col_time1, col_time2 = st.columns([3, 1])
with col_time1:
    st.info(f"🕐 Current Time: {current_time_str}")
with col_time2:
    if st.button("🔄 Refresh Now"):
        st.rerun()

# Debug info (expandable)
with st.expander("🔍 Debug Info", expanded=False):
    st.write(f"**24h Time Format:** {current_time_24h}")
    st.write(f"**Current Day:** {current_day}")
    st.write(f"**Audio Available:** {'✅ Yes' if AUDIO_AVAILABLE else '❌ No'}")
    st.write(f"**Active Schedules:** {len([s for s in st.session_state.schedules if s.get('enabled', True)])}")
    
    if st.session_state.schedules:
        st.write("**Upcoming Alarms Today:**")
        for schedule in st.session_state.schedules:
            if schedule.get('enabled', True) and current_day in schedule.get('days', []):
                st.write(f"  - {schedule['name']} at {schedule['time']}")
    
    st.write(f"**Last Refresh:** {time_module.strftime('%H:%M:%S', time_module.localtime(st.session_state.last_refresh))}")

# Auto-refresh mechanism - rerun every 30 seconds
current_timestamp = time_module.time()
if current_timestamp - st.session_state.last_refresh >= 30:
    st.session_state.last_refresh = current_timestamp
    time_module.sleep(0.1)
    st.rerun()

# Sidebar for creating new alarms
with st.sidebar:
    st.header("⏰ Create New Reading Alarm")
    
    # Eye Wellness Settings
    with st.expander("👁️ Eye Wellness Settings", expanded=False):
        st.session_state.eye_wellness_enabled = st.checkbox(
            "Enable Eye Break Reminders", 
            value=st.session_state.eye_wellness_enabled
        )
        
        if st.session_state.eye_wellness_enabled:
            st.session_state.eye_break_interval = st.slider(
                "Break Interval (minutes)",
                10, 60, st.session_state.eye_break_interval,
                help="How often to remind you to take an eye break"
            )
            
            st.session_state.eye_break_duration = st.slider(
                "Break Duration (minutes)",
                5, 20, st.session_state.eye_break_duration,
                help="Minimum 5 minutes for effective eye rest"
            )
            
            st.info(
                f"💡 Follow the 20-20-20 rule: Every {st.session_state.eye_break_interval} minutes, "
                f"take a {st.session_state.eye_break_duration}-minute break and look at something 20 feet away."
            )
    
    st.divider()
    
    # Test alarm sound button
    if st.button("🔊 Test Alarm Sound", width='stretch'):
        if AUDIO_AVAILABLE:
            test_alarm_sound()
            st.success("✅ Alarm sound test initiated! Check terminal for audio feedback.")
        else:
            st.warning("⚠️ Audio not available in this environment (headless/no audio device). Visual alarms will still work!")
    
    st.divider()
    
    with st.form("new_alarm_form"):
        alarm_name = st.text_input("Alarm Name", placeholder="Morning Reading")
        alarm_time = st.time_input("Reading Time", value=time(9, 0))
        
        st.write("Select Days:")
        days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        selected_days = []
        
        col1, col2 = st.columns(2)
        with col1:
            for day in days_of_week[:4]:
                if st.checkbox(day, key=f"day_{day}"):
                    selected_days.append(day)
        with col2:
            for day in days_of_week[4:]:
                if st.checkbox(day, key=f"day_{day}"):
                    selected_days.append(day)
        
        reading_message = st.text_area(
            "Reminder Message",
            value="It's time for your reading session! 📖",
            height=100
        )
        
        reading_duration = st.slider("Reading Duration (minutes)", 5, 120, 30)
        
        enable_sound = st.checkbox("Enable Alarm Sound 🔊", value=True)
        
        submitted = st.form_submit_button("Create Alarm")
        
        if submitted:
            if alarm_name and selected_days:
                new_schedule = {
                    "id": len(st.session_state.schedules) + 1,
                    "name": alarm_name,
                    "time": alarm_time.strftime("%H:%M"),
                    "days": selected_days,
                    "message": reading_message,
                    "duration": reading_duration,
                    "sound_enabled": enable_sound,
                    "enabled": True,
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                st.session_state.schedules.append(new_schedule)
                save_schedules(st.session_state.schedules)
                st.success(f"✅ Alarm '{alarm_name}' created successfully!")
                st.rerun()
            else:
                st.error("Please provide an alarm name and select at least one day.")

# Main content area
st.header("📅 Your Reading Schedule")

# Check for active alarms
active_alarms = check_current_alarms(st.session_state.schedules)
if active_alarms:
    for alarm in active_alarms:
        # Create unique ID with date to allow alarm to trigger once per day
        today = datetime.now().strftime("%Y-%m-%d")
        alarm_id = f"{alarm['name']}_{alarm['time']}_{today}"
        
        # Play sound if enabled and not already played today
        if alarm.get('sound_enabled', True) and alarm_id not in st.session_state.alarm_played:
            play_alarm_sound(duration=2)
            st.session_state.alarm_played[alarm_id] = datetime.now().isoformat()
            
            # Clean up old alarm history (keep only last 7 days)
            cutoff_date = datetime.now().timestamp() - (7 * 24 * 60 * 60)
            st.session_state.alarm_played = {
                k: v for k, v in st.session_state.alarm_played.items()
                if datetime.fromisoformat(v).timestamp() > cutoff_date
            }
        
        st.warning(f"🔔 **{alarm['name']}**: {alarm['message']}")
        st.info(f"⏱️ Suggested reading duration: {alarm['duration']} minutes")
        
        # Eye wellness reminder
        if st.session_state.eye_wellness_enabled:
            st.success(
                f"👁️ **Eye Wellness Reminder**: Take a {st.session_state.eye_break_duration}-minute break "
                f"every {st.session_state.eye_break_interval} minutes during your reading session!"
            )

# Display existing schedules
if st.session_state.schedules:
    for idx, schedule in enumerate(st.session_state.schedules):
        with st.expander(f"📖 {schedule['name']} - {schedule['time']}", expanded=False):
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                st.write(f"**Time:** {schedule['time']}")
                st.write(f"**Duration:** {schedule['duration']} minutes")
                st.write(f"**Days:** {', '.join(schedule['days'])}")
            
            with col2:
                st.write(f"**Message:** {schedule['message']}")
                st.write(f"**Status:** {'🟢 Enabled' if schedule.get('enabled', True) else '🔴 Disabled'}")
                sound_status = "🔊 On" if schedule.get('sound_enabled', True) else "🔇 Off"
                st.write(f"**Sound:** {sound_status}")
            
            with col3:
                # Toggle enable/disable
                current_status = schedule.get('enabled', True)
                if st.button("🔄 Toggle", key=f"toggle_{idx}"):
                    st.session_state.schedules[idx]['enabled'] = not current_status
                    save_schedules(st.session_state.schedules)
                    st.rerun()
                
                # Delete button
                if st.button("🗑️ Delete", key=f"delete_{idx}"):
                    st.session_state.schedules.pop(idx)
                    save_schedules(st.session_state.schedules)
                    st.rerun()
else:
    st.info("👈 No reading alarms scheduled yet. Create one using the sidebar!")

# Statistics section
st.header("📊 Reading Habit Statistics")

if st.session_state.schedules:
    total_alarms = len(st.session_state.schedules)
    active_alarms_count = sum(1 for s in st.session_state.schedules if s.get('enabled', True))
    total_reading_time = sum(s.get('duration', 0) for s in st.session_state.schedules if s.get('enabled', True))
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Alarms", total_alarms)
    with col2:
        st.metric("Active Alarms", active_alarms_count)
    with col3:
        st.metric("Weekly Reading Time", f"{total_reading_time} min")
    
    # Create a schedule overview table
    st.subheader("Schedule Overview")
    schedule_data = []
    for schedule in st.session_state.schedules:
        schedule_data.append({
            "Name": schedule['name'],
            "Time": schedule['time'],
            "Days": len(schedule['days']),
            "Duration (min)": schedule['duration'],
            "Status": "Active" if schedule.get('enabled', True) else "Inactive"
        })
    
    df = pd.DataFrame(schedule_data)
    st.dataframe(df, width='stretch')
else:
    st.info("No data available yet. Start creating reading alarms!")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center'>
        <p>📚 Reader365 - Building healthy reading habits, one alarm at a time!</p>
    </div>
    """,
    unsafe_allow_html=True
)
