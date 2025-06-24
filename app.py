
import streamlit as st
from PIL import Image
import os
import random
import datetime
import pytz
import zipfile
import json
from google.oauth2.service_account import Credentials
import gspread

os.environ["STREAMLIT_HOME"] = "/tmp"
os.environ["STREAMLIT_DISABLE_USAGE_STATS"] = "1"


# Unzip folders if they haven't been unzipped already
def unzip_if_needed(zip_path, extract_to):
    if not os.path.exists(extract_to):
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)

# Unzip all your folders
unzip_if_needed("yoongi.gif.zip", "yoongi.gif")
unzip_if_needed("bg-music.zip", "bg-music")
unzip_if_needed("images.zip", "images")

scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds_dict = json.loads(os.environ["GOOGLE_CREDS_JSON"])
creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
client = gspread.authorize(creds)
sheet = client.open("Welcome-Back-MinYoongi")


# Page setup
st.set_page_config(page_title="Welcome Back Yoongi", layout="centered")

# Optional: Purple Ocean Mode background animation
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

# Language selection
st.sidebar.title("🌐 Choose Language")
lang = st.sidebar.selectbox("Select your language", ["English", "한국어"], index=0)

translations = {
    "English": {
        "welcome": "💜 Welcome Back, Min Yoongi 💜",
        "countdown": "⌛ Countdown to Yoongi’s Return",
        "send_hug": "🤗 Send a Hug to Yoongi",
        "your_name": "Your Name (optional)",
        "hug_sent": "💜 Hug sent! Thank you ",
        "duplicate": "⚠️ You already sent this hug. Try changing the name!",
        "total_hugs": "🤗 Total Hugs Sent: ",
        "recent_hugs": "🌍 Recent Hugs Sent By:",
        "view_all_hugs": "📜 View All Hugs Sent",
        "leave_msg": "💌 Leave a Message for Yoongi",
        "your_msg": "Your Message to Yoongi 💜",
        "send_msg": "📨 Send Message",
        "msg_sent": "💜 Message sent to Yoongi! Thank you!",
        "latest_msg": "📨 Latest Messages:",
        "view_all_msg": "📜 View All Messages Sent to Yoongi",
        "love_from_army": "💖 Love from ARMYs"
    },
    "한국어": {
        "welcome": "💜 민윤기, 돌아와줘서 고마워요 💜",
        "countdown": "⌛ 윤기의 전역까지 남은 시간",
        "send_hug": "🤗 윤기에게 포옹 보내기",
        "your_name": "이름 (선택사항)",
        "hug_sent": "💜 포옹이 전송되었습니다! 감사합니다 ",
        "duplicate": "⚠️ 이미 이 포옹을 보냈어요. 이름을 바꿔보세요!",
        "total_hugs": "🤗 총 포옹 수: ",
        "recent_hugs": "🌍 최근 포옹:",
        "view_all_hugs": "📜 모든 포옹 보기",
        "leave_msg": "💌 윤기에게 메시지 남기기",
        "your_msg": "윤기에게 전하고 싶은 말 💜",
        "send_msg": "📨 메시지 보내기",
        "msg_sent": "💜 메시지가 전송되었습니다! 감사합니다!",
        "latest_msg": "📨 최근 메시지:",
        "view_all_msg": "📜 윤기에게 보낸 모든 메시지 보기",
        "love_from_army": "💖 아미의 사랑"
    }
}

T = translations[lang]

st.markdown(f"## {T['love_from_army']}")
st.markdown(f"### {T['welcome']}")
st.markdown(f"#### {T['countdown']}")

# Countdown
target = datetime.datetime(2025, 6, 21, 8, 0, 0, tzinfo=pytz.timezone("Asia/Seoul"))
now = datetime.datetime.now(pytz.timezone("Asia/Seoul"))
diff = target - now
st.markdown(f"<div style='font-size: 24px; font-weight: bold; color: purple;'>{diff.days} days, {diff.seconds//3600} hours, {(diff.seconds//60)%60} minutes, {diff.seconds%60} seconds 💜</div>", unsafe_allow_html=True)
st.markdown("until June 21, 2025 – 8:00 AM")

# Hugs
st.markdown(f"### {T['send_hug']}")
name = st.text_input(T["your_name"])
if "hugs" not in st.session_state:
    st.session_state["hugs"] = []
if st.button("💜 Hug"):
    if name and name not in st.session_state["hugs"]:
        st.session_state["hugs"].append(name)
        st.success(T["hug_sent"] + name)
    elif name in st.session_state["hugs"]:
        st.warning(T["duplicate"])
st.markdown(f"### {T['total_hugs']}{len(st.session_state['hugs'])}")
if len(st.session_state["hugs"]) > 0:
    st.markdown(f"**{T['recent_hugs']}**")
    for hugger in st.session_state["hugs"][-5:][::-1]:
        st.markdown(f"- 💜 {hugger}")

# Messages
st.markdown(f"### {T['leave_msg']}")
message = st.text_area(T["your_msg"])
if "msgs" not in st.session_state:
    st.session_state["msgs"] = []
if st.button(T["send_msg"]):
    if message:
        st.session_state["msgs"].append(message)
        st.success(T["msg_sent"])
if len(st.session_state["msgs"]) > 0:
    st.markdown(f"### {T['latest_msg']}")
    for msg in st.session_state["msgs"][-3:][::-1]:
        st.markdown(f"- 💌 {msg}")

# Footer
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
