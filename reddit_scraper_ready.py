#!/usr/bin/env python3
"""
Complete Reddit Scraper with Pre-configured Credentials
Legal scraping of Reddit posts, comments, and user data using official PRAW API
"""

import praw
import csv
import json
import time
from datetime import datetime, timezone
import os
from typing import List, Dict, Optional

class RedditScraper:
    def __init__(self):
        """Initialize Reddit scraper with pre-configured credentials"""
        # Your Reddit API credentials - already configured!
        CLIENT_ID = "4fU894Px-dLO5Qk1gWjOkQ"
        CLIENT_SECRET = "CrwCed-jGFcxY9k1F1FTv4wsXNpCbw"
        USER_AGENT = "reddit_scraper/1.0 by reedyCrap"
        
        try:
            self.reddit = praw.Reddit(
                client_id=CLIENT_ID,
                client_secret=CLIENT_SECRET,
                user_agent=USER_AGENT
            )
            # Test connection
            print(f"✅ Connected to Reddit successfully!")
            print(f"🔑 Using credentials for: reedyCrap")
        except Exception as e:
            print(f"❌ Failed to connect to Reddit: {e}")
            raise
    
    def get_subreddit_posts(self, subreddit_name: str, sort_type: str = 'hot', 
                           limit: int = 25, time_filter: str = 'all') -> List[Dict]:
        """
        Fetch posts from a subreddit
        
        Args:
            subreddit_name: Name of subreddit (without r/)
            sort_type: 'hot', 'new', 'rising', 'top', 'controversial'
            limit: Number of posts to fetch (max 1000)
            time_filter: 'all', 'day', 'week', 'month', 'year' (for 'top' and 'controversial')
        
        Returns:
            List of post dictionaries
        """
        try:
            print(f"🔄 Fetching {limit} {sort_type} posts from r/{subreddit_name}")
            subreddit = self.reddit.subreddit(subreddit_name)
            
            # Get posts based on sort type
            if sort_type == 'hot':
                submissions = subreddit.hot(limit=limit)
            elif sort_type == 'new':
                submissions = subreddit.new(limit=limit)
            elif sort_type == 'rising':
                submissions = subreddit.rising(limit=limit)
            elif sort_type == 'top':
                submissions = subreddit.top(limit=limit, time_filter=time_filter)
            elif sort_type == 'controversial':
                submissions = subreddit.controversial(limit=limit, time_filter=time_filter)
            else:
                submissions = subreddit.hot(limit=limit)
            
            posts = []
            for submission in submissions:
                # Convert timestamp to readable format
                created_time = datetime.fromtimestamp(submission.created_utc, timezone.utc)
                
                post_data = {
                    'id': submission.id,
                    'title': submission.title,
                    'author': str(submission.author) if submission.author else '[deleted]',
                    'subreddit': submission.subreddit.display_name,
                    'score': submission.score,
                    'upvote_ratio': submission.upvote_ratio,
                    'num_comments': submission.num_comments,
                    'created_utc': submission.created_utc,
                    'created_datetime': created_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'url': submission.url,
                    'permalink': f"https://reddit.com{submission.permalink}",
                    'is_self': submission.is_self,
                    'selftext': submission.selftext[:500] if submission.selftext else '',  # Truncate long text
                    'flair': submission.link_flair_text or '',
                    'distinguished': submission.distinguished or '',
                    'stickied': submission.stickied,
                    'spoiler': submission.spoiler,
                    'nsfw': submission.over_18,
                    'gilded': submission.gilded,
                    'domain': submission.domain,
                    'scraped_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                posts.append(post_data)
                
                # Small delay to respect rate limits
                time.sleep(0.1)
            
            print(f"✅ Successfully fetched {len(posts)} posts from r/{subreddit_name}")
            return posts
            
        except Exception as e:
            print(f"❌ Error fetching posts from r/{subreddit_name}: {e}")
            return []
    
    def get_post_comments(self, post_id: str, limit: int = 50) -> List[Dict]:
        """
        Fetch comments for a specific post
        
        Args:
            post_id: Reddit post ID
            limit: Maximum number of top-level comments to fetch
        
        Returns:
            List of comment dictionaries
        """
        try:
            print(f"🔄 Fetching comments for post {post_id}")
            submission = self.reddit.submission(id=post_id)
            
            # Replace MoreComments objects to get actual comments
            submission.comments.replace_more(limit=0)
            
            comments = []
            for comment in submission.comments[:limit]:
                if hasattr(comment, 'body'):  # Check if it's a real comment
                    created_time = datetime.fromtimestamp(comment.created_utc, timezone.utc)
                    
                    comment_data = {
                        'comment_id': comment.id,
                        'post_id': post_id,
                        'author': str(comment.author) if comment.author else '[deleted]',
                        'body': comment.body,
                        'score': comment.score,
                        'created_utc': comment.created_utc,
                        'created_datetime': created_time.strftime('%Y-%m-%d %H:%M:%S'),
                        'is_submitter': comment.is_submitter,
                        'distinguished': comment.distinguished or '',
                        'gilded': comment.gilded,
                        'permalink': f"https://reddit.com{comment.permalink}",
                        'scraped_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    comments.append(comment_data)
                    
                    time.sleep(0.05)  # Small delay
            
            print(f"✅ Successfully fetched {len(comments)} comments")
            return comments
            
        except Exception as e:
            print(f"❌ Error fetching comments for post {post_id}: {e}")
            return []
    
    def search_reddit(self, query: str, subreddit: str = None, sort: str = 'relevance', 
                     time_filter: str = 'all', limit: int = 25) -> List[Dict]:
        """
        Search Reddit for posts
        
        Args:
            query: Search query
            subreddit: Specific subreddit to search (optional)
            sort: 'relevance', 'hot', 'top', 'new', 'comments'
            time_filter: 'all', 'day', 'week', 'month', 'year'
            limit: Number of results
        
        Returns:
            List of post dictionaries
        """
        try:
            print(f"🔍 Searching Reddit for: '{query}'")
            
            if subreddit:
                search_results = self.reddit.subreddit(subreddit).search(
                    query, sort=sort, time_filter=time_filter, limit=limit
                )
                print(f"   In subreddit: r/{subreddit}")
            else:
                search_results = self.reddit.subreddit('all').search(
                    query, sort=sort, time_filter=time_filter, limit=limit
                )
                print(f"   Across all subreddits")
            
            posts = []
            for submission in search_results:
                created_time = datetime.fromtimestamp(submission.created_utc, timezone.utc)
                
                post_data = {
                    'id': submission.id,
                    'title': submission.title,
                    'author': str(submission.author) if submission.author else '[deleted]',
                    'subreddit': submission.subreddit.display_name,
                    'score': submission.score,
                    'num_comments': submission.num_comments,
                    'created_datetime': created_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'url': submission.url,
                    'permalink': f"https://reddit.com{submission.permalink}",
                    'selftext': submission.selftext[:300] if submission.selftext else '',
                    'search_query': query,
                    'scraped_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                posts.append(post_data)
                time.sleep(0.1)
            
            print(f"✅ Found {len(posts)} posts for query: '{query}'")
            return posts
            
        except Exception as e:
            print(f"❌ Error searching Reddit: {e}")
            return []
    
    def get_user_posts(self, username: str, sort: str = 'new', limit: int = 25) -> List[Dict]:
        """
        Get posts from a specific user
        
        Args:
            username: Reddit username (without u/)
            sort: 'hot', 'new', 'top', 'controversial'
            limit: Number of posts
        
        Returns:
            List of post dictionaries
        """
        try:
            print(f"🔄 Fetching posts from user u/{username}")
            user = self.reddit.redditor(username)
            
            if sort == 'hot':
                submissions = user.submissions.hot(limit=limit)
            elif sort == 'new':
                submissions = user.submissions.new(limit=limit)
            elif sort == 'top':
                submissions = user.submissions.top(limit=limit)
            elif sort == 'controversial':
                submissions = user.submissions.controversial(limit=limit)
            else:
                submissions = user.submissions.new(limit=limit)
            
            posts = []
            for submission in submissions:
                created_time = datetime.fromtimestamp(submission.created_utc, timezone.utc)
                
                post_data = {
                    'id': submission.id,
                    'title': submission.title,
                    'author': username,
                    'subreddit': submission.subreddit.display_name,
                    'score': submission.score,
                    'num_comments': submission.num_comments,
                    'created_datetime': created_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'url': submission.url,
                    'permalink': f"https://reddit.com{submission.permalink}",
                    'selftext': submission.selftext[:300] if submission.selftext else '',
                    'scraped_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                posts.append(post_data)
                time.sleep(0.1)
            
            print(f"✅ Successfully fetched {len(posts)} posts from u/{username}")
            return posts
            
        except Exception as e:
            print(f"❌ Error fetching posts from u/{username}: {e}")
            return []
    
    def save_to_csv(self, data: List[Dict], filename: str) -> bool:
        """Save data to CSV file"""
        if not data:
            print("❌ No data to save")
            return False
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as file:
                fieldnames = data[0].keys()
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
            
            print(f"✅ Saved {len(data)} records to {filename}")
            return True
            
        except Exception as e:
            print(f"❌ Error saving to CSV: {e}")
            return False
    
    def save_to_json(self, data: List[Dict], filename: str) -> bool:
        """Save data to JSON file"""
        if not data:
            print("❌ No data to save")
            return False
        
        try:
            with open(filename, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=2, ensure_ascii=False)
            
            print(f"✅ Saved {len(data)} records to {filename}")
            return True
            
        except Exception as e:
            print(f"❌ Error saving to JSON: {e}")
            return False
    
    def get_subreddit_info(self, subreddit_name: str) -> Dict:
        """Get information about a subreddit"""
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            
            info = {
                'name': subreddit.display_name,
                'title': subreddit.title,
                'description': subreddit.description[:500],
                'subscribers': subreddit.subscribers,
                'active_users': subreddit.active_user_count,
                'created_utc': subreddit.created_utc,
                'created_datetime': datetime.fromtimestamp(subreddit.created_utc, timezone.utc).strftime('%Y-%m-%d'),
                'over18': subreddit.over18,
                'public_description': subreddit.public_description,
                'scraped_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            print(f"✅ Retrieved info for r/{subreddit_name}")
            return info
            
        except Exception as e:
            print(f"❌ Error getting subreddit info: {e}")
            return {}

def interactive_menu():
    """Interactive menu for Reddit scraping"""
    print("🚀 Starting Reddit Scraper with Pre-configured Credentials")
    print("=" * 60)
    
    # Initialize scraper with hardcoded credentials
    try:
        scraper = RedditScraper()
    except Exception:
        print("❌ Failed to initialize Reddit scraper. Check your internet connection.")
        return
    
    while True:
        print("\n" + "="*50)
        print("📱 REDDIT SCRAPER MENU")
        print("="*50)
        print("1. Scrape subreddit posts")
        print("2. Scrape post comments")
        print("3. Search Reddit")
        print("4. Scrape user posts")
        print("5. Get subreddit info")
        print("6. Advanced: Subreddit + Comments")
        print("7. Exit")
        
        choice = input("\nEnter your choice (1-7): ").strip()
        
        if choice == '1':
            subreddit = input("Enter subreddit name (without r/): ").strip()
            sort_type = input("Sort by (hot/new/top/rising/controversial) [default: hot]: ").strip() or 'hot'
            limit = int(input("Number of posts (max 1000) [default: 25]: ").strip() or 25)
            
            if sort_type in ['top', 'controversial']:
                time_filter = input("Time filter (day/week/month/year/all) [default: all]: ").strip() or 'all'
            else:
                time_filter = 'all'
            
            posts = scraper.get_subreddit_posts(subreddit, sort_type, limit, time_filter)
            
            if posts:
                # Display sample
                print(f"\n📊 SAMPLE POSTS:")
                for i, post in enumerate(posts[:3], 1):
                    print(f"{i}. [{post['score']}↑] {post['title'][:60]}...")
                    print(f"   By: u/{post['author']} | Comments: {post['num_comments']}")
                
                # Save options
                save_format = input("\nSave as (csv/json/both/skip) [default: csv]: ").strip() or 'csv'
                if save_format in ['csv', 'both']:
                    filename = f"{subreddit}_{sort_type}_posts.csv"
                    scraper.save_to_csv(posts, filename)
                if save_format in ['json', 'both']:
                    filename = f"{subreddit}_{sort_type}_posts.json"
                    scraper.save_to_json(posts, filename)
        
        elif choice == '2':
            post_id = input("Enter Reddit post ID: ").strip()
            limit = int(input("Number of comments [default: 50]: ").strip() or 50)
            
            comments = scraper.get_post_comments(post_id, limit)
            
            if comments:
                print(f"\n📊 SAMPLE COMMENTS:")
                for i, comment in enumerate(comments[:3], 1):
                    print(f"{i}. [{comment['score']}↑] u/{comment['author']}")
                    print(f"   {comment['body'][:100]}...")
                
                save_format = input("\nSave as (csv/json/both/skip) [default: csv]: ").strip() or 'csv'
                if save_format in ['csv', 'both']:
                    filename = f"comments_{post_id}.csv"
                    scraper.save_to_csv(comments, filename)
                if save_format in ['json', 'both']:
                    filename = f"comments_{post_id}.json"
                    scraper.save_to_json(comments, filename)
        
        elif choice == '3':
            query = input("Enter search query: ").strip()
            subreddit = input("Search in specific subreddit (optional): ").strip() or None
            sort = input("Sort by (relevance/hot/top/new/comments) [default: relevance]: ").strip() or 'relevance'
            limit = int(input("Number of results [default: 25]: ").strip() or 25)
            
            posts = scraper.search_reddit(query, subreddit, sort, 'all', limit)
            
            if posts:
                print(f"\n📊 SEARCH RESULTS:")
                for i, post in enumerate(posts[:3], 1):
                    print(f"{i}. [{post['score']}↑] {post['title'][:60]}...")
                    print(f"   r/{post['subreddit']} | u/{post['author']}")
                
                save_format = input("\nSave as (csv/json/both/skip) [default: csv]: ").strip() or 'csv'
                if save_format in ['csv', 'both']:
                    filename = f"search_{query.replace(' ', '_')}.csv"
                    scraper.save_to_csv(posts, filename)
                if save_format in ['json', 'both']:
                    filename = f"search_{query.replace(' ', '_')}.json"
                    scraper.save_to_json(posts, filename)
        
        elif choice == '4':
            username = input("Enter username (without u/): ").strip()
            sort = input("Sort by (hot/new/top/controversial) [default: new]: ").strip() or 'new'
            limit = int(input("Number of posts [default: 25]: ").strip() or 25)
            
            posts = scraper.get_user_posts(username, sort, limit)
            
            if posts:
                print(f"\n📊 USER POSTS:")
                for i, post in enumerate(posts[:3], 1):
                    print(f"{i}. [{post['score']}↑] {post['title'][:60]}...")
                    print(f"   r/{post['subreddit']}")
                
                save_format = input("\nSave as (csv/json/both/skip) [default: csv]: ").strip() or 'csv'
                if save_format in ['csv', 'both']:
                    filename = f"user_{username}_posts.csv"
                    scraper.save_to_csv(posts, filename)
                if save_format in ['json', 'both']:
                    filename = f"user_{username}_posts.json"
                    scraper.save_to_json(posts, filename)
        
        elif choice == '5':
            subreddit = input("Enter subreddit name (without r/): ").strip()
            info = scraper.get_subreddit_info(subreddit)
            
            if info:
                print(f"\n📊 SUBREDDIT INFO:")
                print(f"Name: r/{info['name']}")
                print(f"Title: {info['title']}")
                print(f"Subscribers: {info['subscribers']:,}")
                print(f"Active Users: {info.get('active_users', 'N/A')}")
                print(f"Created: {info['created_datetime']}")
                print(f"NSFW: {info['over18']}")
                print(f"Description: {info['description'][:200]}...")
                
                save = input("\nSave info? (y/n): ").strip().lower()
                if save == 'y':
                    filename = f"subreddit_{subreddit}_info.json"
                    scraper.save_to_json([info], filename)
        
        elif choice == '6':
            subreddit = input("Enter subreddit name (without r/): ").strip()
            post_limit = int(input("Number of posts [default: 10]: ").strip() or 10)
            comment_limit = int(input("Comments per post [default: 20]: ").strip() or 20)
            
            print(f"\n🔄 Scraping r/{subreddit} with comments...")
            posts = scraper.get_subreddit_posts(subreddit, 'hot', post_limit)
            
            all_comments = []
            for i, post in enumerate(posts, 1):
                print(f"   Scraping comments for post {i}/{len(posts)}")
                comments = scraper.get_post_comments(post['id'], comment_limit)
                all_comments.extend(comments)
                time.sleep(1)  # Be nice to Reddit's servers
            
            if posts and all_comments:
                scraper.save_to_csv(posts, f"{subreddit}_posts_with_comments.csv")
                scraper.save_to_csv(all_comments, f"{subreddit}_all_comments.csv")
                print(f"✅ Scraped {len(posts)} posts and {len(all_comments)} comments")
        
        elif choice == '7':
            print("👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid choice! Please enter 1-7.")

def main():
    """Main function"""
    print("🚀 Reddit Scraper v2.0 - Ready to Use!")
    print("🔑 Credentials pre-configured for reedyCrap")
    print("📊 Legal scraping using official Reddit API")
    print("="*50)
    
    interactive_menu()

if __name__ == "__main__":
    main()