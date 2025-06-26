# --- app.py ---
import streamlit as st
from datetime import datetime
from dotenv import load_dotenv
from news_client import NewsAPIClient
from news_utils import display_articles, display_rss_feed
import os

# Load API keys from Streamlit secrets or .env fallback
load_dotenv()

# Streamlit page configuration
st.set_page_config(page_title="📰 Dहooతha", layout="wide")

# Title only (removed multilingual descriptions)
st.title("📰 Dहooతha: Daily News Summarizer")

# Initialize NewsAPI client
client = NewsAPIClient()

# ---- Sidebar Filters ----
st.sidebar.header("📋 Filters")

# News sources
NEWS_SOURCES = {
    "All Sources": None,
    "BBC News": "bbc-news",
    "CNN": "cnn",
    "Reuters": "reuters",
    "The Verge": "the-verge",
    "TechCrunch": "techcrunch",
    "Google News (IN)": "google-news-in",
    "The Times of India": "the-times-of-india",
}
source_name = st.sidebar.selectbox("News Source", list(NEWS_SOURCES.keys()), index=0)
source_code = NEWS_SOURCES[source_name]

# Search query and date input
query = st.sidebar.text_input("Search Keyword", value="Technology")
selected_date = st.sidebar.date_input("Select Date", datetime.now().date())

# Fetch News button
if st.sidebar.button("Fetch News"):
    try:
        date_str = selected_date.strftime("%Y-%m-%d")

        response = client.get_everything(
            q=query,
            sources=source_code,
            from_param=date_str,
            to=date_str,
            language="en",  # Fixed to English only
            sort_by="publishedAt",
            page_size=100
        )

        raw_articles = response.get("articles", [])
        articles = []
        for article in raw_articles:
            published_at = article.get("publishedAt", "")
            if published_at:
                try:
                    dt = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
                    if dt.date() == selected_date:
                        articles.append(article)
                except:
                    continue

        if articles:
            st.success(f"✅ Found {len(articles)} articles for {selected_date.strftime('%Y-%m-%d')}.")
            display_articles(articles)
        else:
            if source_code == "bbc-news" or source_code is None:
                topic_rss_map = {
                    "technology": "https://feeds.bbci.co.uk/news/technology/rss.xml",
                    "tech": "https://feeds.bbci.co.uk/news/technology/rss.xml",
                    "sports": "https://feeds.bbci.co.uk/sport/rss.xml",
                    "business": "https://feeds.bbci.co.uk/news/business/rss.xml",
                    "world": "https://feeds.bbci.co.uk/news/world/rss.xml",
                    "sensex": "https://news.google.com/rss/search?q=sensex"
                }
                topic = query.lower().strip()
                rss_url = topic_rss_map.get(topic, "https://feeds.bbci.co.uk/news/rss.xml")
                display_rss_feed(rss_url, filter_date=selected_date)
            else:
                st.warning("🚫 No news articles were found for your search. Try a different keyword or date.")

    except Exception as e:
        st.error(f"❌ Error fetching news: {e}")
else:
    st.markdown("👈 Use the sidebar to choose filters and click **Fetch News**.")
