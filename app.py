
import streamlit as st
import pandas as pd
from datetime import datetime
from PIL import Image
import os, glob

st.set_page_config(page_title="SimpleTax UK", page_icon="🧾", layout="centered", initial_sidebar_state="collapsed")

st.markdown("""
<style>
.stApp {background-color: #f8fafc !important;}
.block-container {background-color: #f8fafc !important; padding-top: 0.6rem !important; padding-left: 0.5rem !important; padding-right: 0.5rem !important;}
h1 {color: #1e40af !important; font-size: 1.65rem !important; font-weight: 800 !important;}
h3 {color: #1e3a8a !important; font-size: 1.05rem !important; font-weight: 700 !important;}
[data-testid="stTextInput"] input {border: 1.5px solid #d1d5db !important; border-radius: 10px !important; height: 44px !important; font-size: 0.92rem !important;}
.stCaption {color: #6b7280 !important; font-size: 0.82rem !important;}
.stButton button {background-color: #2563eb !important; color: white !important; border-radius: 10px !important; height: 46px !important; font-weight: 600 !important;}
#MainMenu, header, footer, [data-testid="stToolbar"] {display: none !important;}

/* 4 inch fit - header same line */
.header-row {display: flex !important; justify-content: space-between !important; align-items: center !important; width: 100% !important; box-sizing: border-box !important;}
.header-title {color: #1e40af !important; font-weight: 800 !important; font-size: 1.15rem !important; white-space: nowrap !important;}
.logout-small {background-color: #2563eb; color: white; border: none; border-radius: 8px; padding: 6px 10px; font-size: 0.7rem; font-weight: 600; height: 28px; cursor: pointer;}

/* Main nav - fit 4 inch with full words Dashboard Accountant */
.main-nav-box {background-color: white; border-radius: 8px; padding: 2px 1px; margin: 0.3rem 0; border: 1px solid #e2e8f0; width: 100%; box-sizing: border-box;}
.main-nav-box [data-testid="stRadio"] {width: 100% !important;}
.main-nav-box [role="radiogroup"] {display: flex !important; flex-wrap: nowrap !important; justify-content: space-between !important; gap: 0px !important; width: 100% !important;}
.main-nav-box [role="radiogroup"] label {font-size: 0.62rem !important; font-weight: 600 !important; padding: 4px 2px !important; margin: 0 1px !important; flex: 1 !important; text-align: center !important; white-space: nowrap !important; min-width: 0 !important;}
.main-nav-box [role="radiogroup"] label p {font-size: 0.62rem !important;}

/* Upload method */
.upload-box [role="radiogroup"] {gap: 8px !important;}
.upload-box label {font-size: 0.8rem !important;}
</style>
""", unsafe_allow_html=True)

if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "quarter_income" not in st.session_state:
    st.session_state.quarter_income = 1000
if "last_saved" not in st.session_state:
    st.session_state.last_saved = None
if "upload_counter" not in st.session_state:
    st.session_state.upload_counter = 0
if "current_image_path" not in st.session_state:
    st.session_state.current_image_path = None

if not st.session_state.user_id:
    st.title("🧾 SimpleTax UK")
    st.markdown("### 👋 Welcome - Easy Receipts Submission")
    user_code = st.text_input("code", placeholder="type a memorable name or code", label_visibility="collapsed")
    st.caption("You should remember your memorable code")
    if st.button("🔓 Login / Create Private Space", type="primary", use_container_width=True):
        if user_code.strip():
            safe = "".join(c for c in user_code if c.isalnum() or c in ("-","_")).strip()[:30]
            if not safe:
                safe = user_code.strip().replace(" ","_")[:30]
            st.session_state.user_id = safe
            st.rerun()
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

# --- HEADER SAME LINE - FIT 4 INCH ---
st.markdown(f"""
<div class="header-row">
    <div class="header-title">🧾 SimpleTax UK</div>
    <div style="font-size:0.65rem; color:#64748b; margin-left: auto; margin-right: 8px;">Private: {st.session_state.user_id}</div>
</div>
""", unsafe_allow_html=True)

# Put logout in same line using columns that fit 4"
col_title, col_logout = st.columns([3,1], gap="small")
with col_title:
    st.markdown(f"<span style='color:#1e40af; font-weight:800; font-size:1.15rem;'>🧾 SimpleTax UK</span><br><span style='font-size:0.65rem; color:#64748b;'>Private: {st.session_state.user_id}</span>", unsafe_allow_html=True)
with col_logout:
    if st.button("Logout", key="logout_btn", use_container_width=True):
        st.session_state.user_id = None
        st.session_state.current_image_path = None
        st.rerun()

# Nav - full words Dashboard Accountant but fit 4"
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

        # FIX 1: If Take photo, DON'T show second image - camera_input already shows preview with Clear photo
        # Only show our preview for Browse files
        if not is_camera:
            if st.session_state.current_image_path and os.path.exists(st.session_state.current_image_path):
                try:
                    img = Image.open(st.session_state.current_image_path)
                    st.image(img, width=250, caption="Ready to submit - only this receipt")
                except:
                    st.write("Image ready")
        else:
            # For camera, show small note that this is the only receipt
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
    if st.session_state.user_id.lower() == "admin":
        st.warning("ADMIN MODE")
        all_users = get_all_users_data()
        if not all_users:
            st.info("No user receipts yet")
        else:
            for u in all_users:
                with st.expander(f"{u['user']} - {u['count']} - £{u['total']:.2f}"):
                    d = u['df'].rename(columns={"shop": "Description", "date": "Date", "total": "Total £", "category": "Category"})
                    cols = [c for c in ["Date","Description","Total £","Category"] if c in d.columns]
                    st.dataframe(d[cols], width="stretch")
        st.divider()
    df = load_receipts()
    if df.empty:
        st.info("No receipts yet - Add your first receipt")
    else:
        st.caption(f"{len(df)} receipts, £{df['total'].sum():.2f} - only your private receipts")
        for idx in reversed(df.index.tolist()):
            row = df.loc[idx]
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
                        df.drop(idx).to_csv(DB_FILE, index=False)
                        st.rerun()

if main_nav == "Dashboard":
    st.subheader("Dashboard")
    df = load_receipts()
    total_exp = df["total"].sum() if not df.empty else 0
    quarter_income = st.number_input("Income this quarter £", value=st.session_state.quarter_income, min_value=0, step=100)
    st.session_state.quarter_income = quarter_income
    profit = quarter_income - total_exp
    c1, c2 = st.columns(2)
    c1.metric("Expenses", f"£{total_exp:.2f}")
    c2.metric("Profit Q", f"£{profit:.2f}")
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
        your_name = st.text_input("Your name", "Demo User")
        your_business = st.text_input("Business", "Monsoon Foods")
        accountant_email = st.text_input("Accountant email", "accountant@example.com")
        qi = st.session_state.quarter_income
        st.info(f"Income from Dashboard: £{qi:.2f}")
        profit = qi - df["total"].sum()
        txt = f"Business: {your_business}\nIncome: £{qi:.2f}\nExpenses: £{df['total'].sum():.2f}\nProfit: £{profit:.2f}\n\nThanks, {your_name}"
        st.text_area("Preview", txt, height=100)
        st.download_button("Download CSV", df.to_csv(index=False).encode(), "MTD.csv", "text/csv", use_container_width=True)
        import urllib.parse
        subject = urllib.parse.quote(f"MTD - {your_business}")
        body = urllib.parse.quote(txt)
        st.link_button("Open Email App", f"mailto:{accountant_email}?subject={subject}&body={body}", use_container_width=True, type="primary")
