# Google Ads Creative Validator 🎨

A Python tool to validate Google Ads creatives **before** they go live by uploading them as paused ads. Check if your images, videos, or display ads meet Google's advertising policies without spending a single cent.

## 🎯 What Does This Do?

This script uploads your creative assets to a specific Google Ads campaign as **PAUSED** ads, allowing you to:
- ✅ Validate creatives against Google's advertising policies
- ✅ See approval status in the Google Ads UI
- ✅ Get detailed rejection reasons (if any)
- ✅ Never risk accidental ad spend (ads are always paused)

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Google Ads API Credentials

Create a `google-ads.yaml` file (use `google-ads.yaml.template` as a starting point):

```yaml
developer_token: YOUR_DEVELOPER_TOKEN
client_id: YOUR_CLIENT_ID.apps.googleusercontent.com
client_secret: YOUR_CLIENT_SECRET
refresh_token: YOUR_REFRESH_TOKEN
login_customer_id: YOUR_CUSTOMER_ID
use_proto_plus: True
```

**Need help getting credentials?** See [SETUP_GUIDE.md](SETUP_GUIDE.md) for detailed instructions.

### 3. Update Script Configuration

Edit `google_ads_creative_validator.py`:

```python
# Line 13-14: Your account details
CUSTOMER_ID = "3106590821"  # Your Google Ads Customer ID
CAMPAIGN_ID = "23438621203"  # Your Campaign ID

# Line 18: Your creative image
IMAGE_PATH = "path/to/your/image.jpg"

# Line 27: Your landing page
FINAL_URL = "https://www.example.com"
```

### 4. Run the Validator

```bash
python google_ads_creative_validator.py
```

### 5. Check Results in Google Ads UI

1. Go to your campaign: `https://ads.google.com/aw/ads?campaignId=YOUR_CAMPAIGN_ID`
2. Click **"Ads"** in the left sidebar
3. Find your ad with the **Grey "Paused"** icon
4. Check the **"Status"** column:
   - ✅ **"Eligible"** = Creative passed validation
   - ❌ **"Disapproved"** = Creative rejected (hover for reason)

## 📋 Features

- **🔒 Safety First**: All ads created with `PAUSED` status
- **🔍 Smart Ad Group Management**: Finds or creates "Creative_Validator_Bin" ad group
- **📤 Asset Upload**: Handles image upload to Google Ads Asset Service
- **🎨 Responsive Display Ads**: Creates properly formatted display ads
- **📊 Clear Output**: Shows Ad Group ID and Ad Resource Name
- **❌ Error Handling**: Detailed error messages and troubleshooting

## 📁 Project Structure

```
google_ads_api_checker/
├── google_ads_creative_validator.py  # Main script
├── requirements.txt                  # Python dependencies
├── google-ads.yaml.template          # API credentials template
├── SETUP_GUIDE.md                    # Detailed setup instructions
├── README.md                         # This file
├── .gitignore                        # Git ignore rules
└── LICENSE                           # MIT License
```

## 🔧 Requirements

- Python 3.7+
- Google Ads API access
- Active Google Ads account
- Campaign and Ad Group access

## 📖 Documentation

- **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - Complete setup instructions
- **[Google Ads API Docs](https://developers.google.com/google-ads/api/docs/start)** - Official API documentation

## 🐛 Troubleshooting

### Authentication Issues

```bash
# Regenerate refresh token
python -m google.ads.googleads.oauth2.generate_refresh_token \
  --client_id=YOUR_CLIENT_ID \
  --client_secret=YOUR_CLIENT_SECRET
```

### Image Requirements

- **Formats**: JPG, PNG, GIF
- **Max Size**: 5120 KB
- **Recommended Ratio**: 1.91:1 (e.g., 1200x628px)

### Common Errors

| Error | Solution |
|-------|----------|
| `google-ads.yaml not found` | Create config file in script directory |
| `Authentication failed` | Regenerate refresh token |
| `Campaign not found` | Verify Customer ID and Campaign ID |
| `Image upload failed` | Check file path and image format |

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This tool is for validation purposes only. Always review Google Ads policies and ensure your creatives comply with all applicable guidelines.

## 🔗 Resources

- [Google Ads Policies](https://support.google.com/adspolicy/answer/6008942)
- [Display Ad Specifications](https://support.google.com/google-ads/answer/7031480)
- [Google Ads API Python Client](https://github.com/googleads/google-ads-python)

---

Made with ❤️ for advertisers who want to validate creatives safely
