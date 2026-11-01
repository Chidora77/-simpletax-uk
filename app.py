
import streamlit as st
import pandas as pd
from datetime import datetime
from PIL import Image
import os, glob

st.set_page_config(page_title="SimpleTax UK", page_icon="🧾", layout="centered", initial_sidebar_state="collapsed")

st.markdown("""
<style>
.stApp {background-color: #eef2f7 !important;} [data-testid="stAppViewContainer"] {background-color: #eef2f7 !important;} [data-testid="stHeader"] {background-color: #eef2f7 !important;}
.block-container {background-color: #eef2f7 !important; padding-top: 0.6rem !important; padding-left: 0.5rem !important; padding-right: 0.5rem !important;}
h1 {color: #1e40af !important; font-size: 1.65rem !important; font-weight: 800 !important;}
h3 {color: #1e3a8a !important; font-size: 1.05rem !important; font-weight: 700 !important;}
[data-testid="stTextInput"] input {border: 1.5px solid #d1d5db !important; border-radius: 10px !important; height: 44px !important; font-size: 0.92rem !important;}
.stCaption {color: #6b7280 !important; font-size: 0.82rem !important;}
.stButton button {background-color: #2563eb !important; color: white !important; border-radius: 10px !important; height: 46px !important; font-weight: 600 !important;}
#MainMenu, header, footer, [data-testid="stToolbar"] {display: none !important;}
.main-nav-box {background-color: white; border-radius: 8px; padding: 2px 1px; margin: 0.3rem 0; border: 1px solid #e2e8f0; width: 100%; box-sizing: border-box;}
.main-nav-box [role="radiogroup"] {display: flex !important; flex-wrap: nowrap !important; justify-content: space-between !important; gap: 0px !important; width: 100% !important;}
.main-nav-box [role="radiogroup"] label {font-size: 0.62rem !important; font-weight: 600 !important; padding: 4px 2px !important; flex: 1 !important; text-align: center !important; white-space: nowrap !important;}
.upload-box [role="radiogroup"] {gap: 8px !important;}
</style>
""", unsafe_allow_html=True)

if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "quarter_income" not in st.session_state:
    st.session_state.quarter_income = 0
if "last_saved" not in st.session_state:
    st.session_state.last_saved = None
if "upload_counter" not in st.session_state:
    st.session_state.upload_counter = 0
if "current_image_path" not in st.session_state:
    st.session_state.current_image_path = None

# --- FIX 3: ENTER KEY LOGIN via form ---
if not st.session_state.user_id:
    st.title("🧾 SimpleTax UK")
    st.markdown("### 👋 Welcome - Easy Receipts Submission")
    with st.form("login_form"):
        user_code = st.text_input("code", placeholder="type a memorable name or code", label_visibility="collapsed")
        st.caption("You should remember your memorable code")
        submitted = st.form_submit_button("🔓 Login / Create Private Space", type="primary", use_container_width=True)
        if submitted:
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

TEST_LIMIT = 5

def save_receipt(shop, date, total, category, filename, image_path=""):
    df = load_receipts()
    if len(df) >= TEST_LIMIT and st.session_state.user_id.lower() != "admin":
        st.error(f"Test limit: Max {TEST_LIMIT}")
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
    files = glob.glob("receipts_*.csv")
    users = []
    for f in files:
        try:
            df = pd.read_csv(f)
            user = f.replace("receipts_","").replace(".csv","")
            if user.lower() == "admin":
                continue
            if df.empty:
                continue
            users.append({"user": user, "file": f, "count": len(df), "total": df["total"].sum(), "df": df})
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

# --- FIX: HEADER TRUE SAME LINE TOP RIGHT - 4 INCH ---
# Use HTML flex so logout stays top right same line even on 4" screen
st.markdown(f"""
<style>
/* Header flex - forces same line on 4 inch */
.true-header {{
    display: flex !important;
    justify-content: space-between !important;
    align-items: center !important;
    width: 100% !important;
    max-width: 100% !important;
    box-sizing: border-box !important;
    margin-bottom: 2px !important;
    flex-wrap: nowrap !important;
}}
.true-header-left {{
    color: #1e40af !important;
    font-weight: 800 !important;
    font-size: 1.1rem !important;
    white-space: nowrap !important;
    display: flex !important;
    align-items: center !important;
    gap: 4px !important;
}}
.true-header-right {{
    display: flex !important;
    flex-direction: column !important;
    align-items: flex-end !important;
    gap: 2px !important;
}}
.logout-top {{
    background-color: #2563eb !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 5px 12px !important;
    font-size: 0.7rem !important;
    font-weight: 600 !important;
    height: 26px !important;
    text-decoration: none !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    white-space: nowrap !important;
}}
.private-text {{
    font-size: 0.6rem !important;
    color: #64748b !important;
}}

/* Upload field - force fit 4 inch - extra strong */
[data-testid="stFileUploader"],
[data-testid="stCameraInput"],
[data-testid="stFileUploaderDropzone"] {{
    width: 100% !important;
    max-width: 100vw !important;
    min-width: 0 !important;
    box-sizing: border-box !important;
    overflow: hidden !important;
}}
[data-testid="stFileUploader"] section {{
    width: 100% !important;
    max-width: 100% !important;
    box-sizing: border-box !important;
}}
</style>
<div class="true-header">
    <div class="true-header-left">🧾 SimpleTax UK</div>
    <div class="true-header-right">
        <a href="?logout=1" class="logout-top">Logout</a>
        <span class="private-text">Private: {st.session_state.user_id}</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Handle logout via query param
if "logout" in st.query_params:
    st.session_state.user_id = None
    st.session_state.current_image_path = None
    st.query_params.clear()
    st.rerun()


st.markdown('<div class="main-nav-box">', unsafe_allow_html=True)
main_nav = st.radio("nav", ["Add", "List", "Dashboard", "Accountant"], horizontal=True, label_visibility="collapsed", key="main_nav")
st.markdown('</div>', unsafe_allow_html=True)

if main_nav == "Add":
    st.subheader("Add Receipt")
    st.markdown('<div class="upload-box">', unsafe_allow_html=True)
    upload_method = st.radio("method", ["Browse files", "Take photo"], horizontal=True, label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)
    uploaded = None
    is_camera = False
    uploader_key = f"uploader_{st.session_state.upload_counter}"
    if upload_method == "Browse files":
        uf = st.file_uploader("Pick receipt", type=["jpg","jpeg","png","heic"], key=uploader_key, label_visibility="collapsed")
        if uf:
            uploaded = uf
            is_camera = False
    else:
        cam = st.camera_input("Take photo", key=f"cam_{st.session_state.upload_counter}", label_visibility="collapsed")
        if cam:
            uploaded = cam
            is_camera = True
    if st.session_state.last_saved:
        st.success(f"Saved {st.session_state.last_saved['shop']} £{st.session_state.last_saved['total']}")
        st.session_state.last_saved = None
        st.session_state.current_image_path = None
    if uploaded:
        try:
            orig_name = getattr(uploaded, 'name', f"receipt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg")
        except:
            orig_name = f"receipt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        safe_name = "".join(c for c in orig_name if c.isalnum() or c in (".","_","-"))[:50]
        if not safe_name.lower().endswith(('.jpg','.jpeg','.png')):
            safe_name += ".jpg"
        image_path_saved = os.path.join(UPLOAD_DIR, f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{safe_name}")
        try:
            data = uploaded.getvalue()
            with open(image_path_saved, "wb") as out:
                out.write(data)
            st.session_state.current_image_path = image_path_saved
        except:
            pass
        if not is_camera:
            if st.session_state.current_image_path and os.path.exists(st.session_state.current_image_path):
                try:
                    img = Image.open(st.session_state.current_image_path)
                    st.image(img, width=250, caption="Ready to submit - only this receipt")
                except:
                    st.write("Image ready")
        else:
            st.info("This is your current photo - only this will be saved")
        with st.form("add_form"):
            shop = st.text_input("Description", "Monsoon Foods")
            total = st.number_input("Total £", value=49.84, step=0.01)
            date = st.text_input("Date", datetime.now().strftime("%Y-%m-%d"))
            cat = st.selectbox("Category", ["Cost of goods sold","Tools","Travel","Materials","Office costs","Fuel","Other"])
            if st.form_submit_button("SUBMIT RECEIPT", type="primary", use_container_width=True):
                ok = save_receipt(shop, date, total, cat, safe_name, image_path_saved)
                if ok:
                    st.session_state.last_saved = {"shop": shop, "total": total}
                    st.session_state.upload_counter += 1
                    st.session_state.current_image_path = None
                    st.rerun()

if main_nav == "List":
    st.subheader("Receipts")
    df_personal = load_receipts()
    # FIX 1: Admin view - show only one message, no duplicate
    if st.session_state.user_id.lower() == "admin":
        st.info("ADMIN MODE - Backend view of all users")
        all_users = get_all_users_data()
        if not all_users:
            st.warning("No user receipts yet")
        else:
            for u in all_users:
                with st.expander(f"{u['user']} - {u['count']} - £{u['total']:.2f}"):
                    d = u['df'].rename(columns={"shop": "Description", "date": "Date", "total": "Total £", "category": "Category"})
                    cols = [c for c in ["Date","Description","Total £","Category"] if c in d.columns]
                    st.dataframe(d[cols], width="stretch")
        st.divider()
        # For admin, show personal admin receipts separately only if exists, else don't duplicate message
        if df_personal.empty:
            st.caption("Your admin personal receipts: none")
        else:
            st.caption(f"Your admin personal: {len(df_personal)} receipts")
    # Personal receipts list - single message only
    if st.session_state.user_id.lower() != "admin":
        if df_personal.empty:
            st.info("No receipts yet - Add your first receipt")
        else:
            st.caption(f"{len(df_personal)} receipts, £{df_personal['total'].sum():.2f} - only your private receipts")
            for idx in reversed(df_personal.index.tolist()):
                row = df_personal.loc[idx]
                c1, c2, c3, c4 = st.columns([1,3,2,2])
                with c1:
                    if row.get("image_path") and os.path.exists(str(row["image_path"])):
                        try:
                            im = Image.open(row["image_path"])
                            im.thumbnail((40,40))
                            st.image(im, width=40)
                        except:
                            pass
                with c2:
                    st.write(str(row['shop'])[:16])
                with c3:
                    st.write(f"£{float(row['total']):.2f}")
                with c4:
                    with st.popover("View"):
                        st.write(f"{row['shop']} £{row['total']}")
                        if row.get("image_path") and os.path.exists(str(row["image_path"])):
                            st.image(Image.open(row["image_path"]), width=200)
                        if st.button("DELETE", key=f"del_{idx}", type="primary", use_container_width=True):
                            try:
                                if os.path.exists(str(row["image_path"])):
                                    os.remove(str(row["image_path"]))
                            except:
                                pass
                            df_personal.drop(idx).to_csv(DB_FILE, index=False)
                            st.rerun()
    else:
        # admin personal part if not empty
        if not df_personal.empty:
            st.caption(f"Admin personal {len(df_personal)} receipts")
            for idx in reversed(df_personal.index.tolist()):
                row = df_personal.loc[idx]
                c1, c2, c3 = st.columns([1,3,2])
                with c1:
                    st.write(str(row['shop'])[:16])
                with c2:
                    st.write(f"£{float(row['total']):.2f}")
                with c3:
                    if st.button("DELETE", key=f"del_admin_{idx}"):
                        df_personal.drop(idx).to_csv(DB_FILE, index=False)
                        st.rerun()

if main_nav == "Dashboard":
    st.subheader("Dashboard")
    df = load_receipts()
    total_exp = df["total"].sum() if not df.empty else 0
    # FIX 2: Income defaults to 0, not 1000, dynamic
    quarter_income = st.number_input("Income this quarter £", value=float(st.session_state.quarter_income), min_value=0.0, step=100.0)
    st.session_state.quarter_income = quarter_income
    profit = quarter_income - total_exp
    # FIX 4: Show Expense, Profit Q AND Tax Q
    c1, c2, c3 = st.columns(3)
    c1.metric("Expenses", f"£{total_exp:.2f}")
    c2.metric("Profit Q", f"£{profit:.2f}")
    if quarter_income > 0 or total_exp > 0:
        annual, taxable, basic, higher, ni, class2, total_annual, total_q = calc_tax_full(profit)
        c3.metric("Tax Q", f"£{total_q:.2f}")
        st.success(f"Annual £{annual:.0f} | Tax £{total_annual:.0f}/yr = £{total_q:.0f}/qtr")
        with st.expander("📖 Full HMRC breakdown"):
            st.markdown(f"Annual £{annual:.2f} | Taxable £{taxable:.2f} | Income Tax £{basic+higher:.2f} | NI £{ni+class2:.2f} | **Total £{total_annual:.2f}/yr**")
    else:
        c3.metric("Tax Q", "£0.00")
        st.info("Enter income above to see tax")
    if not df.empty:
        st.bar_chart(df.groupby("category")["total"].sum())
        d = df.rename(columns={"shop": "Description", "date": "Date", "total": "Total", "category": "Category"})
        st.dataframe(d[["Date","Description","Total","Category"]], width="stretch")
        st.download_button("Download CSV", d.to_csv(index=False).encode(), "MTD.csv", "text/csv", use_container_width=True)

if main_nav == "Accountant":
    st.subheader("Send to Accountant")
    df = load_receipts()
    if df.empty:
        st.info("Add receipts first")
    else:
        st.metric("Ready", f"{len(df)} receipts", f"£{df['total'].sum():.2f}")
        your_name = st.text_input("Your name", st.session_state.user_id)
        your_business = st.text_input("Business", f"{st.session_state.user_id} Foods" if st.session_state.user_id.lower()!="admin" else "Monsoon Foods")
        accountant_email = st.text_input("Accountant email", "accountant@example.com")
        qi = st.session_state.quarter_income
        st.info(f"Income from Dashboard: £{qi:.2f} - dynamic from Dashboard")
        profit = qi - df["total"].sum()
        txt = f"Business: {your_business}\nIncome: £{qi:.2f}\nExpenses: £{df['total'].sum():.2f}\nProfit: £{profit:.2f}\n\nThanks, {your_name}"
        st.text_area("Preview", txt, height=100)
        st.download_button("Download CSV", df.to_csv(index=False).encode(), "MTD.csv", "text/csv", use_container_width=True)
        import urllib.parse
        subject = urllib.parse.quote(f"MTD - {your_business}")
        body = urllib.parse.quote(txt)
        st.link_button("Open Email App", f"mailto:{accountant_email}?subject={subject}&body={body}", use_container_width=True, type="primary")
