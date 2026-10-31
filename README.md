
# SimpleTax UK - Deploy Guide (Blue & Ash)

## 1. Deploy FREE in 3 minutes (Streamlit Cloud - easiest for you)

1. Create GitHub account (github.com) - free
2. Create new repo: simpletax-uk
3. Upload files:
   - app.py
   - requirements.txt
   - .streamlit/config.toml
   - manifest.json
4. Go to share.streamlit.io
5. Click "New app" -> Connect GitHub -> Select simpletax-uk repo -> Branch main -> Main file app.py -> Deploy
6. You get link: https://simpletax-uk.streamlit.app (free, works forever)
7. Share this link - anyone can use on phone

## 2. Make it INSTALLABLE on mobile (like real app)

### For Android (your 8" phone):
- Open your link in Chrome
- Tap 3 dots top right -> "Add to Home screen" or "Install app"
- It appears as icon "SimpleTax UK" blue icon, opens like native app, no address bar
- Works offline for viewing (PWA)

### For iPhone:
- Open link in Safari
- Tap Share button -> "Add to Home Screen"
- Icon appears, opens full screen

This is how Xero, FreeAgent work - they are websites but installable (PWA). No need for App Store yet.

## 3. Better - Make it REAL APK (optional later)

When you have 100+ users:
- Go to pwaBuilder.com
- Enter your streamlit.app link
- It generates Android APK + iOS package you can upload to Play Store / App Store
- Costs $25 for Google Play one-time

## 4. Custom domain (professional)

- Buy simpletax.uk from GoDaddy/Namecheap (£6/year)
- In Streamlit Cloud settings -> Custom domain -> Add simpletax.uk
- Now users go to https://simpletax.uk

## 5. How to make money after deploy

Your app already has Send to Accountant button:

Option A - Subscription:
- Add Stripe: pip install stripe
- In app, after 10 receipts, show "Subscribe £5.99/mo"
- Stripe handles payments

Option B - Referral (no code needed now):
- When user clicks "Find me accountant", form collects postcode
- You email 3 local accountants: "I have MTD client in Mansfield NG18, £25 lead"
- They PayPal you

Start with Option B today, add Stripe later.

## 6. Local testing

pip install -r requirements.txt
streamlit run app.py
Open http://localhost:8501 on phone via same WiFi

## Your current features

- Add receipt (small image)
- List (40px thumbs)
- Dashboard (income 0 default, tax breakdown)
- Send to Accountant (CSV + email)
- Blue & Ash theme
- Mobile optimized for 8" screen
