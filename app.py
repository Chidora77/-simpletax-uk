import streamlit as st
import pandas as pd
from datetime import datetime
from PIL import Image
import os

st.set_page_config(page_title="SimpleTax UK", page_icon="🧾", layout="centered")

# BLUE AND ASH THEME - Professional accountant look
st.markdown("""
<style>
/* BLUE AND ASH COLOUR PALETTE */
:root {
    --blue-primary: #1e40af;
    --blue-light: #3b82f6;
    --blue-dark: #1e3a8a;
    --ash-light: #f8fafc;
    --ash-medium: #e2e8f0;
    --ash-dark: #64748b;
    --ash-text: #334155;
}

/* Main background - ash light */
.block-container {
    padding-top: 2.5rem !important; 
    padding-bottom: 1rem;
    background-color: #f8fafc;
}

/* Title - BLUE */
h1 {
    font-size: 1.8rem !important; 
    line-height: 1.3 !important; 
    overflow: visible !important;
    color: #1e40af !important;
    font-weight: 800 !important;
}

/* Subheaders - Blue dark */
h2, h3 {
    color: #1e3a8a !important;
    font-weight: 700 !important;
}

/* Tabs - Blue active, ash inactive */
.stTabs [data-baseweb="tab-list"] {
    background-color: #e2e8f0;
    border-radius: 8px;
    padding: 4px;
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    font-size: 0.85rem !important;
    color: #64748b !important;
    border-radius: 6px;
}
.stTabs [aria-selected="true"] {
    background-color: #1e40af !important;
    color: white !important;
    font-weight: 600 !important;
}

/* Buttons - BLUE primary */
.stButton button {
    background-color: #1e40af !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}
.stButton button:hover {
    background-color: #1e3a8a !important;
}

/* Primary button - even stronger blue */
.stButton button[kind="primary"] {
    background-color: #2563eb !important;
    box-shadow: 0 2px 8px rgba(37, 99, 235, 0.3) !important;
}

/* Download buttons - blue outline */
.stDownloadButton button {
    background-color: white !important;
    color: #1e40af !important;
    border: 2px solid #1e40af !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}
.stDownloadButton button:hover {
    background-color: #1e40af !important;
    color: white !important;
}

/* Metrics - ash card with blue accent */
[data-testid="stMetric"] {
    background-color: white !important;
    border: 1px solid #e2e8f0 !important;
    border-left: 4px solid #1e40af !important;
    border-radius: 8px !important;
    padding: 8px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important;
}
[data-testid="stMetricValue"] {
    font-size: 1.15rem !important;
    color: #1e3a8a !important;
    font-weight: 800 !important;
}
[data-testid="stMetricLabel"] {
    font-size: 0.7rem !important;
    color: #64748b !important;
    text-transform: uppercase !important;
    letter-spacing: 0.5px !important;
}

/* Inputs - ash border, blue focus */
.stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
    border: 1.5px solid #cbd5e1 !important;
    border-radius: 8px !important;
    background-color: white !important;
}
.stTextInput input:focus, .stNumberInput input:focus {
    border-color: #3b82f6 !important;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
}

/* File uploader - blue and ash */
[data-testid="stFileUploader"] {
    background-color: white !important;
    border: 2px dashed #94a3b8 !important;
    border-radius: 12px !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: #3b82f6 !important;
    background-color: #f0f7ff !important;
}

/* Expanders - ash header blue icon */
.streamlit-expanderHeader {
    background-color: white !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 8px !important;
    color: #1e3a8a !important;
    font-weight: 600 !important;
}

/* Success/info - blue tint */
.stAlert {
    border-radius: 8px !important;
}

/* Dataframe - ash header */
[data-testid="stDataFrame"] {
    border: 1px solid #e2e8f0 !important;
    border-radius: 8px !important;
}

/* Popover - white with blue accent */
[data-testid="stPopover"] {
    border: 1px solid #e2e8f0 !important;
}

/* Caption - ash dark */
.stCaption {
    color: #64748b !important;
}
</style>
""", unsafe_allow_html=True)

if "upload_counter" not in st.session_state:
    st.session_state.upload_counter = 0
if "last_saved" not in st.session_state:
    st.session_state.last_saved = None
if "zoomed" not in st.session_state:
    st.session_state.zoomed = {}
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "quarter_income" not in st.session_state:
    st.session_state.quarter_income = 0

# --- USER LOGIN - Each person sees ONLY his own receipts ---
if not st.session_state.user_id:
    st.title("🧾 SimpleTax UK")
    st.markdown("### 👋 Welcome - Private Receipts")
    st.info("🔒 Each user sees ONLY his own receipts. Others cannot see yours.")
    user_code = st.text_input("Enter your private code / phone number / business name", placeholder="e.g. 07700 123456 or Monsoon Foods")
    st.caption("This code creates your private space. Remember it to login again.")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔓 Login / Create Private Space", type="primary", use_container_width=True):
            if user_code.strip():
                # Clean code to safe filename
                safe = "".join(c for c in user_code if c.isalnum() or c in ("-","_")).strip()[:30]
                if not safe:
                    safe = user_code.strip().replace(" ","_")[:30]
                st.session_state.user_id = safe
                st.rerun()
            else:
                st.error("Please enter a code")
    with col2:
        st.caption("No password needed - your code is your private key")
    st.stop()

# Set per-user files
DB_FILE = f"receipts_{st.session_state.user_id}.csv"
UPLOAD_DIR = f"receipt_images_{st.session_state.user_id}"
os.makedirs(UPLOAD_DIR, exist_ok=True)
if not os.path.exists(DB_FILE):
    pd.DataFrame(columns=["date","shop","total","category","filename","image_path","created_at"]).to_csv(DB_FILE, index=False)
else:
    # Ensure old file structure works
    pass


if "upload_counter" not in st.session_state:
    st.session_state.upload_counter = 0
if "last_saved" not in st.session_state:
    st.session_state.last_saved = None
if "zoomed" not in st.session_state:
    st.session_state.zoomed = {}

def load_receipts():
    try:
        return pd.read_csv(DB_FILE)
    except:
        return pd.DataFrame(columns=["date","shop","total","category","filename","image_path","created_at"])

def save_receipt(shop, date, total, category, filename, image_path=""):
    df = load_receipts()
    new_row = pd.DataFrame([{
        "date": date, "shop": shop, "total": float(total), "category": category,
        "filename": filename, "image_path": image_path,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
    }])
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(DB_FILE, index=False)

def calc_tax_full(quarter_profit):
    annual = quarter_profit * 4
    taxable = max(0, annual - 12570)
    basic = min(taxable, 37700) * 0.20
    higher = max(0, taxable - 37700) * 0.40
    ni = 0
    if annual > 12570:
        ni += (min(annual, 50270) - 12570) * 0.06
        if annual > 50270:
            ni += (annual - 50270) * 0.02
    class2 = 179.40 if annual > 12570 else 0
    total_annual = basic + higher + ni + class2
    return annual, taxable, basic, higher, ni, class2, total_annual, total_annual/4

col_title, col_logout = st.columns([4,1])
with col_title:
    st.title("🧾 SimpleTax UK")
    st.caption(f"UK Making Tax Digital • Private: {st.session_state.user_id}")
with col_logout:
    if st.button("Logout"):
        st.session_state.user_id = None
        st.rerun()

tab_add, tab_list, tab_dash, tab_send = st.tabs(["📸 Add", "📋 List", "📊 Dashboard", "📧 Accountant"])

with tab_add:
    st.subheader("Add Receipt")
    st.caption("📱 On phone: Use Camera for instant capture")
    
    st.markdown("""
    <style>
    [data-testid="stFileUploader"] {min-height: 120px !important; padding: 10px !important;}
    [data-testid="stFileUploader"] button {min-height: 50px !important; font-size: 1.1rem !important;}
    [data-testid="stFileUploaderDropzone"] {min-height: 100px !important; padding: 20px !important;}
    </style>
    """, unsafe_allow_html=True)
    
    uploader_key = f"uploader_{st.session_state.upload_counter}"
    # Two options
    tab_browse, tab_cam = st.tabs(["📁 Browse", "📷 Camera"])
    uploaded = None
    with tab_browse:
        uploaded_file = st.file_uploader("Pick receipt from phone", type=["jpg","jpeg","png","heic"], key=uploader_key, label_visibility="collapsed")
        if uploaded_file:
            uploaded = uploaded_file
    with tab_cam:
        camera_file = st.camera_input("Take photo of receipt", key=f"cam_{st.session_state.upload_counter}", label_visibility="collapsed")
        if camera_file:
            uploaded = camera_file
            st.success("✅ Photo captured!")
    
    if st.session_state.last_saved:
        st.success(f"✅ {st.session_state.last_saved['shop']} £{st.session_state.last_saved['total']}")
        st.session_state.last_saved = None
    
    if uploaded:
        # Handle filename and save
        try:
            orig_name = uploaded.name
        except:
            orig_name = f"receipt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        
        safe_name = "".join(c for c in orig_name if c.isalnum() or c in (".","_","-"))[:50]
        if not safe_name.lower().endswith(('.jpg','.jpeg','.png','.heic')):
            safe_name += ".jpg"
        
        image_path_saved = os.path.join(UPLOAD_DIR, f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{safe_name}")
        
        # Save file - works for both file_uploader and camera_input
        try:
            file_data = uploaded.getvalue()
        except:
            try:
                file_data = uploaded.getbuffer()
            except:
                file_data = None
        
        if file_data:
            with open(image_path_saved, "wb") as out:
                out.write(file_data)
        
        # Show preview
        try:
            from PIL import Image
            preview_img = Image.open(image_path_saved)
            st.image(preview_img, width=300, caption="Receipt to save")
        except:
            st.write("📷 Image ready")
        
        with st.form("add_form"):
            c1, c2 = st.columns(2)
            shop = c1.text_input("Supplier / Description", "Monsoon Foods")
            total = c2.number_input("Total £", value=49.84, step=0.01)
            date = st.text_input("Date", datetime.now().strftime("%Y-%m-%d"))
            cat = st.selectbox("HMRC Category", ["Cost of goods sold","Tools","Travel","Materials","Office costs","Fuel","Other"])
            if st.form_submit_button("💾 SAVE & NEXT", type="primary", use_container_width=True):
                save_receipt(shop, date, total, cat, safe_name, image_path_saved)
                st.session_state.last_saved = {"shop": shop, "total": total}
                st.session_state.upload_counter += 1
                st.rerun()


with tab_list:
    st.subheader("Receipts")
    df = load_receipts()
    if df.empty:
        st.info("No receipts yet")
    else:
        st.caption(f"{len(df)} receipts • £{df['total'].sum():.2f} total")
        for idx in df.index[::-1]:
            row = df.loc[idx]
            c1, c2, c3, c4 = st.columns([1,4,2,2])
            with c1:
                if row.get("image_path") and os.path.exists(str(row["image_path"])):
                    try:
                        img = Image.open(row["image_path"])
                        img.thumbnail((40,40))
                        st.image(img, width=40)
                    except:
                        st.write("🧾")
            with c2:
                st.write(f"**{str(row['shop'])[:18]}**")
            with c3:
                st.write(f"**£{float(row['total']):.2f}**")
            with c4:
                with st.popover("View"):
                    st.write(f"**{row['shop']}** £{float(row['total']):.2f}")
                    if row.get("image_path") and os.path.exists(str(row["image_path"])):
                        full = Image.open(row["image_path"])
                        key = f"zoom_{idx}"
                        zoomed = st.session_state.zoomed.get(key, False)
                        if not zoomed:
                            st.image(full, width=150)
                            if st.button("🔍 Zoom", key=f"zb_{idx}", use_container_width=True):
                                st.session_state.zoomed[key]=True
                                st.rerun()
                        else:
                            st.image(full, width=300)
                            if st.button("Shrink", key=f"sh_{idx}", use_container_width=True):
                                st.session_state.zoomed[key]=False
                                st.rerun()
                    if st.button("🗑️ DELETE", key=f"del_{idx}", type="primary", use_container_width=True):
                        try:
                            if row.get("image_path") and os.path.exists(str(row["image_path"])):
                                os.remove(row["image_path"])
                        except:
                            pass
                        df.drop(idx).to_csv(DB_FILE, index=False)
                        st.rerun()

with tab_dash:
    st.subheader("Dashboard")
    df = load_receipts()
    total_exp = df["total"].sum() if not df.empty else 0.0
        quarter_income = st.number_input("Income this quarter £", value=st.session_state.quarter_income, min_value=0, step=100, key="dash_income")
    st.session_state.quarter_income = quarter_income
    quarter_profit = quarter_income - total_exp
    c1, c2, c3 = st.columns(3)
    c1.metric("Expenses", f"£{total_exp:.2f}")
    c2.metric("Profit Q", f"£{quarter_profit:.2f}")
    if quarter_income>0:
        annual, taxable, basic, higher, ni, class2, total_annual, total_q = calc_tax_full(quarter_profit)
        c3.metric("Tax Q", f"£{total_q:.2f}")
        st.success(f"Annual £{annual:.0f} | Tax £{total_annual:.0f}/yr = £{total_q:.0f}/qtr")
        with st.expander("📖 Full HMRC breakdown"):
            st.markdown(f"Annual £{annual:.2f} | Taxable £{taxable:.2f} | Income Tax £{basic+higher:.2f} | NI £{ni+class2:.2f} | **Total £{total_annual:.2f}/yr**")
    else:
        c3.metric("Tax Q", "£0")
    if not df.empty:
        st.bar_chart(df.groupby("category")["total"].sum(), height=150)
        display_df = df.rename(columns={"shop": "Supplier / Description", "date": "Date", "total": "Total £", "category": "HMRC Category"})
        st.dataframe(display_df[["Date","Supplier / Description","Total £","HMRC Category"]], width='stretch', height=200)
        export_df = df.rename(columns={"shop": "Supplier_Description", "date": "Date", "total": "Total", "category": "HMRC_Category"})
        csv = export_df.to_csv(index=False).encode()
        st.download_button("📥 Download CSV", csv, "UK-MTD.csv", "text/csv", use_container_width=True)

with tab_send:
    st.subheader("Send to Accountant")
    df = load_receipts()
    if df.empty:
        st.info("Add receipts first")
    else:
        total_exp = df["total"].sum()
        st.metric("Ready to send", f"{len(df)} receipts", f"£{total_exp:.2f}")
        st.divider()
        your_name = st.text_input("Your name", "Demo User")
        your_business = st.text_input("Business name", "Monsoon Foods")
        accountant_email = st.text_input("Accountant email", "accountant@example.com")
        # DYNAMIC - uses income from Dashboard automatically
        quarter_income = st.session_state.quarter_income
        st.info(f"💷 Income from Dashboard: £{quarter_income:.2f} (change it in Dashboard tab if needed)")
        if quarter_income == 0:
            st.warning("⚠️ Set your income in Dashboard tab first!")
        quarter_profit = quarter_income - total_exp
        annual, taxable, basic, higher, ni, class2, total_annual, total_q = calc_tax_full(quarter_profit) if quarter_income>0 else (0,0,0,0,0,0,0,0)
        summary_text = f"""Business: {your_business}
Period: {datetime.now().strftime('%B %Y')}
Expenses: £{total_exp:.2f} in {len(df)} receipts
Income: £{quarter_income:.2f}
Profit: £{quarter_profit:.2f}
Tax: £{total_q:.2f}/qtr

Thanks,
{your_name}
Generated by SimpleTax UK
"""
        st.text_area("Email preview", summary_text, height=150)
        export_df = df.rename(columns={"shop": "Supplier_Description"})
        csv_bytes = export_df.to_csv(index=False).encode()
        col1, col2 = st.columns(2)
        with col1:
            st.download_button("📥 Download CSV", csv_bytes, "MTD-receipts.csv", "text/csv", use_container_width=True)
        with col2:
            import urllib.parse
            subject = urllib.parse.quote(f"MTD Records - {your_business} - {len(df)} receipts")
            body = urllib.parse.quote(summary_text)
            mailto = f"mailto:{accountant_email}?subject={subject}&body={body}"
            st.link_button("📧 Open Email App", mailto, use_container_width=True, type="primary")
