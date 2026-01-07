import streamlit as st
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
import tempfile
import os
from io import BytesIO

# Page configuration
st.set_page_config(
    page_title="Google Ads Creative Validator",
    page_icon="🎨",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 1rem;
        background: linear-gradient(90deg, #4285f4, #34a853, #fbbc05, #ea4335);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        margin: 1rem 0;
    }
    .error-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        margin: 1rem 0;
    }
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<h1 class="main-header">🎨 Google Ads Creative Validator</h1>', unsafe_allow_html=True)
st.markdown("### Validate your creatives *before* they go live - **100% safe, $0 spent**")

# Sidebar for credentials
with st.sidebar:
    st.header("🔐 API Credentials")
    st.info("Configure these in Streamlit Cloud Secrets or enter manually")
    
    use_secrets = st.checkbox("Use Streamlit Secrets", value=True)
    
    if use_secrets:
        try:
            developer_token = st.secrets["google_ads"]["developer_token"]
            client_id = st.secrets["google_ads"]["client_id"]
            client_secret = st.secrets["google_ads"]["client_secret"]
            refresh_token = st.secrets["google_ads"]["refresh_token"]
            st.success("✅ Using secrets from Streamlit Cloud")
        except Exception as e:
            st.error("❌ Secrets not configured. Switch to manual entry or configure secrets.")
            use_secrets = False
    
    if not use_secrets:
        developer_token = st.text_input("Developer Token", type="password")
        client_id = st.text_input("Client ID")
        client_secret = st.text_input("Client Secret", type="password")
        refresh_token = st.text_input("Refresh Token", type="password")
    
    st.markdown("---")
    st.markdown("### 📚 Resources")
    st.markdown("- [Get API Credentials](https://developers.google.com/google-ads/api/docs/first-call/overview)")
    st.markdown("- [GitHub Repo](https://github.com/nstanley-ui/google_ads_api_checker)")


def initialize_client(developer_token, client_id, client_secret, refresh_token, login_customer_id):
    """Initialize Google Ads API client"""
    try:
        credentials = {
            "developer_token": developer_token,
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": refresh_token,
            "login_customer_id": login_customer_id.replace("-", ""),
            "use_proto_plus": True
        }
        
        # Create client from dict
        client = GoogleAdsClient.load_from_dict(credentials)
        return client, None
    except Exception as e:
        return None, str(e)


def find_or_create_ad_group(client, customer_id, campaign_id, ad_group_name):
    """Find existing ad group or create a new one"""
    ga_service = client.get_service("GoogleAdsService")
    
    query = f"""
        SELECT 
            ad_group.id,
            ad_group.name,
            ad_group.resource_name
        FROM ad_group
        WHERE campaign.id = {campaign_id}
          AND ad_group.name = '{ad_group_name}'
        LIMIT 1
    """
    
    try:
        response = ga_service.search(customer_id=customer_id, query=query)
        
        for row in response:
            return row.ad_group.resource_name, row.ad_group.id, None
        
        # Create new ad group
        ad_group_service = client.get_service("AdGroupService")
        campaign_service = client.get_service("CampaignService")
        
        ad_group_operation = client.get_type("AdGroupOperation")
        ad_group = ad_group_operation.create
        
        ad_group.name = ad_group_name
        ad_group.campaign = campaign_service.campaign_path(customer_id, campaign_id)
        ad_group.status = client.enums.AdGroupStatusEnum.ENABLED
        ad_group.type_ = client.enums.AdGroupTypeEnum.DISPLAY_STANDARD
        ad_group.cpc_bid_micros = 1000000
        
        response = ad_group_service.mutate_ad_groups(
            customer_id=customer_id,
            operations=[ad_group_operation]
        )
        
        ad_group_resource_name = response.results[0].resource_name
        ad_group_id = ad_group_resource_name.split('/')[-1]
        
        return ad_group_resource_name, ad_group_id, None
        
    except GoogleAdsException as ex:
        error_msg = "\n".join([f"- {error.message}" for error in ex.failure.errors])
        return None, None, error_msg


def upload_image_asset(client, customer_id, image_data, image_name):
    """Upload image to Google Ads"""
    asset_service = client.get_service("AssetService")
    
    try:
        asset_operation = client.get_type("AssetOperation")
        asset = asset_operation.create
        asset.type_ = client.enums.AssetTypeEnum.IMAGE
        asset.image_asset.data = image_data
        asset.name = image_name
        
        response = asset_service.mutate_assets(
            customer_id=customer_id,
            operations=[asset_operation]
        )
        
        asset_resource_name = response.results[0].resource_name
        asset_id = asset_resource_name.split('/')[-1]
        
        return asset_resource_name, asset_id, None
        
    except GoogleAdsException as ex:
        error_msg = "\n".join([f"- {error.message}" for error in ex.failure.errors])
        return None, None, error_msg


def create_paused_ad(client, customer_id, ad_group_resource_name, image_asset_resource_name,
                     headline_1, headline_2, headline_3, description_1, description_2,
                     business_name, final_url):
    """Create a paused responsive display ad"""
    ad_group_ad_service = client.get_service("AdGroupAdService")
    
    try:
        ad_group_ad_operation = client.get_type("AdGroupAdOperation")
        ad_group_ad = ad_group_ad_operation.create
        ad_group_ad.ad_group = ad_group_resource_name
        ad_group_ad.status = client.enums.AdGroupAdStatusEnum.PAUSED
        
        ad = ad_group_ad.ad
        ad.final_urls.append(final_url)
        
        responsive_display_ad = ad.responsive_display_ad
        
        # Add headlines
        for headline in [headline_1, headline_2, headline_3]:
            ad_text_asset = client.get_type("AdTextAsset")
            ad_text_asset.text = headline
            responsive_display_ad.headlines.append(ad_text_asset)
        
        # Add descriptions
        for description in [description_1, description_2]:
            ad_text_asset = client.get_type("AdTextAsset")
            ad_text_asset.text = description
            responsive_display_ad.descriptions.append(ad_text_asset)
        
        responsive_display_ad.business_name = business_name
        
        # Add image
        marketing_image = client.get_type("AdImageAsset")
        marketing_image.asset = image_asset_resource_name
        responsive_display_ad.marketing_images.append(marketing_image)
        
        response = ad_group_ad_service.mutate_ad_group_ads(
            customer_id=customer_id,
            operations=[ad_group_ad_operation]
        )
        
        ad_resource_name = response.results[0].resource_name
        return ad_resource_name, None
        
    except GoogleAdsException as ex:
        error_msg = "\n".join([f"- {error.message}" for error in ex.failure.errors])
        return None, error_msg


# Main form
st.markdown("---")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📋 Campaign Details")
    customer_id = st.text_input("Customer ID", value="3106590821", help="Your Google Ads Customer ID (no hyphens)")
    campaign_id = st.text_input("Campaign ID", value="23438621203", help="Campaign where the ad will be created")
    ad_group_name = st.text_input("Ad Group Name", value="Creative_Validator_Bin", help="Ad group for validation ads")

with col2:
    st.subheader("🎨 Creative Upload")
    uploaded_file = st.file_uploader("Upload Your Creative", type=["jpg", "jpeg", "png", "gif"])
    
    if uploaded_file:
        st.image(uploaded_file, caption="Preview", use_column_width=True)

st.markdown("---")

st.subheader("📝 Ad Copy (Optional - Will Use Defaults)")

col3, col4, col5 = st.columns(3)

with col3:
    headline_1 = st.text_input("Headline 1", value="Your Headline Here")
    headline_2 = st.text_input("Headline 2", value="Another Great Headline")
    headline_3 = st.text_input("Headline 3", value="Final Headline")

with col4:
    description_1 = st.text_area("Description 1", value="Your description text goes here. Make it compelling!", height=100)
    description_2 = st.text_area("Description 2", value="Another description for your ad.", height=100)

with col5:
    business_name = st.text_input("Business Name", value="Your Business")
    final_url = st.text_input("Final URL", value="https://www.example.com", help="Landing page URL")

st.markdown("---")

# Validate button
if st.button("🚀 Validate Creative", type="primary", use_container_width=True):
    
    # Validation
    errors = []
    
    if not use_secrets and not all([developer_token, client_id, client_secret, refresh_token]):
        errors.append("❌ Please provide all API credentials")
    
    if not uploaded_file:
        errors.append("❌ Please upload a creative image")
    
    if not customer_id or not campaign_id:
        errors.append("❌ Please provide Customer ID and Campaign ID")
    
    if errors:
        for error in errors:
            st.error(error)
    else:
        # Progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Step 1: Initialize client
            status_text.text("🔄 Connecting to Google Ads API...")
            progress_bar.progress(10)
            
            if use_secrets:
                client, error = initialize_client(
                    st.secrets["google_ads"]["developer_token"],
                    st.secrets["google_ads"]["client_id"],
                    st.secrets["google_ads"]["client_secret"],
                    st.secrets["google_ads"]["refresh_token"],
                    customer_id
                )
            else:
                client, error = initialize_client(
                    developer_token, client_id, client_secret, refresh_token, customer_id
                )
            
            if error:
                st.error(f"❌ Authentication failed: {error}")
                st.stop()
            
            progress_bar.progress(20)
            
            # Step 2: Find/Create Ad Group
            status_text.text("🔍 Finding ad group...")
            clean_customer_id = customer_id.replace("-", "")
            ad_group_resource_name, ad_group_id, error = find_or_create_ad_group(
                client, clean_customer_id, campaign_id, ad_group_name
            )
            
            if error:
                st.error(f"❌ Ad Group error: {error}")
                st.stop()
            
            progress_bar.progress(40)
            
            # Step 3: Upload image
            status_text.text("📤 Uploading creative...")
            image_data = uploaded_file.read()
            asset_resource_name, asset_id, error = upload_image_asset(
                client, clean_customer_id, image_data, uploaded_file.name
            )
            
            if error:
                st.error(f"❌ Image upload failed: {error}")
                st.stop()
            
            progress_bar.progress(70)
            
            # Step 4: Create paused ad
            status_text.text("🎨 Creating paused ad...")
            ad_resource_name, error = create_paused_ad(
                client, clean_customer_id, ad_group_resource_name, asset_resource_name,
                headline_1, headline_2, headline_3, description_1, description_2,
                business_name, final_url
            )
            
            if error:
                st.error(f"❌ Ad creation failed: {error}")
                st.stop()
            
            progress_bar.progress(100)
            status_text.text("✅ Complete!")
            
            # Success message
            st.balloons()
            
            st.markdown(f"""
            <div class="success-box">
                <h3>✅ Creative Uploaded Successfully!</h3>
                <p><strong>Ad Group ID:</strong> {ad_group_id}</p>
                <p><strong>Ad Resource Name:</strong> {ad_resource_name}</p>
                <p><strong>Status:</strong> PAUSED (Safe - No spend)</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Next steps
            st.subheader("📋 Next Steps")
            
            campaign_url = f"https://ads.google.com/aw/ads?campaignId={campaign_id}"
            
            st.markdown(f"""
            1. **Go to your campaign**: [{campaign_url}]({campaign_url})
            2. **Click 'Ads'** in the left menu
            3. **Find your ad** with the Grey "Paused" icon
            4. **Check the Status column**:
               - ✅ **"Eligible"** = Your creative PASSED validation
               - ❌ **"Disapproved"** = Your creative FAILED (hover for reason)
            """)
            
            st.info("💡 The ad is PAUSED so it will never spend money. It's purely for validation!")
            
        except Exception as e:
            st.error(f"❌ Unexpected error: {str(e)}")
            import traceback
            with st.expander("📋 Error Details"):
                st.code(traceback.format_exc())

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
    Made with ❤️ for advertisers | 
    <a href="https://github.com/nstanley-ui/google_ads_api_checker" target="_blank">GitHub</a> | 
    <a href="https://developers.google.com/google-ads/api/docs/start" target="_blank">API Docs</a>
</div>
""", unsafe_allow_html=True)
