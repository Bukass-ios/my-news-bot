import os
import time
import feedparser
import google.generativeai as genai
from supabase import create_client

URL = os.environ.get("SUPABASE_URL")
KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
AI_KEY = os.environ.get("GEMINI_API_KEY")

supabase = create_client(URL, KEY)
genai.configure(api_key=AI_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

def start_bot():
    # We changed this to the General Top Stories feed for a better test
    feed_url = "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en"
    feed = feedparser.parse(feed_url)
    
    print(f"Found {len(feed.entries)} potential stories.")
    
    # Try the first 5 stories
    for entry in feed.entries[:5]: 
        url = entry.link
        
        # Check if URL exists
        check = supabase.table("articles").select("id").eq("source_url", url).execute()
        
        if not check.data:
            print(f"Processing: {entry.title}")
            try:
                prompt = f"Write a professional 3-paragraph news summary for: {entry.title}. Focus on the facts."
                response = model.generate_content(prompt)
                
                # IMPORTANT: We use 'source_name' from the feed if available
                source = getattr(entry, 'source', {'title': 'Google News'}).get('title', 'Google News')

                data = {
                    "title": entry.title,
                    "content": response.text,
                    "source_url": url,
                    "source_name": source,
                    "category": "General",
                    "is_approved": True # Changed to True so it shows up on your site immediately!
                }
                
                result = supabase.table("articles").insert(data).execute()
                print(f"Successfully inserted article!")
                
                time.sleep(5) 
            except Exception as e:
                print(f"Error during AI summary: {e}")
        else:
            print("Article already exists in database. Skipping...")

if __name__ == "__main__":
    start_bot()
