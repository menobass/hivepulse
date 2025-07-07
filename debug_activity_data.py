#!/usr/bin/env python3

"""
Debug script to check what activity data is in the database
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import sqlite3
from datetime import datetime, timedelta
import pytz

def check_activity_data():
    """Check what activity data exists in the database"""
    
    print("🔍 Checking activity data in database...")
    
    connection = sqlite3.connect('pulse_analytics.db')
    cursor = connection.cursor()
    
    # Check what data exists in user_activities table
    cursor.execute("""
        SELECT date, 
               COUNT(DISTINCT username) as active_users,
               SUM(posts_count) as posts,
               SUM(comments_count) as comments,
               SUM(votes_count) as votes
        FROM user_activities 
        GROUP BY date 
        ORDER BY date DESC 
        LIMIT 10
    """)
    
    print("\n📊 Activity data by date:")
    print("Date       | Users | Posts | Comments | Votes")
    print("-----------|-------|-------|----------|-------")
    
    rows = cursor.fetchall()
    for row in rows:
        date, users, posts, comments, votes = row
        print(f"{date:<10} | {users:5} | {posts:5} | {comments:8} | {votes:5}")
    
    if not rows:
        print("❌ No activity data found in database!")
    
    # Check current date and timezone
    ecuador_tz = pytz.timezone('America/Guayaquil')
    utc_now = datetime.utcnow()
    ecuador_now = utc_now.replace(tzinfo=pytz.UTC).astimezone(ecuador_tz)
    
    print(f"\n⏰ Current time info:")
    print(f"UTC now: {utc_now}")
    print(f"Ecuador now: {ecuador_now}")
    print(f"Ecuador date: {ecuador_now.date()}")
    
    # Check if we have data for today
    today_str = ecuador_now.strftime('%Y-%m-%d')
    yesterday_str = (ecuador_now - timedelta(days=1)).strftime('%Y-%m-%d')
    
    cursor.execute("SELECT COUNT(*) FROM user_activities WHERE date = ?", (today_str,))
    today_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM user_activities WHERE date = ?", (yesterday_str,))
    yesterday_count = cursor.fetchone()[0]
    
    print(f"\n📅 Activity records:")
    print(f"Today ({today_str}): {today_count} records")
    print(f"Yesterday ({yesterday_str}): {yesterday_count} records")
    
    # Show recent activity entries
    cursor.execute("""
        SELECT date, username, posts_count, comments_count, votes_count, activity_score
        FROM user_activities 
        WHERE date >= ? 
        ORDER BY date DESC, activity_score DESC
        LIMIT 20
    """, (yesterday_str,))
    
    print(f"\n📋 Recent activity entries:")
    recent_rows = cursor.fetchall()
    if recent_rows:
        print("Date       | Username        | Posts | Comments | Votes | Score")
        print("-----------|-----------------|-------|----------|-------|-------")
        for row in recent_rows:
            date, username, posts, comments, votes, score = row
            print(f"{date:<10} | @{username:<14} | {posts:5} | {comments:8} | {votes:5} | {score:5.1f}")
    else:
        print("  No recent activity entries found")
    
    connection.close()

if __name__ == "__main__":
    check_activity_data()
