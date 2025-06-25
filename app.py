from PIL import Image
import os
import random
import datetime
import pytz
import json
import time
import subprocess
import sys
import streamlit as st
import re

# --- FORCE INSTALL GOOGLE AUTH (in case Streamlit Cloud misses it) ---
required_packages = [
    "google-auth",
    "google-auth-oauthlib",
    "google-auth-httplib2",
    "google-api-python-client",
    "gspread"
]

for pkg in required_packages:
    subprocess.call([sys.executable, "-m", "pip", "install", pkg])

from google.oauth2.service_account import Credentials
import gspread

# --- ENVIRONMENT CONFIG ---
os.environ["STREAMLIT_HOME"] = "/tmp"
os.environ["XDG_CONFIG_HOME"] = "/tmp"
os.environ["STREAMLIT_DISABLE_USAGE_STATS"] = "1"

# --- GOOGLE SHEETS SETUP ---
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
try:
    creds_dict = json.loads(st.secrets["GOOGLE_CREDS_JSON"])
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    client = gspread.authorize(creds)
    sheet = client.open("Welcome-Back-MinYoongi")
except Exception as e:
    st.error(f"❌ Google Sheets setup failed: {e}")

# --- PAGE CONFIG ---
st.set_page_config(page_title="Welcome Back Yoongi", layout="centered")

# --- PURPLE OCEAN MODE ---
purple_ocean = st.toggle("🌊 Enable Purple Ocean Mode")
if purple_ocean:
    st.markdown("""
        <style>
        .stApp {
            background: linear-gradient(270deg, #3a0ca3, #7209b7, #b5179e, #f72585);
            background-size: 800% 800%;
            animation: oceanGlow 15s ease infinite;
        }
        @keyframes oceanGlow {
            0% {background-position: 0% 50%;}
            50% {background-position: 100% 50%;}
            100% {background-position: 0% 50%;}
        }
        </style>
    """, unsafe_allow_html=True)

# --- LANGUAGE SELECTOR ---
st.sidebar.title("🌐 Choose Language")
lang = st.sidebar.selectbox("Select your language", ["English", "한국어"], index=0)

if lang not in ["English", "한국어"]:
    lang = "English"

# --- TRANSLATIONS ---
translations = {
    "English": {
        "welcome": "💜 Welcome Back, Min Yoongi 💜",
        "send_hug": "🤗 Send a Hug to Yoongi",
        "your_name": "Your Name (optional)",
        "hug_sent": "💜 Hug sent! Thank you ",
        "duplicate": "⚠️ You already sent this hug. Try changing the name!",
        "total_hugs": "🤗 Total Hugs Sent: ",
        "recent_hugs": "🌍 Recent Hugs Sent By:",
        "leave_msg": "💌 Leave a Message for Yoongi",
        "your_msg": "Your Message to Yoongi 💜",
        "send_msg": "📨 Send Message",
        "msg_sent": "💜 Message sent to Yoongi! Thank you!",
        "latest_msg": "📨 Latest Messages:",
        "love_from_army": "💖 Love from ARMYs",
        "next_gif": "➡️ Next Gif"
    },
    "한국어": {
        "welcome": "💜 민윤기, 돌아와줘서 고마워요 💜",
        "send_hug": "🤗 윤기에게 포옹 보내기",
        "your_name": "이름 (선택사항)",
        "hug_sent": "💜 포옹이 전송되었습니다! 감사합니다 ",
        "duplicate": "⚠️ 이미 이 포옹을 보냈어요. 이름을 바꿔보세요!",
        "total_hugs": "🤗 총 포옹 수: ",
        "recent_hugs": "🌍 최근 포옹:",
        "leave_msg": "💌 윤기에게 메시지 남기기",
        "your_msg": "윤기에게 전하고 싶은 말 💜",
        "send_msg": "📨 메시지 보내기",
        "msg_sent": "💜 메시지가 전송되었습니다! 감사합니다!",
        "latest_msg": "📨 최근 메시지:",
        "love_from_army": "💖 아미의 사랑",
        "next_gif": "➡️ 다음 GIF"
    }
}

T = translations[lang]

# --- HEADER ---
st.markdown("## " + T["love_from_army"])
st.markdown("### " + T["welcome"])
st.balloons()

# --- 🎵 RANDOM MUSIC ---
music_folder = "bg-music"
music_files = [f for f in os.listdir(music_folder) if f.endswith(".mp3")]
if music_files:
    music_choice = os.path.join(music_folder, random.choice(music_files))
    st.audio(music_choice, format="audio/mp3")

# --- 💌 MESSAGES ---
st.markdown(f"### {T['leave_msg']}")
message = st.text_area(T["your_msg"])

if st.button(T["send_msg"]):
    if message:
        try:
            worksheet = sheet.worksheet("Messages")
        except:
            worksheet = sheet.add_worksheet("Messages", rows="1000", cols="2")

        timestamp = datetime.datetime.now(pytz.timezone("Asia/Seoul")).strftime("%Y-%m-%d %H:%M")
        worksheet.append_row([timestamp, message])
        st.success(T["msg_sent"])

# ✅ Load and show messages from Google Sheets
try:
    worksheet = sheet.worksheet("Messages")
    msg_data = worksheet.get_all_values()

    if msg_data:
        st.markdown(f"### {T['latest_msg']}")
        for row in msg_data[-3:][::-1]:  # Show last 3 messages
            st.markdown(f"- 💌 {row[1]}")
except:
    st.warning("No messages yet.")


# --- 🎬 SEQUENTIAL GIFS ---
if "gif_index" not in st.session_state:
    st.session_state.gif_index = 0

def extract_number(filename):
    match = re.search(r'(\d+)', filename)
    return int(match.group(1)) if match else 0

gif_folder = "gif"
gif_files = sorted([f for f in os.listdir(gif_folder) if f.endswith(".gif")], key=extract_number)

if gif_files:
    current_gif = os.path.join(gif_folder, gif_files[st.session_state.gif_index])
    st.image(current_gif, caption=f"💜 Yoongi - {gif_files[st.session_state.gif_index]}", use_container_width=True)
    if st.button(T["next_gif"]):
        st.session_state.gif_index = (st.session_state.gif_index + 1) % len(gif_files)

# --- 🤗 HUGS ---
st.markdown(f"### {T['send_hug']}")
name = st.text_input(T["your_name"])

# Local session list (for recent display)
if "hugs" not in st.session_state:
    st.session_state["hugs"] = []

if st.button("💜 Hug"):
    if name and name not in st.session_state["hugs"]:
        st.session_state["hugs"].append(name)

        # ✅ Save to Google Sheets
        try:
            worksheet = sheet.worksheet("Hugs")
        except:
            worksheet = sheet.add_worksheet("Hugs", rows="1000", cols="2")

        timestamp = datetime.datetime.now(pytz.timezone("Asia/Seoul")).strftime("%Y-%m-%d %H:%M")
        worksheet.append_row([timestamp, name])

        st.success(T["hug_sent"] + name)

    elif name in st.session_state["hugs"]:
        st.warning(T["duplicate"])

# ✅ Display total from Google Sheets instead of session only
try:
    worksheet = sheet.worksheet("Hugs")
    hugs_data = worksheet.get_all_values()
    st.markdown(f"### {T['total_hugs']}{len(hugs_data)}")
    if hugs_data:
        st.markdown(f"**{T['recent_hugs']}**")
        for row in hugs_data[-5:][::-1]:
            st.markdown(f"- 💜 {row[1]}")
except:
    st.warning("No hugs recorded yet.")


# --- 🖼️ RANDOM IMAGE ---
image_folder = "images"
image_files = [f for f in os.listdir(image_folder) if f.endswith(".jpg")]
if image_files:
    image_choice = os.path.join(image_folder, random.choice(image_files))
    st.image(image_choice, caption=T["love_from_army"], use_container_width=True)

# --- FOOTER ---
st.markdown("""
<hr>
<div style="overflow:hidden; white-space:nowrap;">
  <div style="
    display:inline-block;
    animation: scroll-left 12s linear infinite;
    font-size: 20px;
    color: #a855f7;
    text-shadow: black, 0 0 6px #9333ea;
  ">
    💜 ARMY Forever 💜 Yoongi is home 💜 ARMY Forever 💜 Yoongi is home 💜
  </div>
</div>
<style>
@keyframes scroll-left {
  0% { transform: translateX(100%); }
  100% { transform: translateX(-100%); }
}
</style>
""", unsafe_allow_html=True)
