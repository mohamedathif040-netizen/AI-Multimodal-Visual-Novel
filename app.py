import streamlit as st
from google import genai
from dotenv import load_dotenv
import os
import json
from PIL import Image
from io import BytesIO
import requests
import urllib.parse
from gtts import gTTS



def set_background():
    st.markdown(
        """
        <style>

        .stApp{
    background-image: url("https://images.unsplash.com/photo-1519681393784-d120267933ba?auto=format&fit=crop&w=1920&q=80");
    background-size:cover;
    background-position:center;
    background-repeat:no-repeat;
    background-attachment:fixed;
}
.stApp::before{
    content:"";
    position:fixed;
    inset:0;
    background:rgba(0,0,0,0.55);
    z-index:-1;
}
        .block-container{
    background: rgba(10, 10, 20, 0.72);
    backdrop-filter: blur(14px);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 20px;
    padding: 2rem;
    box-shadow: 0 0 35px rgba(0,0,0,0.5);
}
        [data-testid="stSidebar"]{
            background: rgba(15,15,20,0.90);
        }

        h1{
            color: white;
            text-shadow: 50px 10px 50px black;
        }

        h2,h3{
            color: white;
        }

        p,li,label{
            color: white;
        }

        .stButton>button{
    width:100%;
    border:none;
    border-radius:14px;
    background:linear-gradient(90deg,#4f46e5,#9333ea);
    color:white;
    font-size:18px;
    font-weight:700;
    padding:12px;
    transition:0.3s;
}

.stButton>button:hover{
    transform:scale(1.03);
    box-shadow:0 0 20px #9333ea;
}

        </style>
        """,
        unsafe_allow_html=True
    )
# ----------------------------
# Load Environment Variables
# ----------------------------
load_dotenv()

# ----------------------------
# Page Configuration
# ----------------------------
st.set_page_config(
    page_title="AI Visual Novel",
    page_icon="🎮",
    layout="wide"
)
set_background()
# ----------------------------
# Cache Gemini Client
# ----------------------------
@st.cache_resource
def get_gemini_client():
    api_key = os.getenv("GEMINI_API_KEY")
    return genai.Client(api_key=api_key)

client = get_gemini_client()

# ----------------------------
# Session State Initialization
# ----------------------------

if "chat" not in st.session_state:
    st.session_state.chat = None

if "story_history" not in st.session_state:
    st.session_state.story_history = []

if "current_story" not in st.session_state:
    st.session_state.current_story = None

if "current_image_prompt" not in st.session_state:
    st.session_state.current_image_prompt = ""
    
if "selected_option" not in st.session_state:
    st.session_state.selected_option = None
    
if "current_options" not in st.session_state:
    st.session_state.current_options = []

def generate_story(user_choice, genre, art_style):

    """
    Sends the user's choice to Gemini and expects a JSON response.
    """

    prompt = f"""
You are an interactive Visual Novel Game Engine.

The story genre is: {genre}

The art style is: {art_style}

The player's latest action is:

{user_choice}

IMPORTANT RULES:

Return ONLY valid JSON.

Do NOT use markdown.

Do NOT wrap the JSON inside ```.

The JSON must have EXACTLY these keys:

{{
    "story_text": "...",
    "image_prompt": "...",
    "options": [
        "...",
        "...",
        "..."
    ]
}}

Requirements:

1. story_text should be 120-180 words.

2. image_prompt should be detailed for an AI image generator and mention the chosen art style.

3. options should contain exactly 3 different actions.

Return ONLY JSON.
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=prompt
    )

    return response.text
def generate_image(image_prompt):
    """
    Generate image using Pollinations API
    """

    prompt = urllib.parse.quote(image_prompt)

    url = f"https://image.pollinations.ai/prompt/{prompt}"

    response = requests.get(url, timeout=30)

    response.raise_for_status()

    return Image.open(BytesIO(response.content))

def generate_audio(story_text):
    """
    Convert story text to speech using gTTS
    """

    tts = gTTS(text=story_text, lang="en")

    audio_path = "audio/story.mp3"

    tts.save(audio_path)

    return audio_path
# ----------------------------
# Sidebar
# ----------------------------
st.sidebar.title("📖 Story Settings")

genre = st.sidebar.selectbox(
    "Choose Story Genre",
    [
        "Fantasy",
        "Sci-Fi",
        "Horror",
        "Mystery",
        "Adventure",
        "Cyberpunk"
    ]
)

art_style = st.sidebar.selectbox(
    "Choose Art Style",
    [
        "Anime",
        "Realistic",
        "Pixel Art",
        "Fantasy Painting",
        "Comic Book",
        "3D Render"
    ]
)

start_story = st.sidebar.button("🚀 Start Story")

if st.sidebar.button("🔄 New Story"):
    st.session_state.current_story = None
    st.session_state.current_image_prompt = ""
    st.session_state.current_options = []
    st.session_state.story_history = []
    st.session_state.selected_option = None
    st.rerun()
# ----------------------------
# Main Page
# ----------------------------
st.markdown("""
<h1 style="
text-align:center;
font-size:54px;
font-weight:900;
color:#ffffff;
text-shadow:
0 0 10px #8b5cf6,
0 0 20px #8b5cf6,
0 0 35px #4f46e5;
">
🎮 AI Multi-Modal Visual Novel
</h1>
""", unsafe_allow_html=True)

st.markdown(
"<h4 style='text-align:center;color:#dddddd;'>Powered by Gemini • Pollinations AI • gTTS • Streamlit</h4>",
unsafe_allow_html=True
)

st.write(
    """
Welcome!

Choose your story settings from the sidebar and click **Start Story** to begin your adventure.

The AI will generate:
- 📖 Story
- 🖼️ Image
- 🔊 Narration
- 🎲 Multiple Choices
"""
)

st.info(f"Genre: **{genre}** | Art Style: **{art_style}**")

if start_story:

    with st.spinner("Generating story..."):

        response = generate_story(
            "Start the adventure",
            genre,
            art_style
        )

        story_data = json.loads(response)

        st.session_state.current_story = story_data["story_text"]
        st.session_state.story_history.append(story_data["story_text"])
        st.session_state.current_image_prompt = story_data["image_prompt"]
        st.session_state.current_options = story_data["options"]

st.divider()

st.subheader("📜 Story History")

for i, story in enumerate(st.session_state.story_history, start=1):
    with st.expander(f"Scene {i}"):
        st.write(story)

# Display the current story from session state
if st.session_state.current_story:

    st.subheader("📖 Story")

    st.markdown(f"""
    <div style="
    background: rgba(0,0,0,0.55);
    padding:25px;
    border-radius:15px;
    border-left:5px solid #8b5cf6;
    font-size:18px;
    line-height:1.8;
    color:white;
    box-shadow:0 0 15px rgba(0,0,0,0.4);
    ">
    {st.session_state.current_story}
    </div>
    """, unsafe_allow_html=True)
    
    try:
        audio_file = generate_audio(st.session_state.current_story)
        st.audio(audio_file)
    except Exception:
        st.toast("🔊 Audio generation failed.")

    st.subheader("🖼 Scene")

    try:
        image = generate_image(st.session_state.current_image_prompt)
        st.image(image, use_container_width=True)
        st.caption("🎨 AI-generated scene")
    except Exception:
        st.toast("🖼 Image server is busy, skipping visual...")

    st.subheader("🎮 Choose Your Next Action")

    for option in st.session_state.current_options:

        if st.button(option, use_container_width=True):

            with st.spinner("Continuing your adventure..."):

                response = generate_story(option, genre, art_style)

                story_data = json.loads(response)

                st.session_state.current_story = story_data["story_text"]
                st.session_state.story_history.append(story_data["story_text"])
                st.session_state.current_image_prompt = story_data["image_prompt"]
                st.session_state.current_options = story_data["options"]

                st.rerun()