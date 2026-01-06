#!/usr/bin/env python3
"""
Google Ads Creative Validator
Uploads a creative to a specific campaign as a PAUSED ad to validate against Google's policies.
"""

import os
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

# ============================================================================
# CONFIGURATION
# ============================================================================
CUSTOMER_ID = "3106590821"
CAMPAIGN_ID = "23438621203"
AD_GROUP_NAME = "Creative_Validator_Bin"

# Path to your image file
IMAGE_PATH = "path/to/your/image.jpg"  # UPDATE THIS

# Ad copy (dummy values - you can customize these)
HEADLINE_1 = "Your Headline Here"
HEADLINE_2 = "Another Great Headline"
HEADLINE_3 = "Final Headline"
DESCRIPTION_1 = "Your description text goes here. Make it compelling!"
DESCRIPTION_2 = "Another description for your ad."
BUSINESS_NAME = "Your Business"
FINAL_URL = "https://www.example.com"  # UPDATE THIS


# ============================================================================
# MAIN FUNCTIONS
# ============================================================================

def initialize_client():
    """Initialize Google Ads API client from google-ads.yaml"""
    try:
        client = GoogleAdsClient.load_from_storage()
        print("✓ Google Ads API client initialized")
        return client
    except Exception as e:
        print(f"✗ Failed to initialize client: {e}")
        print("\nMake sure you have a google-ads.yaml file with your credentials.")
        print("See: https://developers.google.com/google-ads/api/docs/client-libs/python/configuration")
        raise


def find_or_create_ad_group(client, customer_id, campaign_id, ad_group_name):
    """
    Find existing ad group by name in the campaign, or create a new one.
    Returns the ad group resource name.
    """
    ga_service = client.get_service("GoogleAdsService")
    
    # Query for existing ad groups in this campaign
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
    
    print(f"\n🔍 Searching for Ad Group '{ad_group_name}' in Campaign {campaign_id}...")
    
    try:
        response = ga_service.search(customer_id=customer_id, query=query)
        
        # Check if ad group exists
        for row in response:
            ad_group_id = row.ad_group.id
            ad_group_resource_name = row.ad_group.resource_name
            print(f"✓ Found existing Ad Group: {ad_group_name} (ID: {ad_group_id})")
            return ad_group_resource_name, ad_group_id
        
        # Ad group doesn't exist, create it
        print(f"✗ Ad Group not found. Creating new Ad Group: {ad_group_name}")
        return create_ad_group(client, customer_id, campaign_id, ad_group_name)
        
    except GoogleAdsException as ex:
        print(f"✗ Error searching for ad group: {ex}")
        raise


def create_ad_group(client, customer_id, campaign_id, ad_group_name):
    """Create a new ad group in the specified campaign."""
    ad_group_service = client.get_service("AdGroupService")
    campaign_service = client.get_service("CampaignService")
    
    # Create ad group operation
    ad_group_operation = client.get_type("AdGroupOperation")
    ad_group = ad_group_operation.create
    
    ad_group.name = ad_group_name
    ad_group.campaign = campaign_service.campaign_path(customer_id, campaign_id)
    ad_group.status = client.enums.AdGroupStatusEnum.ENABLED
    ad_group.type_ = client.enums.AdGroupTypeEnum.DISPLAY_STANDARD
    
    # Set default bid (required, but won't matter since ad will be paused)
    ad_group.cpc_bid_micros = 1000000  # $1.00
    
    try:
        response = ad_group_service.mutate_ad_groups(
            customer_id=customer_id, 
            operations=[ad_group_operation]
        )
        
        ad_group_resource_name = response.results[0].resource_name
        ad_group_id = ad_group_resource_name.split('/')[-1]
        
        print(f"✓ Created Ad Group: {ad_group_name} (ID: {ad_group_id})")
        return ad_group_resource_name, ad_group_id
        
    except GoogleAdsException as ex:
        print(f"✗ Error creating ad group: {ex}")
        raise


def upload_image_asset(client, customer_id, image_path):
    """Upload image to Google Ads and return the asset resource name."""
    asset_service = client.get_service("AssetService")
    
    print(f"\n📤 Uploading image: {image_path}")
    
    # Read image file
    try:
        with open(image_path, "rb") as image_file:
            image_data = image_file.read()
    except FileNotFoundError:
        print(f"✗ Error: Image file not found at {image_path}")
        raise
    
    # Create asset operation
    asset_operation = client.get_type("AssetOperation")
    asset = asset_operation.create
    asset.type_ = client.enums.AssetTypeEnum.IMAGE
    asset.image_asset.data = image_data
    asset.name = os.path.basename(image_path)
    
    try:
        response = asset_service.mutate_assets(
            customer_id=customer_id,
            operations=[asset_operation]
        )
        
        asset_resource_name = response.results[0].resource_name
        asset_id = asset_resource_name.split('/')[-1]
        
        print(f"✓ Image uploaded successfully (Asset ID: {asset_id})")
        return asset_resource_name
        
    except GoogleAdsException as ex:
        print(f"✗ Error uploading image: {ex}")
        raise


def create_paused_responsive_display_ad(
    client, 
    customer_id, 
    ad_group_resource_name,
    image_asset_resource_name,
    headline_1,
    headline_2,
    headline_3,
    description_1,
    description_2,
    business_name,
    final_url
):
    """Create a ResponsiveDisplayAd with PAUSED status."""
    ad_group_ad_service = client.get_service("AdGroupAdService")
    
    print(f"\n🎨 Creating PAUSED Responsive Display Ad...")
    
    # Create ad group ad operation
    ad_group_ad_operation = client.get_type("AdGroupAdOperation")
    ad_group_ad = ad_group_ad_operation.create
    ad_group_ad.ad_group = ad_group_resource_name
    ad_group_ad.status = client.enums.AdGroupAdStatusEnum.PAUSED  # 🔒 SAFETY LOCK
    
    # Configure the ad
    ad = ad_group_ad.ad
    ad.final_urls.append(final_url)
    
    # Create responsive display ad
    responsive_display_ad = ad.responsive_display_ad
    
    # Add headlines
    responsive_display_ad.headlines.append(create_ad_text_asset(client, headline_1))
    responsive_display_ad.headlines.append(create_ad_text_asset(client, headline_2))
    responsive_display_ad.headlines.append(create_ad_text_asset(client, headline_3))
    
    # Add descriptions
    responsive_display_ad.descriptions.append(create_ad_text_asset(client, description_1))
    responsive_display_ad.descriptions.append(create_ad_text_asset(client, description_2))
    
    # Add business name
    responsive_display_ad.business_name = business_name
    
    # Add the uploaded image
    marketing_image = client.get_type("AdImageAsset")
    marketing_image.asset = image_asset_resource_name
    responsive_display_ad.marketing_images.append(marketing_image)
    
    try:
        response = ad_group_ad_service.mutate_ad_group_ads(
            customer_id=customer_id,
            operations=[ad_group_ad_operation]
        )
        
        ad_resource_name = response.results[0].resource_name
        
        print(f"✓ Ad created successfully (Status: PAUSED)")
        print(f"  Resource Name: {ad_resource_name}")
        return ad_resource_name
        
    except GoogleAdsException as ex:
        print(f"\n✗ Error creating ad:")
        for error in ex.failure.errors:
            print(f"  - {error.message}")
            if error.error_code:
                print(f"    Error code: {error.error_code}")
        raise


def create_ad_text_asset(client, text):
    """Helper function to create AdTextAsset."""
    ad_text_asset = client.get_type("AdTextAsset")
    ad_text_asset.text = text
    return ad_text_asset


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    print("=" * 70)
    print("GOOGLE ADS CREATIVE VALIDATOR")
    print("=" * 70)
    print(f"Customer ID: {CUSTOMER_ID}")
    print(f"Campaign ID: {CAMPAIGN_ID}")
    print(f"Ad Group Name: {AD_GROUP_NAME}")
    print("=" * 70)
    
    try:
        # Initialize client
        client = initialize_client()
        
        # Step 1: Find or create ad group
        ad_group_resource_name, ad_group_id = find_or_create_ad_group(
            client, CUSTOMER_ID, CAMPAIGN_ID, AD_GROUP_NAME
        )
        
        # Step 2: Upload image asset
        image_asset_resource_name = upload_image_asset(
            client, CUSTOMER_ID, IMAGE_PATH
        )
        
        # Step 3: Create paused responsive display ad
        ad_resource_name = create_paused_responsive_display_ad(
            client,
            CUSTOMER_ID,
            ad_group_resource_name,
            image_asset_resource_name,
            HEADLINE_1,
            HEADLINE_2,
            HEADLINE_3,
            DESCRIPTION_1,
            DESCRIPTION_2,
            BUSINESS_NAME,
            FINAL_URL
        )
        
        # Success output
        print("\n" + "=" * 70)
        print("✅ SUCCESS - Creative uploaded for validation")
        print("=" * 70)
        print(f"📊 Ad Group ID: {ad_group_id}")
        print(f"🎯 Ad Resource Name: {ad_resource_name}")
        print("\n📋 NEXT STEPS:")
        print(f"1. Go to: https://ads.google.com/aw/ads?campaignId={CAMPAIGN_ID}")
        print("2. Click 'Ads' in the left menu")
        print("3. Find your ad with the Grey 'Paused' icon")
        print("4. Check the 'Status' column:")
        print("   ✅ 'Eligible' = Your creative PASSED Google's validation")
        print("   ❌ 'Disapproved' = Your creative FAILED (hover to see reason)")
        print("=" * 70)
        
    except Exception as e:
        print("\n" + "=" * 70)
        print("❌ SCRIPT FAILED")
        print("=" * 70)
        print(f"Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
