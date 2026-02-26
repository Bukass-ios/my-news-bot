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
    # Broader feed to guarantee new stories for testing
    feed_url = "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en"
    feed = feedparser.parse(feed_url)
    
    print(f"Robot found {len(feed.entries)} potential stories.")
    
    for entry in feed.entries[:5]: 
        url = entry.link
        
        # Check if URL exists to avoid duplicates
        check = supabase.table("articles").select("id").eq("source_url", url).execute()
        
        if not check.data:
            print(f"New story found! Summarizing: {entry.title}")
            try:
                prompt = f"Summarize this news in 3 professional paragraphs: {entry.title}. Link: {url}"
                response = model.generate_content(prompt)
                
                source_name = getattr(entry, 'source', {}).get('title', 'Google News')

                data = {
                    "title": entry.title,
                    "content": response.text,
                    "source_url": url,
                    "source_name": source_name,
                    "category": "Top Stories",
                    "is_approved": True # Make them live immediately for this test
                }
                
                supabase.table("articles").insert(data).execute()
                print("Successfully saved to database!")
                time.sleep(5) 
            except Exception as e:
                print(f"AI error: {e}")
        else:
            print("Article already exists. Skipping...")

if __name__ == "__main__":
    start_bot()
