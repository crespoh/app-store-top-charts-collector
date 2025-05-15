# 📱 App Store Top Charts Collector

A Python-based scraper for collecting top app data from the Apple App Store, including app name, ID, developer, category, rank, and icon. Optionally, the icon PNG can be downloaded and stored.

---

## 🚀 Features

- Collect top-ranked apps from the iOS App Store
- Extract metadata like:
  - App name
  - App ID
  - Developer name
  - Category
  - Ranking
  - Icon URL (and optionally download PNG)
- Output results to a JSON or MongoDB database
- Easy to customize for different countries, categories, and app types

---

## 🛠 Requirements

- Python 3.7+
- pip packages:
  - `requests`
  - `beautifulsoup4`
  - `pymongo` *(optional, if using MongoDB)*

Install dependencies:

```bash
pip install -r requirements.txt
