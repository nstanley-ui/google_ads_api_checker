# Google Ads Creative Validator - Setup Guide

## 📋 Prerequisites

1. **Google Ads Account** with API access
2. **Python 3.7+** installed
3. **Google Ads API credentials** (developer token, client ID, client secret, refresh token)

---

## 🔧 Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🔑 Step 2: Set Up Google Ads API Credentials

### A) Get Your Credentials

1. **Developer Token**: 
   - Go to [Google Ads API Center](https://ads.google.com/aw/apicenter)
   - Apply for a developer token (if you don't have one)
   - Note: You can use a test account developer token for testing

2. **OAuth2 Credentials**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project (or use existing)
   - Enable "Google Ads API"
   - Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client ID"
   - Choose "Desktop app"
   - Download the JSON file

3. **Generate Refresh Token**:
   ```bash
   python -m google.ads.googleads.oauth2.generate_refresh_token \
     --client_id=YOUR_CLIENT_ID \
     --client_secret=YOUR_CLIENT_SECRET
   ```
   This will open a browser window to authorize and return a refresh token.

### B) Create google-ads.yaml

Create a file named `google-ads.yaml` in the same directory as the script:

```yaml
# Google Ads API Configuration
developer_token: YOUR_DEVELOPER_TOKEN
client_id: YOUR_CLIENT_ID.apps.googleusercontent.com
client_secret: YOUR_CLIENT_SECRET
refresh_token: YOUR_REFRESH_TOKEN
login_customer_id: 3106590821
use_proto_plus: True
```

**Important**: Replace the placeholders with your actual credentials.

---

## ✏️ Step 3: Configure the Script

Open `google_ads_creative_validator.py` and update:

```python
# Line 13-14: Update these paths
IMAGE_PATH = "path/to/your/image.jpg"  # Your creative image
FINAL_URL = "https://www.example.com"   # Your landing page URL

# Lines 17-22: Customize your ad copy (optional)
HEADLINE_1 = "Your Headline Here"
HEADLINE_2 = "Another Great Headline"
# ... etc
```

---

## 🚀 Step 4: Run the Script

```bash
python google_ads_creative_validator.py
```

---

## 📊 Step 5: Check Results in Google Ads UI

1. Go to: https://ads.google.com/aw/ads?campaignId=23438621203
2. Click **"Ads"** in the left menu
3. Look for your ad with a **Grey "Paused" icon**
4. Check the **"Status"** column:
   - ✅ **"Eligible"** = Your creative PASSED validation
   - ❌ **"Disapproved"** = Your creative FAILED (hover to see reason)

---

## 🔍 Troubleshooting

### Error: "No google-ads.yaml found"
- Make sure the file is in the same directory as the script
- Or set the environment variable: `export GOOGLE_ADS_CONFIGURATION_FILE_PATH=/path/to/google-ads.yaml`

### Error: "Authentication failed"
- Verify your refresh token is valid
- Regenerate refresh token if needed
- Check that developer token is approved (or use test account)

### Error: "Campaign not found"
- Verify the Customer ID (3106590821) and Campaign ID (23438621203)
- Make sure you have access to this account

### Error: "Image upload failed"
- Check image file path is correct
- Verify image meets Google's requirements:
  - Format: JPG, PNG, or GIF
  - Max file size: 5120 KB
  - Recommended: 1200x628px (1.91:1 ratio)

---

## 📝 Notes

- The ad is created with **PAUSED** status, so it will **never spend money**
- You can run this script multiple times to test different creatives
- The script will reuse the existing "Creative_Validator_Bin" ad group
- All ads created will appear in your Google Ads dashboard

---

## 🔗 Useful Links

- [Google Ads API Documentation](https://developers.google.com/google-ads/api/docs/start)
- [Python Client Library Guide](https://developers.google.com/google-ads/api/docs/client-libs/python)
- [Image Asset Requirements](https://support.google.com/google-ads/answer/7031480)
