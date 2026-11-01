
import streamlit as st
import pandas as pd
from datetime import datetime
from PIL import Image
import os, glob

st.set_page_config(page_title="SimpleTax UK", page_icon="🧾", layout="centered", initial_sidebar_state="collapsed")

st.markdown('''
<style>
.stApp {background-color: #eef2f7 !important;}
[data-testid="stAppViewContainer"] {background-color: #eef2f7 !important;}
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
.true-header {display: flex !important; justify-content: space-between !important; align-items: center !important; width: 100% !important; max-width: 100% !important; box-sizing: border-box !important; margin-bottom: 2px !important; flex-wrap: nowrap !important;}
.true-header-left {color: #1e40af !important; font-weight: 800 !important; font-size: 1.1rem !important; white-space: nowrap !important;}
.logout-top {background-color: #2563eb !important; color: white !important; border-radius: 8px !important; padding: 5px 12px !important; font-size: 0.7rem !important; font-weight: 600 !important; height: 26px !important; text-decoration: none !important; display: inline-flex !important; align-items: center !important; white-space: nowrap !important;}
.private-text {font-size: 0.6rem !important; color: #64748b !important;}
[data-testid="stFileUploader"], [data-testid="stCameraInput"] {width: 100% !important; max-width: 100vw !important; box-sizing: border-box !important;}
</style>
''', unsafe_allow_html=True)

if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "q1" not in st.session_state:
    st.session_state.q1 = 0.0
if "q2" not in st.session_state:
    st.session_state.q2 = 0.0
if "q3" not in st.session_state:
    st.session_state.q3 = 0.0
if "q4" not in st.session_state:
    st.session_state.q4 = 0.0
if "last_saved" not in st.session_state:
    st.session_state.last_saved = None
if "upload_counter" not in st.session_state:
    st.session_state.upload_counter = 0
if "current_image_path" not in st.session_state:
    st.session_state.current_image_path = None
if "quarter_income" not in st.session_state:
    st.session_state.quarter_income = 0.0

if "logout" in st.query_params:
    st.session_state.user_id = None
    st.session_state.current_image_path = None
    st.query_params.clear()
    st.rerun()

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
    st.stop()

def get_db_file():
    return f"receipts_{st.session_state.user_id}.csv"

def get_upload_dir():
    d = f"receipt_images_{st.session_state.user_id}"
    os.makedirs(d, exist_ok=True)
    return d

def load_receipts():
    f = get_db_file()
    if not os.path.exists(f):
        pd.DataFrame(columns=["date","shop","total","category","filename","image_path","created_at"]).to_csv(f, index=False)
    try:
        return pd.read_csv(f)
    except:
        return pd.DataFrame(columns=["date","shop","total","category","filename","image_path","created_at"])

TEST_LIMIT = 5

def save_receipt(shop, date, total, category, filename, image_path=""):
    f = get_db_file()
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
    df.to_csv(f, index=False)
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

def calc_tax_from_annual(annual_profit):
    taxable = max(0, annual_profit - 12570)
    basic = min(taxable, 37700) * 0.20
    higher = max(0, taxable - 37700) * 0.40
    ni = 0
    if annual_profit > 12570:
        ni += (min(annual_profit, 50270) - 12570) * 0.06
        if annual_profit > 50270:
            ni += (annual_profit - 50270) * 0.02
    class2 = 179.40 if annual_profit > 12570 else 0
    total_annual = basic + higher + ni + class2
    return annual_profit, taxable, basic, higher, ni, class2, total_annual

st.markdown(f'''
<div class="true-header">
    <div class="true-header-left">🧾 SimpleTax UK</div>
    <div style="display:flex; flex-direction:column; align-items:flex-end; gap:2px;">
        <a href="?logout=1" class="logout-top">Logout</a>
        <span class="private-text">Private: {st.session_state.user_id}</span>
    </div>
</div>
''', unsafe_allow_html=True)

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
    uploader_key = f"uploader_{st.session_state.user_id}_{st.session_state.upload_counter}"
    if upload_method == "Browse files":
        uf = st.file_uploader("Pick receipt", type=["jpg","jpeg","png","heic"], key=uploader_key, label_visibility="collapsed")
        if uf:
            uploaded = uf
            is_camera = False
    else:
        cam = st.camera_input("Take photo", key=f"cam_{st.session_state.user_id}_{st.session_state.upload_counter}", label_visibility="collapsed")
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
        upload_dir = get_upload_dir()
        image_path_saved = os.path.join(upload_dir, f"{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}_{safe_name}")
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
                    st.image(img, width=250, caption=f"Ready to submit - only this receipt for {st.session_state.user_id}")
                except:
                    st.write("Image ready")
        else:
            st.info(f"This is your current photo for {st.session_state.user_id} - only this will be saved")
        with st.form("add_form"):
            shop = st.text_input("Description", placeholder="e.g. Your shop name", label_visibility="visible")
            total = st.number_input("Total £", value=0.0, step=0.01)
            date = st.text_input("Date", datetime.now().strftime("%Y-%m-%d"))
            cat = st.selectbox("Category", ["Cost of goods sold","Tools","Travel","Materials","Office costs","Fuel","Other"])
            if st.form_submit_button("SUBMIT RECEIPT", type="primary", use_container_width=True):
                if not shop.strip():
                    st.error("Please enter description")
                else:
                    ok = save_receipt(shop, date, total, cat, safe_name, image_path_saved)
                    if ok:
                        st.session_state.last_saved = {"shop": shop, "total": total}
                        st.session_state.upload_counter += 1
                        st.session_state.current_image_path = None
                        st.rerun()

if main_nav == "List":
    st.subheader("Receipts")
    df_personal = load_receipts()
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
    if st.session_state.user_id.lower() != "admin":
        if df_personal.empty:
            st.info("No receipts yet - Add your first receipt")
        else:
            st.caption(f"{len(df_personal)} receipts, £{df_personal['total'].sum():.2f} - only your private receipts for {st.session_state.user_id}")
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
                        if st.button("DELETE", key=f"del_{st.session_state.user_id}_{idx}", type="primary", use_container_width=True):
                            try:
                                if os.path.exists(str(row["image_path"])):
                                    os.remove(str(row["image_path"]))
                            except:
                                pass
                            df_personal.drop(idx).to_csv(get_db_file(), index=False)
                            st.rerun()

if main_nav == "Dashboard":
    st.subheader("Dashboard")
    df = load_receipts()
    total_exp = df["total"].sum() if not df.empty else 0
    st.markdown("**Quarterly Income - enter each quarter separately (dynamic)**")
    col1, col2 = st.columns(2)
    with col1:
        q1 = st.number_input("Q1 Income £ (Apr-Jul)", value=float(st.session_state.q1), min_value=0.0, step=100.0, key="q1_input")
        q2 = st.number_input("Q2 Income £ (Jul-Oct)", value=float(st.session_state.q2), min_value=0.0, step=100.0, key="q2_input")
    with col2:
        q3 = st.number_input("Q3 Income £ (Oct-Jan)", value=float(st.session_state.q3), min_value=0.0, step=100.0, key="q3_input")
        q4 = st.number_input("Q4 Income £ (Jan-Apr)", value=float(st.session_state.q4), min_value=0.0, step=100.0, key="q4_input")
    st.session_state.q1, st.session_state.q2, st.session_state.q3, st.session_state.q4 = q1, q2, q3, q4
    annual_income = q1+q2+q3+q4
    annual_profit = annual_income - total_exp
    c1, c2, c3 = st.columns(3)
    c1.metric("Expenses", f"£{total_exp:.2f}")
    c2.metric("Profit Annual", f"£{annual_profit:.2f}")
    if annual_income > 0:
        annual, taxable, basic, higher, ni, class2, total_annual = calc_tax_from_annual(annual_profit)
        c3.metric("Tax Annual", f"£{total_annual:.2f}")
        st.success(f"Annual Income £{annual_income:.0f} | Profit £{annual_profit:.0f} | Tax £{total_annual:.0f}/yr = £{total_annual/4:.0f}/qtr avg")
        with st.expander("📖 Full HMRC breakdown - dynamic per quarter"):
            st.markdown(f"Annual Profit £{annual_profit:.2f} | Taxable £{taxable:.2f} | Income Tax £{basic+higher:.2f} | NI £{ni+class2:.2f} | **Total £{total_annual:.2f}/yr**")
            st.caption(f"Q1 £{q1:.0f} + Q2 £{q2:.0f} + Q3 £{q3:.0f} + Q4 £{q4:.0f} = £{annual_income:.0f} (dynamic - each quarter can be different)")
    else:
        c3.metric("Tax Annual", "£0.00")
        st.info("Enter income for each quarter above - no more x4 same quarter")
    st.session_state.quarter_income = annual_income
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
        qi = st.session_state.q1 + st.session_state.q2 + st.session_state.q3 + st.session_state.q4
        st.info(f"Total Annual Income (dynamic): £{qi:.2f} = Q1 £{st.session_state.q1:.0f}+Q2 £{st.session_state.q2:.0f}+Q3 £{st.session_state.q3:.0f}+Q4 £{st.session_state.q4:.0f}")
        profit = qi - df["total"].sum()
        txt = f"Business: {your_business}\nAnnual Income: £{qi:.2f}\nExpenses: £{df['total'].sum():.2f}\nAnnual Profit: £{profit:.2f}\n\nThanks, {your_name}"
        st.text_area("Preview", txt, height=100)
        st.download_button("Download CSV", df.to_csv(index=False).encode(), "MTD.csv", "text/csv", use_container_width=True)
        import urllib.parse
        subject = urllib.parse.quote(f"MTD - {your_business}")
        body = urllib.parse.quote(txt)
        st.link_button("Open Email App", f"mailto:{accountant_email}?subject={subject}&body={body}", use_container_width=True, type="primary")
