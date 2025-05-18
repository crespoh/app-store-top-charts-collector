# Contents of app_data_collector.py
import requests
import json
from pymongo import MongoClient
from datetime import datetime
import os

def fetch_top_apps(feed_url, category, region):
    try:
        response = requests.get(feed_url)
        response.raise_for_status()
        data = response.json()
        apps = data.get('feed', {}).get('results', [])
        return [{'app_id': int(app['id']), 'app_name': app['name'], 'category': category, 'region': region} for app in apps]
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {category} apps from {region}: {e}")
        return []
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON for {category} apps from {region}: {e}")
        return []
    except KeyError as e:
        print(f"KeyError in JSON response for {category} apps from {region}: {e}")
        return []

from bson import Binary

def fetch_app_logo(app_id):
    """Fetch the logo URL, image bytes, and bundleId for an app from the iTunes Search API."""
    search_url = f"https://itunes.apple.com/lookup?id={requests.utils.quote(str(app_id))}&entity=software&limit=1"
    try:
        resp = requests.get(search_url)
        resp.raise_for_status()
        result = resp.json()
        if result.get('resultCount', 0) > 0:
            app_info = result['results'][0]
            logo_url = app_info.get('artworkUrl100')
            bundle_id = app_info.get('bundleId')
            track_name = app_info.get('trackName')
            logo_image = None
            if logo_url:
                img_resp = requests.get(logo_url)
                img_resp.raise_for_status()
                logo_image = Binary(img_resp.content)
            return logo_url, logo_image, bundle_id, track_name
    except Exception as e:
        print(f"Error fetching logo for {app_id}: {e}")
    return None, None, None, None

def update_mongodb(mongodb_uri, db_name, collection_name, new_apps):
    client = MongoClient(mongodb_uri)
    db = client[db_name]
    collection = db[collection_name]

    added_count = 0
    for app in new_apps:
        existing_app = collection.find_one({'app_id': app['app_id'], 'region': app['region']})
        if not existing_app:
            app['date_added'] = datetime.now()
            collection.insert_one(app)
            added_count += 1

    client.close()
    print(f"Added {added_count} new apps to MongoDB collection '{collection_name}'.")

if __name__ == "__main__":
    mongodb_uri = os.environ.get("MONGODB_URI")
    db_name = "app_store_data"
    collection_name = "top_apps"
    regions = ["us", "gb", "au", "sg", "my"]  # List of regions

    if not mongodb_uri:
        print("MONGODB_URI environment variable not set. Please configure it in Render.")
        exit()

    all_new_apps = []
    for region in regions:
        feeds = [
            #https://rss.marketingtools.apple.com/api/v2/us/apps/top-free/50/apps.json
            (f"https://rss.marketingtools.apple.com/api/v2/{region}/apps/top-free/50/apps.json", "Top Free"),
            (f"https://rss.marketingtools.apple.com/api/v2/{region}/apps/top-paid/50/apps.json", "Top Paid"),
        ]
        for url, category in feeds:
            top_apps = fetch_top_apps(url, category, region)
            # Enhance each app with logo_url from iTunes Search API
            for app in top_apps:
                logo_url, logo_image, bundle_id, track_name = fetch_app_logo(app['app_id'])
                app['logo_url'] = logo_url
                app['logo_image'] = logo_image
                app['bundle_id'] = bundle_id
                app['track_name'] = track_name
            all_new_apps.extend(top_apps)   

    if all_new_apps:
        update_mongodb(mongodb_uri, db_name, collection_name, all_new_apps)
    else:
        print("No new apps fetched.")