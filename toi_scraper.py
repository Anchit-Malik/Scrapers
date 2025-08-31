#!/usr/bin/env python3
"""
Times of India News Scraper
Scrapes news articles from Times of India homepage
"""

import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime
import time

def scrape_times_of_india():
    """
    Scrape news articles from Times of India homepage
    Returns list of articles with title, URL, image, and source
    """
    url = "https://timesofindia.indiatimes.com/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        print("🔄 Fetching Times of India homepage...")
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        print(f"✅ Successfully fetched page (Status: {response.status_code})")
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        news_articles = []
        
        # Find all article links
        for link in soup.find_all('a', href=True):
            href = link['href']
            
            # Times of India articles have 'articleshow' in URL
            if 'articleshow' in href:
                title = link.get_text().strip()
                
                # Filter meaningful titles
                if title and len(title) > 15:
                    # Get full URL
                    full_url = href if href.startswith('http') else 'https://timesofindia.indiatimes.com' + href
                    
                    # Try to find associated image
                    img_element = link.find('img')
                    img_url = ""
                    if img_element:
                        img_url = img_element.get('src', '')
                        if img_url and not img_url.startswith('http'):
                            img_url = 'https:' + img_url
                    
                    # Determine category based on URL
                    category = "Other"
                    if '/india/' in full_url:
                        category = "India News"
                    elif '/world/' in full_url:
                        category = "World News"
                    elif '/sports/' in full_url:
                        category = "Sports"
                    elif '/business/' in full_url:
                        category = "Business"
                    elif '/entertainment/' in full_url:
                        category = "Entertainment"
                    
                    news_articles.append({
                        'title': title,
                        'url': full_url,
                        'image': img_url,
                        'category': category,
                        'source': 'Times of India',
                        'scraped_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })
        
        # Remove duplicates based on URL
        seen_urls = set()
        unique_articles = []
        for article in news_articles:
            if article['url'] not in seen_urls:
                seen_urls.add(article['url'])
                unique_articles.append(article)
        
        return unique_articles
    
    except requests.RequestException as e:
        print(f"❌ Error fetching webpage: {e}")
        return []
    except Exception as e:
        print(f"❌ Error parsing data: {e}")
        return []

def save_to_csv(articles, filename='times_of_india_articles.csv'):
    """Save articles to CSV file"""
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            
            # Write header
            writer.writerow(['Title', 'URL', 'Image_URL', 'Category', 'Source', 'Scraped_At'])
            
            # Write data
            for article in articles:
                writer.writerow([
                    article['title'],
                    article['url'],
                    article['image'],
                    article['category'],
                    article['source'],
                    article['scraped_at']
                ])
        
        print(f"✅ Data saved to {filename}")
        return True
    
    except Exception as e:
        print(f"❌ Error saving to CSV: {e}")
        return False

def display_statistics(articles):
    """Display scraping statistics"""
    print(f"\n📊 SCRAPING STATISTICS:")
    print("=" * 50)
    print(f"Total articles scraped: {len(articles)}")
    print(f"Articles with images: {sum(1 for a in articles if a['image'])}")
    print(f"Articles without images: {sum(1 for a in articles if not a['image'])}")
    
    # Count by category
    categories = {}
    for article in articles:
        cat = article['category']
        categories[cat] = categories.get(cat, 0) + 1
    
    print(f"\n📂 CATEGORIES:")
    for category, count in sorted(categories.items()):
        print(f"{category}: {count} articles")

def display_sample_articles(articles, count=5):
    """Display sample articles"""
    print(f"\n📰 SAMPLE ARTICLES (Top {count}):")
    print("=" * 80)
    
    for i, article in enumerate(articles[:count], 1):
        print(f"{i}. {article['title']}")
        print(f"   Category: {article['category']}")
        print(f"   URL: {article['url']}")
        if article['image']:
            print(f"   Image: {article['image']}")
        print(f"   Scraped: {article['scraped_at']}")
        print("-" * 80)

def main():
    """Main function to run the scraper"""
    print("🚀 Starting Times of India News Scraper")
    print("=" * 50)
    
    # Scrape articles
    articles = scrape_times_of_india()
    
    if not articles:
        print("❌ No articles found. Exiting.")
        return
    
    # Display results
    display_statistics(articles)
    display_sample_articles(articles)
    
    # Save to CSV
    save_to_csv(articles)
    
    print(f"\n✅ Scraping completed successfully!")
    print(f"📄 Total articles: {len(articles)}")
    print(f"💾 Data saved to: times_of_india_articles.csv")

if __name__ == "__main__":
    main()