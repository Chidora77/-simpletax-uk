
import streamlit as st
import pandas as pd
from datetime import datetime
from PIL import Image
import os, glob

st.set_page_config(page_title="SimpleTax UK", page_icon="🧾", layout="centered", initial_sidebar_state="collapsed")

st.markdown("""
<style>
.stApp {background-color: #eef2f7 !important;}
.block-container {background-color: #eef2f7 !important; padding-left: 0.6rem !important; padding-right: 0.6rem !important;}
#MainMenu, header, footer, [data-testid="stToolbar"] {display: none !important;}
</style>
""", unsafe_allow_html=True)

if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "quarter_income" not in st.session_state:
    st.session_state.quarter_income = 1000
if "last_saved" not in st.session_state:
    st.session_state.last_saved = None
if "zoomed" not in st.session_state:
    st.session_state.zoomed = {}
if "upload_counter" not in st.session_state:
    st.session_state.upload_counter = 0

if not st.session_state.user_id:
    st.title("🧾 SimpleTax UK")
    st.markdown("### Welcome - Easy Receipts Submission")
    user_code = st.text_input("memory code", placeholder="e.g. 07700 or Monsoon Foods", label_visibility="collapsed")
    st.caption("You should remember your memory code")
    if st.button("Login / Create Private Space", type="primary", use_container_width=True):
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
        st.error(f"Test limit: Max {TEST_LIMIT} receipts")
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

col_h1, col_h2 = st.columns([4,1])
with col_h1:
    st.markdown(f"**🧾 SimpleTax UK**  \n<span style='font-size:0.7rem;color:#64748b'>Private: {st.session_state.user_id}</span>", unsafe_allow_html=True)
with col_h2:
    if st.button("Logout", key="logout_btn"):
        st.session_state.user_id = None
        st.rerun()

main_nav = st.radio("nav", ["Add", "List", "Dash", "Acct"], horizontal=True, label_visibility="collapsed")
st.divider()

show_add = main_nav == "Add"
show_list = main_nav == "List"
show_dash = main_nav == "Dash"
show_send = main_nav == "Acct"

if show_add:
    st.subheader("Add Receipt")
    upload_method = st.radio("method", ["Browse files", "Take photo"], horizontal=True)
    uploaded = None
    uploader_key = f"uploader_{st.session_state.upload_counter}"
    if upload_method == "Browse files":
        uf = st.file_uploader("Pick receipt", type=["jpg","jpeg","png","heic"], key=uploader_key, label_visibility="collapsed")
        if uf:
            uploaded = uf
    else:
        cam = st.camera_input("Take photo", key=f"cam_{st.session_state.upload_counter}", label_visibility="collapsed")
        if cam:
            uploaded = cam

    if st.session_state.last_saved:
        st.success(f"Saved {st.session_state.last_saved['shop']} £{st.session_state.last_saved['total']}")
        st.session_state.last_saved = None

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
        except:
            pass
        if os.path.exists(image_path_saved):
            try:
                img = Image.open(image_path_saved)
                st.image(img, width=250, caption="Ready to submit - fill form below")
            except:
                st.write("Image ready")
        with st.form("add_form"):
            shop = st.text_input("Description", "Monsoon Foods")
            total = st.number_input("Total £", value=49.84, step=0.01)
            date = st.text_input("Date", datetime.now().strftime("%Y-%m-%d"))
            cat = st.selectbox("Category", ["Cost of goods sold","Tools","Travel","Materials","Office costs","Fuel","Other"])
            submitted = st.form_submit_button("SUBMIT RECEIPT", type="primary", use_container_width=True)
            if submitted:
                ok = save_receipt(shop, date, total, cat, safe_name, image_path_saved)
                if ok:
                    st.session_state.last_saved = {"shop": shop, "total": total}
                    st.session_state.upload_counter += 1
                    st.rerun()

if show_list:
    st.subheader("Receipts")
    if st.session_state.user_id.lower() == "admin":
        st.warning("ADMIN MODE - Backend view")
        all_users = get_all_users_data()
        if not all_users:
            st.info("No user receipts yet")
        else:
            for u in all_users:
                with st.expander(f"{u['user']} - {u['count']} receipts - £{u['total']:.2f}"):
                    d = u['df'].rename(columns={"shop": "Description", "date": "Date", "total": "Total £", "category": "Category"})
                    cols = [c for c in ["Date","Description","Total £","Category"] if c in d.columns]
                    st.dataframe(d[cols], width="stretch")
        st.divider()
    df = load_receipts()
    remaining = TEST_LIMIT - len(df)
    if st.session_state.user_id.lower() != "admin":
        if remaining <= 2 and remaining > 0:
            st.warning(f"Test limit: {remaining} left")
        elif remaining <= 0:
            st.error(f"Limit reached: {TEST_LIMIT} max")
    if df.empty:
        st.info("No receipts yet - Add your first receipt")
    else:
        st.caption(f"{len(df)} receipts, £{df['total'].sum():.2f}")
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
                        st.write("R")
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

if show_dash:
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

if show_send:
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
