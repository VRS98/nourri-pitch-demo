import streamlit as st
import time
import base64
import os

def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except Exception:
        return ""

brand_logo_b64 = get_base64_of_bin_file("brand_logo.jpg")
logo_html = f"""
<div style="background:#fff; padding:12px; border-radius:16px; margin-bottom:20px; display:flex; align-items:center; justify-content:center; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
<img src="data:image/jpeg;base64,{brand_logo_b64}" style="max-width: 100%; height:auto; border-radius:8px;">
</div>
""" if brand_logo_b64 else """
<div style="display:flex; align-items:center; gap:12px; margin-bottom: 20px; padding: 10px 5px;">
<div style="background:#1c6b42; width:40px; height:40px; border-radius:12px; display:flex; align-items:center; justify-content:center; font-size:20px;">🌿</div>
<div>
<div style="font-weight:800; font-size:20px; color:#fff; line-height:1.1;">Nourri</div>
<div style="color:#5a9870; font-size:13px; font-weight:500;">AI Food Companion</div>
</div>
</div>
"""

# Configure page
st.set_page_config(page_title="Nourri · AI Food Companion", layout="wide", initial_sidebar_state="expanded")

# --- DATA ---
INVENTORY = [
    {"name":"Organic Heirloom Spinach", "cat":"Greens", "days":1, "co2":0.3, "ns":"A", "qty":"200g", "conf":97},
    {"name":"Wild Arugula", "cat":"Greens", "days":2, "co2":0.2, "ns":"A", "qty":"100g", "conf":94},
    {"name":"Local Oyster Mushrooms", "cat":"Fungi", "days":2, "co2":0.2, "ns":"A", "qty":"150g", "conf":98},
    {"name":"Heirloom Cherry Tomatoes", "cat":"Vegetables", "days":3, "co2":0.4, "ns":"A", "qty":"250g", "conf":96},
    {"name":"Artisan Sourdough Bread", "cat":"Bakery", "days":3, "co2":0.8, "ns":"B", "qty":"½ loaf", "conf":91},
    {"name":"Biodynamic Greek Yogurt", "cat":"Dairy", "days":4, "co2":1.8, "ns":"A", "qty":"500g", "conf":99},
    {"name":"Organic Oat Milk", "cat":"Dairy Alt", "days":5, "co2":0.5, "ns":"B", "qty":"1L", "conf":99},
    {"name":"Pasture-Raised Eggs", "cat":"Protein", "days":10, "co2":1.1, "ns":"A", "qty":"6 eggs", "conf":97},
    {"name":"Sheep's Milk Feta", "cat":"Dairy", "days":7, "co2":2.5, "ns":"C", "qty":"150g", "conf":93},
    {"name":"Organic Lemon", "cat":"Citrus", "days":14, "co2":0.3, "ns":"A", "qty":"3 pcs", "conf":98},
]

RECIPES = [
    {
        "name": "Rescue Greens & Mushroom Frittata", "emoji": "🥗",
        "time": "20 min", "serves": 3, "diff": "Easy", "co2": 1.4, "ns": "A",
        "inFridge": ["Organic Heirloom Spinach","Local Oyster Mushrooms","Pasture-Raised Eggs"],
        "toOrder": ["Olive Oil","Parmesan"],
        "aiNote": "Prioritised spinach (1 day left) and mushrooms (2 days) — combining them maximises waste prevention while creating nutritional synergy: complete protein, iron, and B-vitamins in one dish.",
        "steps": [
            "Preheat oven 190°C, heat olive oil in an oven-safe pan.",
            "Sauté mushrooms 5 min until golden.",
            "Add spinach, wilt 2 min.",
            "Whisk 5 eggs + 2 tbsp oat milk + pepper + nutmeg.",
            "Pour egg mix over veg, top with crumbled feta.",
            "Bake 12–15 min until set and golden."
        ]
    },
    {
        "name": "Shakshuka with Wilting Arugula", "emoji": "🍳",
        "time": "25 min", "serves": 2, "diff": "Easy", "co2": 1.5, "ns": "A",
        "inFridge": ["Heirloom Cherry Tomatoes","Pasture-Raised Eggs","Wild Arugula","Sheep's Milk Feta"],
        "toOrder": ["Harissa Paste","Cumin"],
        "aiNote": "Rescues 4 items simultaneously. Arugula (2 days) replaces traditional parsley — stronger flavour but complementary. Highest waste-prevention score of all suggestions.",
        "steps": [
            "Sauté onion with harissa + cumin 5 min.",
            "Add tomatoes, crush lightly, simmer 10 min.",
            "Make wells in sauce, crack in eggs.",
            "Cover and cook 6–8 min to your liking.",
            "Top with crumbled feta + raw arugula.",
            "Serve from pan with sourdough."
        ]
    },
    {
        "name": "Lemon Yogurt Parfait Bowl", "emoji": "🥣",
        "time": "10 min", "serves": 2, "diff": "Easy", "co2": 0.6, "ns": "A",
        "inFridge": ["Biodynamic Greek Yogurt","Organic Lemon"],
        "toOrder": ["Granola","Mixed Berries","Honey"],
        "aiNote": "Yogurt hits day 4 soon — 2 servings/day clears stock before expiry. Lemon adds flavour complexity and brightness. Minimal carbon impact: 0.6 kg CO₂e.",
        "steps": [
            "Zest and juice the lemon, stir into yogurt with honey.",
            "Layer yogurt, then granola, then berries.",
            "Repeat layers.",
            "Finish with extra lemon zest.",
            "Serve immediately or refrigerate overnight."
        ]
    }
]

AGENT_STEPS = [
  {"label": "STEP 1 / 5 — Analyzing inventory...", "icon": "📋", "call": 'check_inventory_levels(user_id="user_001")', "response": '{"spinach":{"qty":"200g","days_left":1,"status":"⚠ CRITICAL"},"oat_milk":{"qty":"0.3L","days_left":3,"status":"⚠ LOW"},"eggs":{"qty":"2 eggs","days_left":10,"status":"⚠ LOW"}}', "insight": "⚡ Identified 3 deficit items — replenishment needed within 4 days", "delay": 1.3},
  {"label": "STEP 2 / 5 — Forecasting consumption...", "icon": "📈", "call": 'get_consumption_forecast(user_id="user_001", horizon="7_days")', "response": '{"oat_milk":"2.1 L/week","eggs":"6/week","leafy_greens":"280g/week","model_confidence":0.91}', "insight": "📊 Forecast confirms: current stock covers < 1 day of demand", "delay": 1.1},
  {"label": "STEP 3 / 5 — Querying farm partners...", "icon": "🌾", "call": 'query_farm_partners(location="Paris 11e", items=["baby_spinach","oat_milk","eggs"], max_km=20)', "response": '{"Radicle Urban Farms (4km)":{"baby_spinach":"300g→€2.80","oat_milk":"2×1L→€3.80","co2_saved":"1.8kg"},"Green Valley Cooperative (12km)":{"eggs":"12-pack→€4.20","co2_saved":"0.8kg"}}', "insight": "🌿 2 trusted partners · 3 items · combined CO₂ saving: 2.6 kg", "delay": 1.5},
  {"label": "STEP 4 / 5 — Running guardrails...", "icon": "🛡️", "guardrails": True, "delay": 1.8},
  {"label": "STEP 5 / 5 — Placing order...", "icon": "✅", "call": 'place_order(items=["baby_spinach_300g","oat_milk_2L","eggs_12pack"], payment="card_****4521", delivery="asap")', "response": '{"order_id":"NR-20260617-0891","status":"CONFIRMED","eta":"~2 hours","total":"€10.80","co2_saved":"2.6kg"}', "insight": "🎉 Order NR-20260617-0891 confirmed · Delivery by 14:45 · €10.80 · 2.6kg CO₂e saved", "delay": 1.0}
]

# --- STATE INITIALIZATION ---
defaults = {"scanned": False, "inventory": [], "selected_recipe": None, "auto_mode": False, "agent_done": False, "favorites": set(), "nav_view": "📷 Smart Scanner"}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# --- CSS INJECTION ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

/* Hide Streamlit Chrome */
#MainMenu, footer, .stDeployButton {visibility: hidden; display: none;}
header[data-testid="stHeader"] { background: transparent !important; }

/* Sidebar Toggle Fix */
[data-testid="collapsedControl"] {
    display: flex !important;
    background-color: #fff !important;
    border-radius: 50% !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1) !important;
    margin: 16px !important;
}
[data-testid="collapsedControl"] svg {
    fill: #0c2218 !important;
}

/* Global Background */
.stApp {
    background-color: #f5f0e4;
    font-family: 'Inter', sans-serif;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #0c2218 !important;
    border-right: 1px solid rgba(255,255,255,0.05);
}
section[data-testid="stSidebar"] * { color: #fff; }

/* Typography */
.n-section-label { color: #3a7a55; font-size: 12px; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 4px; }
.n-h1 { color: #0c2218; font-size: 28px; font-weight: 800; letter-spacing: -0.03em; margin: 0; }
.n-subtitle { color: #6b7d72; font-size: 14px; font-weight: 500; margin-top: 4px; margin-bottom: 20px;}
.n-header-container { border-bottom: 1px solid rgba(0,0,0,0.08); padding-bottom: 16px; margin-bottom: 32px; display: flex; justify-content: space-between; align-items: end;}
.n-badge { background: #e5e7eb; color: #374151; padding: 4px 12px; border-radius: 99px; font-size: 12px; font-weight: 600; }

/* Custom Radio Navigation inside Sidebar */
div[role="radiogroup"] { gap: 4px; }
div[role="radiogroup"] > label {
    padding: 12px 16px;
    border-radius: 8px;
    cursor: pointer;
    transition: background 0.2s;
}
div[role="radiogroup"] > label:hover { background-color: rgba(56,161,105,0.15); }
div[role="radiogroup"] > label[data-checked="true"] {
    background-color: rgba(56,161,105,0.3) !important;
}
div[role="radiogroup"] > label > div:first-child { display: none; /* hide radio circle */ }
div[role="radiogroup"] > label span { font-weight: 600 !important; color: white !important; font-size: 15px;}

/* Buttons */
div.stButton > button[kind="primary"] {
    background-color: #1c6b42; color: #fff; border: none; border-radius: 12px;
    font-weight: 600; padding: 8px 16px; transition: all 0.3s; white-space: nowrap;
}
div.stButton > button[kind="primary"]:hover { background-color: #155235; color: #fff;}

div.stButton > button[kind="secondary"] {
    background-color: transparent; color: #6b7d72; border: 1px solid #dde4df; border-radius: 8px;
    font-weight: 600; padding: 6px 12px; font-size: 13px; transition: all 0.3s;
}
div.stButton > button[kind="secondary"]:hover { background-color: #f3f4f6; color: #0c2218;}

/* Cards */
.n-card {
    background: #fff; border-radius: 18px; border: 1px solid #dde4df;
    box-shadow: 0 4px 16px rgba(0,0,0,0.03); padding: 24px; margin-bottom: 24px;
    transition: all 0.3s;
}
.n-card:hover { border-color: #bbf7d0; box-shadow: 0 8px 24px rgba(0,0,0,0.06); }

/* Inventory Table */
.inv-table { width: 100%; border-collapse: collapse; font-size: 13px; text-align: left; }
.inv-table th { padding: 12px 16px; font-weight: 600; color: #6b7d72; text-transform: uppercase; font-size: 11px; letter-spacing: 0.05em; border-bottom: 1px solid #dde4df; }
.inv-table td { padding: 14px 16px; border-bottom: 1px solid #f0fdf4; color: #0c2218; font-weight: 500;}
.inv-row-warn { background-color: #fff9f9; }
.ns-badge { width: 28px; height: 28px; border-radius: 8px; display: inline-flex; align-items: center; justify-content: center; color: white; font-weight: 800; font-size: 14px; }
.co2-bar-bg { width: 56px; height: 5px; background: #e5e7eb; border-radius: 99px; overflow: hidden; display: inline-block; margin-right: 8px; vertical-align: middle;}
.co2-bar-fg { height: 100%; background: #1c6b42; }
.exp-pill { padding: 4px 10px; border-radius: 99px; font-size: 11px; font-weight: 700; display: inline-block; }
.dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block; margin-right: 10px; }

/* Layout & Alignment */
.section-title { font-size: 16px !important; font-weight: 700 !important; color: #0c2218 !important; margin: 0 0 16px 0 !important; letter-spacing: 0.02em; }

/* File Uploader */
[data-testid="stFileUploadDropzone"] {
    border: 2px dashed #c4cdc7; border-radius: 16px; background: #fff; transition: all 0.3s; padding: 24px;
}
[data-testid="stFileUploadDropzone"]:hover { border-color: #1c6b42; background: #f0fdf4; }

/* Recipe specific */
.rec-pill { display: inline-block; padding: 2px 10px; border-radius: 99px; font-size: 11px; font-weight: 600; margin: 2px; }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.markdown(logo_html, unsafe_allow_html=True)
    st.markdown("""
<div style="height:1px; background:linear-gradient(90deg, rgba(255,255,255,0.1), transparent); margin-bottom:20px;"></div>
""", unsafe_allow_html=True)
    
    co2 = "8.1" if st.session_state.scanned else "0.0"
    items = "10" if st.session_state.scanned else "0"
    exp = "3" if st.session_state.scanned else "0"
    
    st.markdown(f"""
<div style="background:rgba(56,161,105,0.1); border:1px solid rgba(56,161,105,0.3); border-radius:16px; padding:16px; margin-bottom:24px;">
<div style="display:flex; justify-content:space-between; text-align:center;">
<div><div style="color:#fff; font-size:20px; font-weight:800;">{co2}</div><div style="color:#5a9870; font-size:10px; font-weight:600;">KG CO₂e</div></div>
<div><div style="color:#fff; font-size:20px; font-weight:800;">{items}</div><div style="color:#5a9870; font-size:10px; font-weight:600;">ITEMS</div></div>
<div><div style="color:{'#ef4444' if st.session_state.scanned else '#fff'}; font-size:20px; font-weight:800;">{exp}</div><div style="color:#5a9870; font-size:10px; font-weight:600;">EXPIRING</div></div>
</div>
</div>
<div style="color:#3a7a55; font-size:11px; font-weight:700; letter-spacing:0.1em; margin-bottom:8px; margin-left:8px;">NAVIGATION</div>
""", unsafe_allow_html=True)
    
    view = st.radio("Navigation", ["📷 Smart Scanner", "🍳 Recipe Engine", "🛒 Local Market"], label_visibility="collapsed", key="nav_view")
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
<div style="background:rgba(56,161,105,0.1); border-radius:16px; padding:16px;">
<div style="display:flex; align-items:center; gap:10px; margin-bottom:12px;">
<div style="background:#1c6b42; width:36px; height:36px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:18px;">👤</div>
<div><div style="color:#fff; font-weight:600; font-size:14px;">Alex Chen</div><div style="background:#166534; color:#86efac; font-size:10px; padding:2px 8px; border-radius:99px; display:inline-block; font-weight:600; margin-top:2px;">Eco-Pro Plan</div></div>
</div>
<div style="height:6px; background:rgba(255,255,255,0.1); border-radius:99px; overflow:hidden; margin-bottom:6px;"><div style="height:100%; width:72%; background:#38a169;"></div></div>
<div style="display:flex; justify-content:space-between; font-size:11px;"><span style="color:#5a9870;">Goal progress</span><span style="color:#fff; font-weight:600;">72%</span></div>
</div>
""", unsafe_allow_html=True)

# --- HELPER FUNCS ---
def get_ns_col(ns):
    return {"A":"#1a8a3c", "B":"#78b12c", "C":"#e6a817", "D":"#f47b1e", "E":"#e73b2b"}.get(ns, "#78b12c")

def get_exp_style(days):
    if days <= 1: return "#ef4444", "#fef2f2", "#fecaca", "Today!"
    if days <= 2: return "#ef4444", "#fef2f2", "#fecaca", "2 days"
    if days <= 4: return "#ea580c", "#fff7ed", "#fed7aa", f"{days} days"
    return "#16a34a", "#f0fdf4", "#bbf7d0", f"{days} days"

# --- MAIN ---
if view == "📷 Smart Scanner":
    st.markdown("""
<div class="n-header-container">
<div>
<div class="n-section-label">Homepage</div>
<h1 class="n-h1">Smart Scanner</h1>
<div class="n-subtitle">Turn everyday ingredients into culinary magic while tracking your positive impact.</div>
</div>
</div>
""", unsafe_allow_html=True)

    # Top Metrics
    st.markdown("""
<div style="display:flex; gap:24px; margin-bottom:32px;">
    <div class="n-card" style="flex:1; margin-bottom:0; padding:20px; background:linear-gradient(135deg, #f0fdf4, #fff);">
        <div style="font-size:12px; color:#6b7d72; font-weight:700; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:8px;">💰 Savings (This Month)</div>
        <div style="font-size:28px; font-weight:800; color:#0c2218;">€42.50</div>
        <div style="font-size:12px; color:#15803d; font-weight:600; margin-top:4px;">↑ 12% vs last month</div>
    </div>
    <div class="n-card" style="flex:1; margin-bottom:0; padding:20px; background:linear-gradient(135deg, #f0fdf4, #fff);">
        <div style="font-size:12px; color:#6b7d72; font-weight:700; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:8px;">🌿 Carbon Prevented</div>
        <div style="font-size:28px; font-weight:800; color:#0c2218;">15.2 <span style="font-size:16px;">kg CO₂e</span></div>
        <div style="font-size:12px; color:#15803d; font-weight:600; margin-top:4px;">↑ 8% vs last month</div>
    </div>
    <div class="n-card" style="flex:1; margin-bottom:0; padding:20px; background:linear-gradient(135deg, #fff9f9, #fff);">
        <div style="font-size:12px; color:#6b7d72; font-weight:700; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:8px;">⚠️ Needs Attention</div>
        <div style="font-size:28px; font-weight:800; color:#ef4444;">3 <span style="font-size:16px;">Items</span></div>
        <div style="font-size:12px; color:#b91c1c; font-weight:600; margin-top:4px;">Expiring in &lt; 48h</div>
    </div>
</div>
    """, unsafe_allow_html=True)
    
    col_left, col_right = st.columns([1.5, 1], gap="large")
    
    with col_left:
        st.markdown('<div class="section-title">Current Inventory</div>', unsafe_allow_html=True)
        if not st.session_state.scanned:
            st.markdown("""
<p style="color:#6b7d72; font-size:14px; margin-bottom:16px;">Upload a photo of your fridge. Our computer vision AI will instantly detect your ingredients, their expiry dates, and carbon footprint.</p>
""", unsafe_allow_html=True)
            uploaded = st.file_uploader("📸 Drop your fridge photo here", label_visibility="visible")
            if uploaded:
                st.image(uploaded, width=400)
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🔍 Run Demo Scan", use_container_width=True, type="primary") or uploaded:
                with st.spinner("Analysing with computer vision · detecting items, expiry & nutrition..."):
                    time.sleep(2)
                    st.session_state.scanned = True
                    st.session_state.inventory = INVENTORY
                    st.rerun()
            
        else:
            st.markdown("""
<div style="background:#0c2218; color:#fff; padding:20px 24px; border-radius:16px; margin-bottom:24px; display:flex; align-items:center; gap:16px;">
<div style="font-size:28px;">✅</div>
<div>
<div style="font-size:16px; font-weight:700;">10 items detected · Ready for culinary magic ✨</div>
<div style="font-size:13px; color:#86efac; margin-top:4px;">3 items flagged as expiring within 48h · 8.1 kg CO₂e total footprint tracked</div>
</div>
</div>
""", unsafe_allow_html=True)
            
            # Build Table HTML
            rows = ""
            for item in sorted(st.session_state.inventory, key=lambda x: x["days"]):
                dot_col, pill_bg, pill_border, pill_lbl = get_exp_style(item["days"])
                row_class = "inv-row-warn" if item["days"] <= 2 else ""
                co2_pct = min(100, (item["co2"]/3.0)*100)
                ns_bg = get_ns_col(item["ns"])
                
                rows += f"""<tr class="{row_class}">
<td><span class="dot" style="background:{dot_col}"></span>{item['name']} <span style="color:#6b7d72; font-size:11px; margin-left:6px;">{item['qty']}</span></td>
<td><span style="background:#f3f4f6; padding:4px 10px; border-radius:8px; font-size:11px;">{item['cat']}</span></td>
<td><span class="exp-pill" style="background:{pill_bg}; color:{dot_col}; border:1px solid {pill_border};">{pill_lbl}</span></td>
<td><div class="co2-bar-bg"><div class="co2-bar-fg" style="width:{co2_pct}%"></div></div><span style="font-size:11px; color:#6b7d72; font-weight:600;">{item['co2']}kg</span></td>
<td><div class="ns-badge" style="background:{ns_bg};">{item['ns']}</div></td>
</tr>"""
            
            st.markdown(f"""
<div class="n-card" style="padding:0; overflow:hidden;">
<table class="inv-table">
<thead style="background:#fafaf8;">
<tr><th>Item</th><th>Category</th><th>Expires</th><th>CO₂ / item</th><th>Nutri-Score</th></tr>
</thead>
<tbody>{rows}</tbody>
</table>
</div>
""", unsafe_allow_html=True)
            def go_to_recipes():
                st.session_state.nav_view = "🍳 Recipe Engine"
                
            c1, c2, c3 = st.columns([1.5, 1.5, 1.5])
            with c1:
                if st.button("🔄 Scan Another", type="primary", use_container_width=True):
                    st.session_state.scanned = False
                    st.session_state.inventory = []
                    st.rerun()
            with c2:
                st.button("🍳 Cook with Nourri ✨", type="primary", use_container_width=True, on_click=go_to_recipes)

    with col_right:
        st.markdown('<div class="section-title">Previously Bought Items</div>', unsafe_allow_html=True)
        st.markdown("""
<div class="n-card" style="padding:16px;">
    <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #f3f4f6; padding-bottom:12px; margin-bottom:12px;">
        <div style="display:flex; align-items:center; gap:12px;">
            <div style="font-size:24px;">🥛</div>
            <div>
                <div style="font-weight:600; font-size:14px; color:#0c2218;">Organic Oat Milk</div>
                <div style="font-size:12px; color:#6b7d72;">Bought 4 days ago</div>
            </div>
        </div>
        <div style="background:#f0fdf4; color:#15803d; padding:6px 12px; border-radius:8px; font-size:12px; font-weight:700; cursor:pointer;">+ Add</div>
    </div>
    <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #f3f4f6; padding-bottom:12px; margin-bottom:12px;">
        <div style="display:flex; align-items:center; gap:12px;">
            <div style="font-size:24px;">🥚</div>
            <div>
                <div style="font-weight:600; font-size:14px; color:#0c2218;">Free-Range Eggs</div>
                <div style="font-size:12px; color:#6b7d72;">Bought 1 week ago</div>
            </div>
        </div>
        <div style="background:#f0fdf4; color:#15803d; padding:6px 12px; border-radius:8px; font-size:12px; font-weight:700; cursor:pointer;">+ Add</div>
    </div>
    <div style="display:flex; justify-content:space-between; align-items:center;">
        <div style="display:flex; align-items:center; gap:12px;">
            <div style="font-size:24px;">☕</div>
            <div>
                <div style="font-weight:600; font-size:14px; color:#0c2218;">Fairtrade Coffee Beans</div>
                <div style="font-size:12px; color:#6b7d72;">Bought 2 weeks ago</div>
            </div>
        </div>
        <div style="background:#f0fdf4; color:#15803d; padding:6px 12px; border-radius:8px; font-size:12px; font-weight:700; cursor:pointer;">+ Add</div>
    </div>
</div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="section-title" style="margin-top:24px;">Saved Recipes</div>', unsafe_allow_html=True)
        if len(st.session_state.favorites) == 0:
            st.markdown("""
<div class="n-card" style="padding:24px; text-align:center; color:#6b7d72;">
    <div style="font-size:32px; margin-bottom:8px;">🤍</div>
    <div style="font-size:14px; font-weight:500;">No recipes saved yet.</div>
    <div style="font-size:12px; margin-top:4px;">Head to the Recipe Engine to save your favorites!</div>
</div>
""", unsafe_allow_html=True)
        else:
            for fav_idx in st.session_state.favorites:
                fav_r = RECIPES[fav_idx]
                st.markdown(f"""
<div class="n-card" style="padding:16px; display:flex; align-items:center; gap:16px;">
    <div style="font-size:32px; background:#f0fdf4; width:56px; height:56px; border-radius:12px; display:flex; align-items:center; justify-content:center;">{fav_r['emoji']}</div>
    <div>
        <div style="font-weight:700; font-size:14px; color:#0c2218; line-height:1.2; margin-bottom:4px;">{fav_r['name']}</div>
        <div style="font-size:12px; color:#6b7d72;">⏱ {fav_r['time']} · 📉 {fav_r['co2']}kg CO₂e</div>
    </div>
</div>
""", unsafe_allow_html=True)

elif view == "🍳 Recipe Engine":
    st.markdown("""
<div class="n-header-container">
<div>
<div class="n-section-label">Recipe Engine</div>
<h1 class="n-h1">Nourri-Powered Recipes</h1>
<div class="n-subtitle">Delicious, zero-waste meals tailored to what you have right now.</div>
</div>
<div class="n-badge">✨ Nourri Smart Recipes</div>
</div>
""", unsafe_allow_html=True)
    
    cols = st.columns(3, gap="large")
    for idx, r in enumerate(RECIPES):
        total_items = len(r['inFridge']) + len(r['toOrder'])
        match_pct = (len(r['inFridge']) / total_items) * 100
        bar_col = "#16a34a" if match_pct >= 70 else "#f97316"
        ns_bg = get_ns_col(r['ns'])
        
        in_fridge_html = "".join([f'<span class="rec-pill" style="background:#dcfce7; color:#15803d;">✅ {x}</span>' for x in r['inFridge'][:2]])
        to_order_html = "".join([f'<span class="rec-pill" style="background:#f3f4f6; color:#9ca3af;">📦 {x}</span>' for x in r['toOrder'][:1]])
        extra_html = f'<span class="rec-pill" style="background:#fff7ed; color:#ea580c;">+{len(r["toOrder"])} needed</span>' if r['toOrder'] else ''

        with cols[idx]:
            # Custom HTML Card
            st.markdown(f"""
<div class="n-card" style="padding:0; overflow:hidden; height: 420px; display: flex; flex-direction: column;">
<div style="background: linear-gradient(135deg, #f0fdf4, #dcfce7); padding: 24px; display:flex; justify-content:space-between; align-items:start; flex-shrink: 0;">
<div style="font-size: 42px; line-height:1;">{r['emoji']}</div>
<div class="ns-badge" style="background:{ns_bg};">{r['ns']}</div>
</div>
<div style="padding: 20px 24px; display: flex; flex-direction: column; flex-grow: 1;">
<h3 style="margin: 0 0 12px 0; font-size:18px; font-weight:700; color:#0c2218; line-height:1.3;">{r['name']}</h3>
<div style="display:flex; gap:12px; font-size:12px; color:#6b7d72; font-weight:600; margin-bottom:16px;">
<span>⏱ {r['time']}</span><span>👤 {r['serves']}</span><span>📊 {r['diff']}</span>
</div>
<div>
<div style="background:#dcfce7; color:#15803d; padding:6px 12px; border-radius:99px; font-size:12px; font-weight:700; display:inline-block; margin-bottom:16px;">
📉 Saves {r['co2']} kg CO₂e
</div>
</div>
<div style="margin-bottom:16px;">
<div style="display:flex; justify-content:space-between; font-size:11px; font-weight:600; color:#6b7d72; margin-bottom:6px;">
<span>Match</span> <span style="color:{bar_col}">{len(r['inFridge'])}/{total_items} items in fridge</span>
</div>
<div style="height:6px; background:#e5e7eb; border-radius:99px; overflow:hidden;">
<div style="height:100%; width:{match_pct}%; background:{bar_col};"></div>
</div>
</div>
<div style="display:flex; flex-wrap:wrap; gap:6px; margin-top: auto;">
{in_fridge_html}{to_order_html}{extra_html}
</div>
</div>
</div>
""", unsafe_allow_html=True)
            
            btn_c1, btn_c2 = st.columns([1, 1])
            with btn_c1:
                btn_label = "✕ Close" if st.session_state.selected_recipe == idx else "View Recipe"
                if st.button(btn_label, key=f"btn_{idx}", use_container_width=True, type="primary"):
                    st.session_state.selected_recipe = None if st.session_state.selected_recipe == idx else idx
                    st.rerun()
            with btn_c2:
                is_fav = idx in st.session_state.favorites
                fav_label = "❤️ Saved" if is_fav else "🤍 Favorite"
                # If using primary color for active heart
                if st.button(fav_label, key=f"fav_{idx}", use_container_width=True, type="primary" if is_fav else "secondary"):
                    if is_fav:
                        st.session_state.favorites.remove(idx)
                    else:
                        st.session_state.favorites.add(idx)
                    st.rerun()

    if st.session_state.selected_recipe is not None:
        r = RECIPES[st.session_state.selected_recipe]
        st.markdown(f"""
<div class="n-card" style="padding:24px; display:flex; align-items:start; gap:16px; background:linear-gradient(135deg, #f0fdf4, #fff); border-left: 4px solid #1c6b42; border-radius: 12px; margin-top: 24px; margin-bottom: 24px;">
    <div style="font-size:24px; margin-top:-4px;">✨</div>
    <div>
        <div style="font-size:12px; font-weight:800; color:#1c6b42; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:6px;">Nourri Insight</div>
        <div style="color:#0c2218; font-size:14px; line-height:1.6; font-weight:500;">{r['aiNote']}</div>
    </div>
</div>
""", unsafe_allow_html=True)
        
        c1, c2 = st.columns([1, 1.5], gap="large")
        with c1:
            html_c1 = '<div class="section-title">Ingredients</div><div class="n-card" style="padding:0; overflow:hidden;">'
            for item in r['inFridge']:
                html_c1 += f"""
<div style="display:flex; justify-content:space-between; align-items:center; padding:16px; border-bottom:1px solid #f3f4f6;">
    <div style="display:flex; align-items:center; gap:12px;">
        <div style="width:16px; height:16px; border-radius:50%; background:#dcfce7; display:flex; align-items:center; justify-content:center;"><div style="width:6px; height:6px; background:#16a34a; border-radius:50%;"></div></div>
        <span style="font-weight:600; font-size:14px; color:#0c2218;">{item}</span>
    </div>
    <span style="font-size:11px; font-weight:600; color:#6b7d72;">In Fridge</span>
</div>
"""
            for item in r['toOrder']:
                html_c1 += f"""
<div style="display:flex; justify-content:space-between; align-items:center; padding:16px; border-bottom:1px solid #f3f4f6; background:#fffdfa;">
    <div style="display:flex; align-items:center; gap:12px;">
        <div style="width:16px; height:16px; border-radius:50%; background:#ffedd5; display:flex; align-items:center; justify-content:center;"><div style="width:6px; height:6px; background:#ea580c; border-radius:50%;"></div></div>
        <span style="font-weight:600; font-size:14px; color:#0c2218;">{item}</span>
    </div>
    <span style="font-size:10px; font-weight:800; color:#ea580c; background:#fff7ed; padding:4px 8px; border-radius:99px; text-transform:uppercase; letter-spacing:0.05em;">To Order</span>
</div>
"""
            html_c1 += '</div>'
            st.markdown(html_c1, unsafe_allow_html=True)
            
            if len(r['toOrder']) > 0:
                summary_key = f"show_order_summary_{st.session_state.selected_recipe}"
                placed_key = f"order_placed_{st.session_state.selected_recipe}"
                
                if st.session_state.get(placed_key, False):
                    st.success("✅ Order placed! Delivery by 14:45")
                elif st.session_state.get(summary_key, False):
                    # Build summary table HTML
                    total_cost = 0.0
                    rows_html = ""
                    for item in r['toOrder']:
                        price = 3.20 # Mock price
                        total_cost += price
                        rows_html += f"""
<tr style="border-bottom:1px solid #f9f9f9;">
<td style="padding:8px 0; color:#0c2218;">{item}</td>
<td style="padding:8px 0; color:#0c2218; text-align:right;">€{price:.2f}</td>
</tr>
"""
                    summary_html = f"""
<div class="n-card" style="padding:16px; margin-bottom:16px; border:1px solid #dde4df; border-radius:12px; background:#fff;">
<h4 style="margin:0 0 4px 0; color:#0c2218; font-size:16px;">Order Summary</h4>
<p style="font-size:13px; color:#6b7d72; margin:0 0 16px 0;">Ordering from <strong style="color:#1c6b42;">Radicle Urban Farms</strong></p>
<table style="width:100%; font-size:14px; text-align:left; border-collapse:collapse; margin-bottom:4px;">
<tr style="border-bottom:1px solid #eee;">
<th style="padding:8px 0; color:#0c2218; font-weight:600;">Item</th>
<th style="padding:8px 0; color:#0c2218; font-weight:600; text-align:right;">Est. Cost</th>
</tr>
{rows_html}
<tr>
<td style="padding:12px 0 4px 0; font-weight:800; color:#0c2218; font-size:15px;">Total</td>
<td style="padding:12px 0 4px 0; font-weight:800; color:#0c2218; text-align:right; font-size:15px;">€{total_cost:.2f}</td>
</tr>
</table>
</div>
"""
                    st.markdown(summary_html, unsafe_allow_html=True)

                    col_conf1, col_conf2 = st.columns(2)
                    with col_conf1:
                        if st.button("Go Back", type="secondary", use_container_width=True):
                            st.session_state[summary_key] = False
                            st.rerun()
                    with col_conf2:
                        if st.button("Confirm Order", type="primary", use_container_width=True):
                            st.session_state[placed_key] = True
                            st.session_state[summary_key] = False
                            st.rerun()
                else:
                    if st.button("🛒 Order Missing Ingredients", use_container_width=True, type="primary"):
                        st.session_state[summary_key] = True
                        st.session_state[placed_key] = False
                        st.rerun()
        with c2:
            html_c2 = '<div class="section-title">Preparation Steps</div><div class="n-card" style="padding:24px;">'
            for i, step in enumerate(r['steps']):
                border_style = "border-bottom:1px solid #f8fafc;" if i < len(r['steps']) - 1 else ""
                html_c2 += f"""
<div style="display:flex; gap:20px; margin-bottom:{'20px' if i < len(r['steps']) - 1 else '0'}; position:relative;">
    <div style="font-size:16px; font-weight:800; color:#cbd5e1; min-width:24px; text-align:right;">0{i+1}</div>
    <div style="font-size:15px; color:#0c2218; line-height:1.6; font-weight:500; flex:1; padding-bottom:{'20px' if i < len(r['steps']) - 1 else '0'}; {border_style}">{step}</div>
</div>
"""
            html_c2 += '</div>'
            st.markdown(html_c2, unsafe_allow_html=True)

elif view == "🛒 Local Market":
    st.markdown("""
<div class="n-header-container">
<div>
<div class="n-section-label">Local Market</div>
<h1 class="n-h1">Nourri Smart Restock</h1>
<div class="n-subtitle">Seamlessly replenish your kitchen with fresh, local ingredients before you run out.</div>
</div>
<div class="n-badge">🌿 Nourri Auto-Pilot</div>
</div>
""", unsafe_allow_html=True)
    
    # Auto Mode Toggle
    auto_bg = "linear-gradient(135deg, #f0fdf4, #dcfce7)" if st.session_state.auto_mode else "linear-gradient(135deg, #fff, #fafaf8)"
    auto_border = "#86efac" if st.session_state.auto_mode else "#dde4df"
    auto_text = "Your Kitchen is on Autopilot mode. Nourri will periodically check inventory and order from local markets when stocks run low. Don't worry, you'll be notified for order sizes exceeding your configured limit, these will be placed only on approval." if st.session_state.auto_mode else "Turn on Auto-Pilot to let Nourri automatically order essentials from local farms when stock runs low."
    auto_col = "#15803d" if st.session_state.auto_mode else "#6b7d72"
    auto_title = "#0c2218"
    icon = "✨" if st.session_state.auto_mode else "⚡"
    
    st.markdown(f"""
<div class="n-card" style="background:{auto_bg}; border: 1px solid {auto_border}; padding: 24px 24px 16px 24px; margin-bottom: 8px;">
<div style="display:flex; align-items:start; gap:16px;">
    <div style="font-size:28px; line-height:1;">{icon}</div>
    <div>
        <h3 style="margin:0 0 8px 0; color:{auto_title}; font-size:18px; font-weight:700;">Nourri Auto-Pilot</h3>
        <p style="margin:0; color:{auto_col}; font-weight:500; font-size:14px; line-height:1.5;">{auto_text}</p>
    </div>
</div>
</div>
""", unsafe_allow_html=True)
    
    st.toggle("Enable Nourri Auto-Pilot", key="auto_mode")
    
    if False:
        # Smart Basket
        st.markdown("""
<div class="n-card" style="background:#fff; border-top: 4px solid #1c6b42;">
<h4 style="margin:0 0 20px 0; color:#0c2218; font-size:16px;">🛒 Your Curated Basket</h4>
<div style="background:#fafaf8; border:1px solid #e5e7eb; border-radius:12px; padding:16px;">
<div style="display:flex; justify-content:space-between; margin-bottom:12px; font-size:14px; color:#0c2218; font-weight:500;">
<span>🥬 Baby Spinach 300g <span style="color:#6b7d72; font-size:12px; margin-left:8px;">Radicle Urban Farms</span></span> <b>€2.80</b>
</div>
<div style="display:flex; justify-content:space-between; margin-bottom:12px; font-size:14px; color:#0c2218; font-weight:500;">
<span>🥛 Oat Milk 2×1L <span style="color:#6b7d72; font-size:12px; margin-left:8px;">Radicle Urban Farms</span></span> <b>€3.80</b>
</div>
<div style="display:flex; justify-content:space-between; padding-bottom:16px; border-bottom:1px solid #e5e7eb; font-size:14px; color:#0c2218; font-weight:500;">
<span>🥚 Free-Range Eggs 12-pack <span style="color:#6b7d72; font-size:12px; margin-left:8px;">Green Valley Cooperative</span></span> <b>€4.20</b>
</div>
<div style="display:flex; justify-content:space-between; margin-top:16px; align-items:center;">
<span style="font-size:13px; color:#15803d; font-weight:600;">3 items · 2 local farms · saves 2.6 kg CO₂e</span>
<span style="font-size:18px; font-weight:800; color:#0c2218;">Total: €10.80</span>
</div>
</div>
</div>
""", unsafe_allow_html=True)
        
        # Agent Trace Panel
        st.markdown("""
<div class="n-card" style="padding:0; overflow:hidden;">
<div style="padding:20px; border-bottom:1px solid #dde4df; display:flex; justify-content:space-between; align-items:center; background:#fafaf8;">
<h3 style="margin:0; font-size:16px; color:#0c2218; font-weight:700;">How Nourri Decides</h3>
<span class="n-badge" style="background:#dcfce7; color:#15803d;">Auto-Pilot Active</span>
</div>
<div style="padding:24px;" id="agent-container">
""", unsafe_allow_html=True)
        
        if st.button("✨ Let Nourri Handle It", disabled=st.session_state.agent_done, type="primary"):
            placeholders = [st.empty() for _ in range(5)]
            audit_placeholder = st.empty()
            
            for idx, step in enumerate(AGENT_STEPS):
                time.sleep(step['delay'])
                with placeholders[idx]:
                    if step.get('guardrails'):
                        st.markdown(f"""
<div style="margin-bottom:24px;">
<div style="font-weight:700; font-size:13px; color:#0c2218; margin-bottom:12px;">{step['label']}</div>
<div style="background:#f0fdf4; border:1px solid #86efac; padding:10px 14px; border-radius:8px; margin-bottom:6px; font-size:12px; color:#15803d; font-weight:600;">✅ Budget check — €10.80 < €20.00 → auto-approval eligible</div>
<div style="background:#f0fdf4; border:1px solid #86efac; padding:10px 14px; border-radius:8px; margin-bottom:6px; font-size:12px; color:#15803d; font-weight:600;">✅ Allergen scan — No conflict with user profile</div>
<div style="background:#f0fdf4; border:1px solid #86efac; padding:10px 14px; border-radius:8px; margin-bottom:6px; font-size:12px; color:#15803d; font-weight:600;">✅ Partner trust gate — Radicle (4.8★) · Green Valley (4.9★) verified</div>
<div style="background:#fff7ed; border:1px solid #fed7aa; padding:10px 14px; border-radius:8px; margin-bottom:6px; font-size:12px; color:#c2410c; font-weight:700;">⚠️ HITL GATE — €10.80 below €20 threshold → proceeding autonomously</div>
<div style="background:#f0fdf4; border:1px solid #86efac; padding:10px 14px; border-radius:8px; font-size:12px; color:#15803d; font-weight:600;">✅ Carbon gate — local sourcing saves 2.6 kg CO₂e → within policy</div>
</div>
""", unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
<div style="margin-bottom:24px;">
<div style="font-weight:700; font-size:13px; color:#0c2218; margin-bottom:8px;">{step['label']}</div>
<div style="background:#0c2218; color:#86efac; padding:12px; border-radius:8px; font-family:monospace; font-size:11.5px; white-space:pre-wrap; margin-bottom:4px;">→ {step['call']}</div>
<div style="background:#f0fdf4; border:1px solid #bbf7d0; color:#166534; padding:12px; border-radius:8px; font-family:monospace; font-size:11px; margin-bottom:8px;">← {step['response']}</div>
<div style="font-size:13px; font-weight:600; color:#0c2218;">{step['insight']}</div>
</div>
""", unsafe_allow_html=True)
            
            st.session_state.agent_done = True
            
            with audit_placeholder:
                st.markdown("""
<div style="background:#0c2218; color:#86efac; padding:20px; border-radius:16px; font-family:monospace; font-size:11px; margin-top:16px;">
2026-06-17T12:32:11Z  agent=nourri-replenishment-v1.2  task=auto_reorder
tool_calls=3  guardrails_checked=5  guardrails_passed=5
hitl_required=false  items_ordered=3  total=€10.80  co2_saved=2.6kg
confidence=0.94  order_id=NR-20260617-0891  status=COMPLETED  duration=6.1s
── RESPONSIBLE AI METRICS ─────────────────────────────────────────
[ROBUSTNESS]  adversarial_pass_rate=87%  edge_case_pass_rate=94%
[BIAS]        max_disparity_across_segments=3.8pp  threshold=10pp  ✅ PASS
[CARBON]      tokens_per_run=4,847  energy=0.0015 kWh  co2eq=0.090 gCO₂eq
[EXPLAINABILITY] trace_completeness=100%  user_explanation=clear (10/10)
</div>
<div style="background:linear-gradient(135deg, #1c6b42, #155235); padding:16px; border-radius:12px; margin-top:20px; color:white; font-weight:600; font-size:14px; text-align:center; box-shadow:0 4px 12px rgba(28,107,66,0.2);">
🎉 Order processed successfully · Ref NR-20260617-0891 confirmed · Delivery by 14:45
</div>
<div style="background: linear-gradient(135deg, #0c2218, #1c6b42); color: white; text-align: center; padding: 32px; border-radius: 20px; margin-top: 24px;">
    <div style="color: #86efac; font-size: 11px; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 8px;">Done in 6 seconds ✨</div>
    <div style="font-size: 26px; font-weight: 800;">€10.80 restocked · 2.6 kg CO₂e prevented</div>
    <div style="color: #86efac; font-size: 13px; margin-top: 8px;">Nourri ordered from 2 local farms — no action needed from you</div>
    <div style="display: flex; justify-content: center; gap: 12px; margin-top: 20px;">
        <span style="background: rgba(255,255,255,0.15); border-radius: 99px; padding: 6px 14px; font-size: 12px; font-weight: 600;">✅ All safety checks passed</span>
        <span style="background: rgba(255,255,255,0.15); border-radius: 99px; padding: 6px 14px; font-size: 12px; font-weight: 600;">🌿 Sourced locally</span>
        <span style="background: rgba(255,255,255,0.15); border-radius: 99px; padding: 6px 14px; font-size: 12px; font-weight: 600;">⚡ Fully autonomous</span>
    </div>
</div>
""", unsafe_allow_html=True)
                
            if st.button("↺ Run Again", type="secondary"):
                st.session_state.agent_done = False
                st.rerun()
                
        st.markdown("</div></div>", unsafe_allow_html=True) # Close agent container & card
        
    # Partners Grid
    st.markdown('<div class="section-title" style="margin-top:32px;">Our Local Farm Partners</div>', unsafe_allow_html=True)
    cols = st.columns(2, gap="large")
    partners = [
        ("🏙️", "Radicle Urban Farms", "4km", "Zero-Pesticide", "4.8★", "1.8kg"),
        ("🌾", "Green Valley Cooperative", "12km", "Certified Organic", "4.9★", "0.8kg"),
        ("🐄", "Sunrise Dairy Co-op", "18km", "Biodynamic", "4.7★", "2.1kg"),
        ("🍄", "Forest Edge Mushroom Lab", "7km", "Artisan Craft", "5.0★", "0.4kg")
    ]
    for idx, p in enumerate(partners):
        with cols[idx%2]:
            st.markdown(f"""
<div class="n-card" style="display:flex; align-items:center; gap:16px;">
<div style="font-size:36px; background:#f0fdf4; border-radius:50%; width:64px; height:64px; display:flex; align-items:center; justify-content:center; flex-shrink:0;">{p[0]}</div>
<div style="flex:1;">
<h4 style="margin:0 0 4px 0; color:#0c2218; font-size:15px; font-weight:700;">{p[1]}</h4>
<div style="font-size:12px; color:#6b7d72; font-weight:500; margin-bottom:8px;">{p[2]} · {p[4]}</div>
<div style="display:flex; justify-content:space-between; align-items:center;">
<span style="background:#dcfce7; color:#15803d; padding:4px 8px; border-radius:6px; font-size:10px; font-weight:700; text-transform:uppercase; letter-spacing:0.05em;">{p[3]}</span>
<span style="font-size:11px; font-weight:600; color:#1c6b42;">🌿 saves {p[5]} CO₂e</span>
</div>
</div>
</div>
""", unsafe_allow_html=True)
