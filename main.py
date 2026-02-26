import os
import time  # Added this
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
    feed = feedparser.parse("https://news.google.com/rss/search?q=technology&hl=en-US")
    
    # Let's limit it to just 2 articles for the first test to stay under quota
    for entry in feed.entries[:2]: 
        check = supabase.table("articles").select("id").eq("source_url", entry.link).execute()
        
        if not check.data:
            print(f"Summarizing: {entry.title}")
            try:
                prompt = f"Write a catchy 3-paragraph blog post about this news: {entry.title}. Source: {entry.link}"
                response = model.generate_content(prompt)
                
                supabase.table("articles").insert({
                    "title": entry.title,
                    "content": response.text,
                    "source_url": entry.link,
                    "category": "Tech",
                    "is_approved": False 
                }).execute()
                
                print("Success! Waiting 10 seconds before next one...")
                time.sleep(10)  # This prevents the 'Quota Error' you saw
            except Exception as e:
                print(f"AI was too busy: {e}")
                continue

if __name__ == "__main__":
    start_bot()
