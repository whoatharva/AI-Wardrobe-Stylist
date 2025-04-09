import streamlit as st
import json
import requests
import random
import pandas as pd
from PIL import Image, ImageDraw
import io
from dotenv import load_dotenv
import os

load_dotenv()

# --- CONFIG ---
st.set_page_config(
    page_title="👗 AI Wardrobe Stylist",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM STYLING ---
st.markdown("""
    <style>
        .main {background-color: #f5f5f5;}
        .stButton>button {
            background-color: #ff69b4;
            color: white;
            border-radius: 10px;
            height: 3em;
            width: 10em;
            font-size: 1em;
        }
        .css-1aumxhk {padding: 2rem 1rem;}
        .stTextArea textarea {font-size: 1.1em;}
        .outfit-card {
            border: 1px solid #ddd;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 20px;
            background-color: black;
        }
    </style>
""", unsafe_allow_html=True)

# --- API KEYS ---
DALLE_ENDPOINT = os.getenv("DALLE_ENDPOINT")
DALLE_API_KEY = os.getenv("DALLE_API_KEY")

# --- DEFAULT WARDROBE JSON ---
default_wardrobe = [
    {
      "type": "top",
      "name": "white t-shirt",
      "season": ["Summer", "Spring"],
      "occasion": ["Casual"],
      "color": "White",
      "style": "Western",
      "fabric": "Cotton"
    },
    {
      "type": "top",
      "name": "black graphic tee",
      "season": ["Summer", "Spring"],
      "occasion": ["Casual", "Streetwear"],
      "color": "Black",
      "style": "Western",
      "fabric": "Cotton"
    },
    {
      "type": "top",
      "name": "blue denim shirt",
      "season": ["All"],
      "occasion": ["Casual", "Smart Casual"],
      "color": "Blue",
      "style": "Western",
      "fabric": "Denim"
    },
    {
      "type": "top",
      "name": "olive green kurta",
      "season": ["All"],
      "occasion": ["Ethnic", "Festive"],
      "color": "Olive Green",
      "style": "Indian",
      "fabric": "Cotton"
    },
    {
      "type": "top",
      "name": "white linen shirt",
      "season": ["Summer"],
      "occasion": ["Casual", "Semi-formal"],
      "color": "White",
      "style": "Western",
      "fabric": "Linen"
    },
    {
      "type": "top",
      "name": "black hoodie",
      "season": ["Winter"],
      "occasion": ["Casual"],
      "color": "Black",
      "style": "Western",
      "fabric": "Fleece"
    },
    {
      "type": "top",
      "name": "light grey sweatshirt",
      "season": ["Winter"],
      "occasion": ["Casual"],
      "color": "Grey",
      "style": "Western",
      "fabric": "Cotton Blend"
    },
    {
      "type": "top",
      "name": "navy blue polo shirt",
      "season": ["Summer", "Spring"],
      "occasion": ["Casual", "Smart Casual"],
      "color": "Navy Blue",
      "style": "Western",
      "fabric": "Cotton"
    },
    {
      "type": "outerwear",
      "name": "maroon Nehru jacket",
      "season": ["All"],
      "occasion": ["Ethnic", "Festive"],
      "color": "Maroon",
      "style": "Indian",
      "fabric": "Cotton Blend"
    },
    {
      "type": "top",
      "name": "cream cotton kurta",
      "season": ["All"],
      "occasion": ["Ethnic", "Casual"],
      "color": "Cream",
      "style": "Indian",
      "fabric": "Cotton"
    },
    {
      "type": "bottom",
      "name": "blue jeans",
      "season": ["All"],
      "occasion": ["Casual"],
      "color": "Blue",
      "style": "Western",
      "fabric": "Denim"
    },
    {
      "type": "bottom",
      "name": "black chinos",
      "season": ["All"],
      "occasion": ["Casual", "Semi-formal"],
      "color": "Black",
      "style": "Western",
      "fabric": "Cotton"
    },
    {
      "type": "bottom",
      "name": "beige chinos",
      "season": ["All"],
      "occasion": ["Casual", "Semi-formal"],
      "color": "Beige",
      "style": "Western",
      "fabric": "Cotton"
    },
    {
      "type": "bottom",
      "name": "grey joggers",
      "season": ["All"],
      "occasion": ["Casual", "Loungewear"],
      "color": "Grey",
      "style": "Athleisure",
      "fabric": "Polyester"
    },
    {
      "type": "bottom",
      "name": "white pyjama",
      "season": ["All"],
      "occasion": ["Ethnic", "Casual"],
      "color": "White",
      "style": "Indian",
      "fabric": "Cotton"
    },
    {
      "type": "bottom",
      "name": "navy blue trousers",
      "season": ["All"],
      "occasion": ["Formal", "Semi-formal"],
      "color": "Navy Blue",
      "style": "Western",
      "fabric": "Polyester"
    },
    {
      "type": "bottom",
      "name": "denim shorts",
      "season": ["Summer"],
      "occasion": ["Casual"],
      "color": "Blue",
      "style": "Western",
      "fabric": "Denim"
    },
    {
      "type": "bottom",
      "name": "dhoti pants",
      "season": ["All"],
      "occasion": ["Ethnic", "Festive"],
      "color": "Off White",
      "style": "Indian",
      "fabric": "Cotton"
    },
    {
      "type": "bottom",
      "name": "cargo pants",
      "season": ["All"],
      "occasion": ["Casual", "Outdoor"],
      "color": "Olive Green",
      "style": "Utility",
      "fabric": "Cotton"
    },
    {
      "type": "footwear",
      "name": "white sneakers",
      "season": ["All"],
      "occasion": ["Casual", "Streetwear"],
      "color": "White",
      "style": "Western",
      "fabric": "Canvas"
    },
    {
      "type": "footwear",
      "name": "black formal shoes",
      "season": ["All"],
      "occasion": ["Formal"],
      "color": "Black",
      "style": "Western",
      "fabric": "Leather"
    },
    {
      "type": "footwear",
      "name": "brown loafers",
      "season": ["All"],
      "occasion": ["Semi-formal"],
      "color": "Brown",
      "style": "Western",
      "fabric": "Leather"
    },
    {
      "type": "footwear",
      "name": "kolhapuri chappals",
      "season": ["Summer"],
      "occasion": ["Ethnic", "Casual"],
      "color": "Tan",
      "style": "Indian",
      "fabric": "Leather"
    },
    {
      "type": "footwear",
      "name": "tan sandals",
      "season": ["Summer"],
      "occasion": ["Casual"],
      "color": "Tan",
      "style": "Western",
      "fabric": "Leather"
    },
    {
      "type": "footwear",
      "name": "sports shoes",
      "season": ["All"],
      "occasion": ["Sports", "Casual"],
      "color": "Multicolor",
      "style": "Athleisure",
      "fabric": "Synthetic"
    },
    {
      "type": "footwear",
      "name": "mojari",
      "season": ["All"],
      "occasion": ["Ethnic", "Wedding"],
      "color": "Brown",
      "style": "Indian",
      "fabric": "Leather"
    },
    {
      "type": "accessory",
      "name": "silver watch",
      "season": ["All"],
      "occasion": ["Formal", "Casual"],
      "color": "Silver",
      "style": "Western",
      "fabric": "Metal"
    },
    {
      "type": "accessory",
      "name": "black sunglasses",
      "season": ["Summer"],
      "occasion": ["Casual", "Travel"],
      "color": "Black",
      "style": "Western",
      "fabric": "Plastic"
    },
    {
      "type": "accessory",
      "name": "leather belt",
      "season": ["All"],
      "occasion": ["Formal", "Casual"],
      "color": "Brown",
      "style": "Western",
      "fabric": "Leather"
    },
    {
      "type": "accessory",
      "name": "red pocket square",
      "season": ["All"],
      "occasion": ["Formal", "Wedding"],
      "color": "Red",
      "style": "Western",
      "fabric": "Silk"
    },
    {
      "type": "accessory",
      "name": "brown leather bracelet",
      "season": ["All"],
      "occasion": ["Casual"],
      "color": "Brown",
      "style": "Western",
      "fabric": "Leather"
    },
    {
      "type": "accessory",
      "name": "black cap",
      "season": ["Summer"],
      "occasion": ["Casual", "Outdoor"],
      "color": "Black",
      "style": "Western",
      "fabric": "Cotton"
    },
    {
      "type": "accessory",
      "name": "cotton stole",
      "season": ["Winter", "Autumn"],
      "occasion": ["Ethnic", "Casual"],
      "color": "Multicolor",
      "style": "Indian",
      "fabric": "Cotton"
    },
    {
      "type": "accessory",
      "name": "rudraksha mala",
      "season": ["All"],
      "occasion": ["Spiritual", "Ethnic"],
      "color": "Brown",
      "style": "Indian",
      "fabric": "Wood"
    },
    {
      "type": "outerwear",
      "name": "denim jacket",
      "season": ["Winter", "Autumn"],
      "occasion": ["Casual"],
      "color": "Blue",
      "style": "Western",
      "fabric": "Denim"
    },
    {
      "type": "outerwear",
      "name": "bomber jacket",
      "season": ["Winter"],
      "occasion": ["Casual", "Smart Casual"],
      "color": "Black",
      "style": "Western",
      "fabric": "Polyester"
    },
    {
      "type": "outerwear",
      "name": "raincoat",
      "season": ["Monsoon"],
      "occasion": ["Outdoor", "Travel"],
      "color": "Various",
      "style": "Utility",
      "fabric": "Waterproof"
    },
    {
      "type": "outerwear",
      "name": "woolen blazer",
      "season": ["Winter"],
      "occasion": ["Formal", "Semi-formal"],
      "color": "Grey",
      "style": "Western",
      "fabric": "Wool"
    },
    {
      "type": "outerwear",
      "name": "hooded windbreaker",
      "season": ["Spring", "Autumn"],
      "occasion": ["Outdoor", "Travel"],
      "color": "Multicolor",
      "style": "Western",
      "fabric": "Nylon"
    }
  ]
  
# --- SKIN TONE MATCHES ---
COLOR_SKIN_MATCHES = {
    "Fair": ["Navy", "Blue", "Burgundy", "Purple", "Emerald", "Teal"],
    "Wheatish": ["Coral", "Orange", "Green", "Burgundy", "Teal", "Light Blue"],
    "Brown": ["Gold", "Mustard", "Emerald", "Royal Blue", "Purple", "Red"],
    "Dark": ["Bright Red", "Yellow", "Orange", "Hot Pink", "Turquoise", "Royal Blue"]
}


# --- FILE UPLOAD ---
st.title("Use Inbuilt Json or Upload your custom data")
uploaded_file = st.file_uploader("📤 Upload your wardrobe JSON file (optional)", type=["json"])
try:
    if uploaded_file:
        clothes_data = json.load(uploaded_file)
        st.success(f"✅ Custom wardrobe loaded! ({len(clothes_data)} items)")
    else:
        clothes_data = default_wardrobe
        st.info(f"ℹ️ Using default wardrobe. ({len(clothes_data)} items)")
except Exception as e:
    st.error(f"❌ Error loading wardrobe file: {e}")
    clothes_data = default_wardrobe

# --- PREVIEW TABLE ---
st.markdown("### 👕 Available Wardrobe")
st.dataframe(pd.DataFrame(clothes_data))

# --- HELPER FUNCTIONS ---
def generate_color_palette(items):
    colors = [item.get("color", "").lower() for item in items if item.get("color")]
    color_map = {
        "black": "#000000", "white": "#FFFFFF", "red": "#FF0000", "green": "#00FF00", "blue": "#0000FF",
        "yellow": "#FFFF00", "purple": "#800080", "orange": "#FFA500", "pink": "#FFC0CB", "grey": "#808080",
        "gray": "#808080", "brown": "#A52A2A", "navy": "#000080", "teal": "#008080", "silver": "#C0C0C0",
        "cream": "#FFFDD0", "beige": "#F5F5DC"
    }
    return [color_map.get(c, "#CCCCCC") for c in colors]

def create_palette_image(colors, width=300, height=50):
    if not colors: return None
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    block_width = width / len(colors)
    for i, color in enumerate(colors):
        draw.rectangle([(i * block_width, 0), ((i + 1) * block_width, height)], fill=color)
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    return buf.getvalue()

def color_harmony_score(items):
    colors = [item.get("color", "").lower() for item in items if item.get("color")]
    neutrals = ["black", "white", "grey", "gray", "beige", "tan", "cream", "navy"]
    has_neutral = any(color in neutrals for color in colors)
    unique_colors = len(set(colors))
    if has_neutral and unique_colors <= 3: return "Excellent"
    elif has_neutral or unique_colors <= 3: return "Good"
    else: return "Fair"

def get_outfit_reasoning(outfit_items, skin_tone):
    outfit_types = {item.get("type"): item for item in outfit_items}
    total_items = len(outfit_items)
    color_score = color_harmony_score(outfit_items)
    complimentary_colors = sum(1 for item in outfit_items if item.get("color") in COLOR_SKIN_MATCHES.get(skin_tone, []))
    reasoning = []
    if total_items >= 3:
        reasoning.append("✅ Well-balanced outfit with multiple complementary pieces.")
    reasoning.append(f"✅ Color harmony: {color_score}")
    skin_compatibility = "High" if complimentary_colors >= 2 else "Medium" if complimentary_colors == 1 else "Low"
    reasoning.append(f"✅ {skin_tone} skin tone compatibility: {skin_compatibility}")
    if "top" in outfit_types and "bottom" in outfit_types:
        reasoning.append("✅ Complete outfit with coordinated top and bottom.")
    if "accessory" in outfit_types:
        reasoning.append("✅ Accessories add personal style and elevate the outfit.")
    return reasoning

def create_better_dalle_prompt(outfit_items, gender, skin_tone, body_shape, occasion, season, custom_prompt):
    outfit_text = ", ".join(f"{item.get('color')} {item.get('name')}" for item in outfit_items)
    return (
        f"Photorealistic fashion shot of a {gender.lower()} with {skin_tone.lower()} skin tone and {body_shape.lower()} build. "
        f"Wearing a {season.lower()} {occasion.lower()} outfit: {outfit_text}. {custom_prompt}"
    )

def display_clean_item(item):
    color = item.get("color", "").lower()
    name = item.get("name", "")
    if color in name.lower():
        return name.title()
    return f"{color.title()} {name.title()}"

# --- SIDEBAR ---
st.sidebar.header("✨ Options")
selected_occasion = st.sidebar.selectbox("🎉 Occasion", ["Casual", "Formal", "Ethnic", "Semi-formal"])
selected_season = st.sidebar.selectbox("🌦️ Season", ["Summer", "Winter", "All"])
user_name = st.sidebar.text_input("🧑 Your Name", "Fashionista")
gender = st.sidebar.selectbox("🚻 Gender", ["Male", "Female"])
body_shape = st.sidebar.selectbox("🏋️ Body Shape", ["Slim", "Average", "Athletic", "Plus Size"])
skin_tone = st.sidebar.selectbox("🎨 Skin Tone", ["Fair", "Wheatish", "Brown", "Dark"])
num_outfits = st.sidebar.slider("Number of Outfit Options", 1, 5, 3)

# --- MAIN ---
st.title("AI Wardrobe Stylist")
st.markdown("Upload your wardrobe or use the default one. Generate personalized outfits with reasoning!")

# --- TEXT PROMPT ---
prompt = st.text_area("💬 Describe the style or vibe you're going for", "A stylish outfit that looks effortlessly cool.")

# --- GENERATE ---
if st.button("🪄 Generate Outfit Options"):
    filtered = [item for item in clothes_data if selected_occasion in item['occasion'] or "All" in item['occasion']]
    filtered = [item for item in filtered if selected_season in item['season'] or "All" in item['season']]
    if not filtered:
        st.warning("No exact matches found. Using full wardrobe.")
        filtered = clothes_data

    items_by_type = {}
    for item in filtered:
        items_by_type.setdefault(item['type'], []).append(item)

    for i in range(num_outfits):
        st.markdown(f"## 🎯 Option {i + 1}")
        outfit_items = []
        for t in ["top", "bottom", "footwear", "accessory"]:
            if t in items_by_type:
                outfit_items.append(random.choice(items_by_type[t]))
        reasoning = get_outfit_reasoning(outfit_items, skin_tone)
        palette = generate_color_palette(outfit_items)
        img = create_palette_image(palette)

        col1, col2 = st.columns([3, 2])
        with col1:
            st.subheader("Outfit")
            for item in outfit_items:
                st.markdown(f"- **{item['type'].capitalize()}**: {display_clean_item(item)}")
            st.subheader("Why it works")
            for reason in reasoning:
                st.markdown(reason)
            if img:
                st.image(img, caption="Color Palette")

        with col2:
            st.subheader("Generated Image")
            try:
                prompt_text = create_better_dalle_prompt(outfit_items, gender, skin_tone, body_shape, selected_occasion, selected_season, prompt)
                dalle_response = requests.post(
                    DALLE_ENDPOINT,
                    headers={"api-key": DALLE_API_KEY, "Content-Type": "application/json"},
                    json={"prompt": prompt_text, "size": "1024x1024", "n": 1}
                )
                if dalle_response.status_code == 200:
                    url = dalle_response.json()['data'][0]['url']
                    st.image(url, caption="AI Outfit", use_container_width=True)
                    with st.expander("Prompt used"):
                        st.code(prompt_text)
                else:
                    st.error(f"Failed to generate image. Status: {dalle_response.status_code}")
            except Exception as e:
                st.error(f"Image generation failed: {str(e)}")