import os
import feedparser
import google.generativeai as genai
from supabase import create_client

# These will be hidden safely in GitHub Secrets
URL = os.environ.get("SUPABASE_URL")
KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
AI_KEY = os.environ.get("GEMINI_API_KEY")

supabase = create_client(URL, KEY)
genai.configure(api_key=AI_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

def start_bot():
    # 1. Get news from Google News RSS
    feed = feedparser.parse("https://news.google.com/rss/search?q=technology&hl=en-US")
    
    for entry in feed.entries[:3]: # Let's start with 3 stories
        # 2. Check if we already posted this
        check = supabase.table("articles").select("id").eq("source_url", entry.link).execute()
        
        if not check.data:
            print(f"Summarizing: {entry.title}")
            # 3. AI writes the post
            prompt = f"Write a catchy 3-paragraph blog post about this news: {entry.title}. Source: {entry.link}"
            response = model.generate_content(prompt)
            
            # 4. Save to your Supabase table
            supabase.table("articles").insert({
                "title": entry.title,
                "content": response.text,
                "source_url": entry.link,
                "category": "Tech",
                "is_approved": False 
            }).execute()

if __name__ == "__main__":
    start_bot()
