import streamlit as st
import pandas as pd
from datetime import datetime
from PIL import Image
import os

st.set_page_config(page_title="SimpleTax UK", page_icon="🧾", layout="centered", initial_sidebar_state="collapsed", menu_items=None)

# BLUE AND ASH THEME + HIDE BRANDING
st.markdown("""
<style>
.block-container {padding-top: 2.5rem !important; padding-bottom: 1rem; background-color: #f8fafc;}
h1 {font-size: 1.8rem !important; color: #1e40af !important; font-weight: 800 !important;}
h2, h3 {color: #1e3a8a !important; font-weight: 700 !important;}
.stTabs [data-baseweb="tab-list"] {background-color: #e2e8f0; border-radius: 8px; padding: 4px; gap: 4px;}
.stTabs [data-baseweb="tab"] {font-size: 0.85rem !important; color: #64748b !important; border-radius: 6px;}
.stTabs [aria-selected="true"] {background-color: #1e40af !important; color: white !important; font-weight: 600 !important;}
.stButton button {background-color: #1e40af !important; color: white !important; border: none !important; border-radius: 8px !important; font-weight: 600 !important;}
.stButton button:hover {background-color: #1e3a8a !important;}
.stButton button[kind="primary"] {background-color: #2563eb !important; box-shadow: 0 2px 8px rgba(37, 99, 235, 0.3) !important;}
.stDownloadButton button {background-color: white !important; color: #1e40af !important; border: 2px solid #1e40af !important; border-radius: 8px !important; font-weight: 600 !important;}
[data-testid="stMetric"] {background-color: white !important; border: 1px solid #e2e8f0 !important; border-left: 4px solid #1e40af !important; border-radius: 8px !important; padding: 8px !important; box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important;}
[data-testid="stMetricValue"] {font-size: 1.15rem !important; color: #1e3a8a !important; font-weight: 800 !important;}
[data-testid="stMetricLabel"] {font-size: 0.7rem !important; color: #64748b !important; text-transform: uppercase !important;}
.stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {border: 1.5px solid #cbd5e1 !important; border-radius: 8px !important; background-color: white !important;}
[data-testid="stFileUploader"] {background-color: white !important; border: 2px dashed #94a3b8 !important; border-radius: 12px !important; min-height: 120px !important;}
[data-testid="stFileUploaderDropzone"] {min-height: 100px !important; padding: 20px !important;}
/* Hide branding */
#MainMenu, header, footer, [data-testid="stToolbar"], [data-testid="stDecoration"], [data-testid="stStatusWidget"], [data-testid="stHeader"], .stDeployButton, [data-testid="stAppDeployButton"] {display: none !important; visibility: hidden !important;}
.viewerBadge_container__1QSob {display: none !important;}
</style>
""", unsafe_allow_html=True)

# Session init
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

# Login
if not st.session_state.user_id:
    # Compact for 8" phone
    st.markdown("""
    <style>
    /* Compact login for 8 inch phone */
    .block-container {padding-top: 1rem !important;}
    h1 {font-size: 1.4rem !important; margin-bottom: 0.2rem !important;}
    h3 {font-size: 1.1rem !important; margin-top: 0.5rem !important; margin-bottom: 0.5rem !important;}
    [data-testid="stTextInput"] {margin-top: 0.5rem !important;}
    [data-testid="stTextInput"] input {height: 38px !important; font-size: 0.9rem !important; padding: 6px 10px !important;}
    .stCaption {font-size: 0.75rem !important; margin-top: 0.2rem !important;}
    .stButton button {height: 42px !important; font-size: 0.9rem !important; margin-top: 0.5rem !important;}
    </style>
    """, unsafe_allow_html=True)
    st.title("🧾 SimpleTax UK")
    st.markdown("### 👋 Welcome - Easy Receipts Submission")
    user_code = st.text_input("Code / Phone / Business", placeholder="e.g. 07700 or Monsoon Foods", label_visibility="collapsed")
    st.caption("Code is your private key - remember it")
    if st.button("🔓 Login / Create Private Space", type="primary", use_container_width=True):
        if user_code.strip():
            safe = "".join(c for c in user_code if c.isalnum() or c in ("-","_")).strip()[:30]
            if not safe:
                safe = user_code.strip().replace(" ","_")[:30]
            st.session_state.user_id = safe
            st.rerun()
        else:
            st.error("Please enter a code")
    st.stop()

DB_FILE = f"receipts_{st.session_state.user_id}.csv"
UPLOAD_DIR = f"receipt_images_{st.session_state.user_id}"
os.makedirs(UPLOAD_DIR, exist_ok=True)

if not os.path.exists(DB_FILE):
    pd.DataFrame(columns=["date","shop","total","category","filename","image_path","created_at"]).to_csv(DB_FILE, index=False)

def load_receipts():
    try:
        return pd.read_csv(DB_FILE)
    except:
        return pd.DataFrame(columns=["date","shop","total","category","filename","image_path","created_at"])

# Test limit - 5 receipts per user in test period
TEST_LIMIT = 5

def save_receipt(shop, date, total, category, filename, image_path=""):
    df = load_receipts()
    # Check limit
    if len(df) >= TEST_LIMIT and st.session_state.user_id.lower() != "admin":
        st.error(f"⚠️ Test limit: Max {TEST_LIMIT} receipts per user. Contact admin.")
        return False
    new_row = pd.DataFrame([{
        "date": date, "shop": shop, "total": float(total), "category": category,
        "filename": filename, "image_path": image_path,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
    }])
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(DB_FILE, index=False)
    return True

def get_all_users_data():
    """Admin: see all users uploads"""
    import glob
    all_files = glob.glob("receipts_*.csv")
    users = []
    for f in all_files:
        try:
            df = pd.read_csv(f)
            user = f.replace("receipts_","").replace(".csv","")
            users.append({"user": user, "file": f, "count": len(df), "total": df["total"].sum() if not df.empty else 0, "df": df})
        except:
            pass
    return users

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

# --- FIXED HEADER FOR 4" MOBILE ---
# Check logout via query param
if "logout" in st.query_params:
    st.session_state.user_id = None
    st.query_params.clear()
    st.rerun()

st.markdown("""
<style>
.stApp {background-color: #eef2f7 !important;}
[data-testid="stAppViewContainer"] {background-color: #eef2f7 !important;}
[data-testid="stHeader"] {background-color: #eef2f7 !important;}
.block-container {background-color: #eef2f7 !important;}
</style>
""", unsafe_allow_html=True)

st.markdown(f"""
<style>
/* Header - same line */
.header-wrapper {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    width: 100%;
    box-sizing: border-box;
    margin-bottom: 4px;
}}
.logout-link {{
    background-color: #1e40af;
    color: white !important;
    padding: 6px 14px;
    border-radius: 8px;
    text-decoration: none !important;
    font-size: 0.8rem;
    font-weight: 600;
    white-space: nowrap;
    margin-left: 10px;
}}
.logout-link:hover {{background-color: #1e3a8a; color: white !important;}}
/* Main nav - single line 4 inch */
.main-nav {{
    background-color: #f1f5f9;
    border-radius: 8px;
    padding: 4px 2px;
    margin-top: 0.5rem;
    width: 100%;
    overflow-x: auto;
}}
.main-nav [role="radiogroup"] {{
    gap: 2px !important;
    flex-wrap: nowrap !important;
    display: flex !important;
    justify-content: space-between;
    width: 100%;
}}
.main-nav [role="radiogroup"] label {{
    font-size: 0.68rem !important;
    font-weight: 600 !important;
    padding: 6px 5px !important;
    border-radius: 6px !important;
    white-space: nowrap !important;
    flex: 1;
    text-align: center;
    min-width: 0;
    margin: 0 !important;
}}
@media (max-width: 400px) {{
    .main-nav [role="radiogroup"] label {{font-size: 0.62rem !important; padding: 5px 3px !important;}}
    [data-testid="stFileUploader"] {{width: 100% !important; max-width: 100% !important; box-sizing: border-box !important;}}
}}
</style>
<div class="header-wrapper">
    <div style="display:flex; align-items:center; gap:6px;">
        <span style="font-size:1.4rem;">🧾</span>
        <span style="color:#1e40af; font-size:1.35rem; font-weight:800;">SimpleTax UK</span>
    </div>
    <a href="?logout=1" class="logout-link">Logout</a>
</div>
<p style="margin:0 0 8px 0; color:#64748b; font-size:0.78rem;">UK Making Tax Digital • Private: {st.session_state.user_id}</p>
""", unsafe_allow_html=True)

# Main navigation - SINGLE LINE on 4 inch screen
st.markdown("""
<style>
/* Main nav - ultra compact single line */
.main-nav {
    background-color: #f1f5f9;
    border-radius: 8px;
    padding: 4px 2px;
    margin-top: 0.5rem;
    width: 100%;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
}
.main-nav [data-testid="stRadio"] {padding: 0; margin: 0;}
.main-nav [role="radiogroup"] {
    gap: 2px !important;
    flex-wrap: nowrap !important;
    display: flex !important;
    justify-content: space-between;
    width: 100%;
}
.main-nav [role="radiogroup"] label {
    font-size: 0.68rem !important;
    font-weight: 600 !important;
    padding: 6px 5px !important;
    border-radius: 6px !important;
    white-space: nowrap !important;
    flex: 1;
    text-align: center;
    min-width: 0;
    margin: 0 !important;
}
.main-nav [role="radiogroup"] label p {
    font-size: 0.68rem !important;
    margin: 0 !important;
}
/* Selected */
.main-nav label:has(input:checked) {
    background-color: #1e40af !important;
    color: white !important;
}
/* Even more compact on 4 inch */
@media (max-width: 400px) {
    .main-nav [role="radiogroup"] label {font-size: 0.62rem !important; padding: 5px 3px !important;}
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-nav">', unsafe_allow_html=True)
main_nav = st.radio("Main menu", ["Add", "List", "Dash", "Acct"], horizontal=True, label_visibility="collapsed", key="main_nav_radio")
st.markdown('</div>', unsafe_allow_html=True)

# Map radio to tab variables for compatibility
class FakeTab:
    def __init__(self, active, name):
        self.active = active
        self.name = name
    def __enter__(self):
        return self
    def __exit__(self, *args):
        pass

# Use conditions instead of tabs
show_add = main_nav == "Add"
show_list = main_nav == "List"
show_dash = main_nav == "Dash"
show_send = main_nav == "Acct"


if show_add:
    # Compact for 8" phone - smaller everything
    st.markdown("""
    <style>
    /* Compact Add Receipt for 8 inch */
    h2 {font-size: 1.2rem !important; margin-bottom: 0.3rem !important;}
    [data-testid="stCaptionContainer"] {font-size: 0.75rem !important; margin-bottom: 0.3rem !important;}
    [data-testid="stFileUploader"] {min-height: 60px !important; padding: 5px !important; margin-top: 0.3rem !important;}
    [data-testid="stFileUploader"] button {min-height: 32px !important; font-size: 0.85rem !important; padding: 4px 10px !important;}
    [data-testid="stFileUploaderDropzone"] {min-height: 50px !important; padding: 8px !important;}
    [data-testid="stFileUploaderDropzone"] small {font-size: 0.7rem !important;}
    [data-testid="stCameraInput"] {margin-top: 0.3rem !important;}
    /* Radio buttons instead of blue tabs - clean look */
    [data-testid="stRadio"] {margin-top: 0.5rem !important; margin-bottom: 0.2rem !important;}
    [data-testid="stRadio"] label {font-size: 0.85rem !important;}
    </style>
    """, unsafe_allow_html=True)
    st.subheader("Add Receipt")
    st.caption("📱 Camera for instant capture")
    uploader_key = f"uploader_{st.session_state.upload_counter}"
    
    # Radio buttons instead of blue square tabs
    upload_method = st.radio("Upload method", ["📁 Browse files", "📷 Take photo"], horizontal=True, label_visibility="collapsed")
    
    uploaded = None
    if upload_method == "📁 Browse files":
        uploaded_file = st.file_uploader("Pick receipt", type=["jpg","jpeg","png","heic"], key=uploader_key, label_visibility="collapsed")
        if uploaded_file:
            uploaded = uploaded_file
    else:
        camera_file = st.camera_input("Photo", key=f"cam_{st.session_state.upload_counter}", label_visibility="collapsed")
        if camera_file:
            uploaded = camera_file
            st.success("✅ Captured!")
    
    if st.session_state.last_saved:
        st.success(f"✅ {st.session_state.last_saved['shop']} £{st.session_state.last_saved['total']}")
        st.session_state.last_saved = None
    
    if uploaded:
        try:
            orig_name = uploaded.name
        except:
            orig_name = f"receipt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        safe_name = "".join(c for c in orig_name if c.isalnum() or c in (".","_","-"))[:50]
        if not safe_name.lower().endswith(('.jpg','.jpeg','.png','.heic')):
            safe_name += ".jpg"
        image_path_saved = os.path.join(UPLOAD_DIR, f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{safe_name}")
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
        try:
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
                ok = save_receipt(shop, date, total, cat, safe_name, image_path_saved)
                if ok:
                    st.session_state.last_saved = {"shop": shop, "total": total}
                    st.session_state.upload_counter += 1
                    st.rerun()

if show_list:
    st.subheader("Receipts")
    # Admin view - if login as admin, see all users
    if st.session_state.user_id.lower() == "admin":
        st.warning("👑 ADMIN MODE - You can see all users uploads (backend)")
        all_users = get_all_users_data()
        if not all_users:
            st.info("No users yet")
        else:
            for u in all_users:
                with st.expander(f"👤 {u['user']} - {u['count']} receipts - £{u['total']:.2f}"):
                    st.dataframe(u['df'], width='stretch')
                    # Show images path
                    st.caption(f"Files in: receipt_images_{u['user']}/")
            st.divider()
            st.caption("End admin view - below is your own admin receipts")
    
    df = load_receipts()
    # Show limit info
    remaining = TEST_LIMIT - len(df)
    if st.session_state.user_id.lower() != "admin":
        if remaining <= 2 and remaining > 0:
            st.warning(f"⚠️ Test limit: {remaining} receipts left out of {TEST_LIMIT}")
        elif remaining <= 0:
            st.error(f"❌ Test limit reached: {TEST_LIMIT} receipts max")
    if df.empty:
        st.info("No receipts yet - Add your first receipt")
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

if show_dash:
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

if show_send:
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
