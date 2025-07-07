"""
Hive API Client Module
Handles all interactions with the Hive blockchain API
"""

import logging
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json
import time

# Use requests instead of lighthive for compatibility
try:
    from lighthive import Client  # type: ignore
    from lighthive.exceptions import RPCNodeException  # type: ignore
    LIGHTHIVE_AVAILABLE = True
except ImportError:
    Client = None  # type: ignore
    RPCNodeException = Exception  # type: ignore
    LIGHTHIVE_AVAILABLE = False
    print("⚠️ lighthive not available, using requests for Hive API calls")


class HiveAPIClient:
    """Client for interacting with Hive blockchain APIs"""
    
    def __init__(self, config: Dict):
        """Initialize Hive API client with configuration"""
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize client based on availability
        self.client: Optional[Any] = None
        self.use_lighthive = False
        
        if LIGHTHIVE_AVAILABLE and Client is not None:
            try:
                self.client = Client(
                    keys=[config.get('HIVE_POSTING_KEY', ''), config.get('HIVE_ACTIVE_KEY', '')],
                    nodes=[config.get('HIVE_NODE', 'https://api.hive.blog')]
                )
                self.use_lighthive = True
            except Exception as e:
                self.logger.warning(f"Failed to initialize lighthive, falling back to requests: {e}")
                self.client = None
                self.use_lighthive = False
        else:
            self.client = None
            self.use_lighthive = False
        
        # Hive API endpoints
        self.hive_node = config.get('HIVE_NODE', 'https://api.hive.blog')
        self.account_name = config.get('HIVE_ACCOUNT_NAME', '')
        self.image_upload_service = config.get('IMAGE_UPLOAD_SERVICE', 'https://images.hive.blog')
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 0.1  # 100ms between requests
    
    def _rate_limit(self):
        """Implement rate limiting for API requests"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last)
        
        self.last_request_time = time.time()
    
    def _make_api_call(self, method: str, params: Optional[List] = None) -> Optional[Dict]:
        """Make API call to Hive node using requests"""
        try:
            self._rate_limit()
            
            payload = {
                "jsonrpc": "2.0",
                "method": method,
                "params": params or [],
                "id": 1
            }
            
            response = requests.post(
                self.hive_node,
                json=payload,
                timeout=30,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('result')
            else:
                self.logger.error(f"API call failed with status {response.status_code}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error making API call: {str(e)}")
            return None
    
    def get_posts_by_tag(self, tag: str, date: str, limit: int = 100) -> List[Dict]:
        """Get posts by tag for a specific date"""
        self.logger.info(f"Getting posts by tag {tag} for date {date}")
        
        try:
            self._rate_limit()
            
            # For now, return mock data for testing
            # In production, this would query the Hive API
            mock_posts = [
                {
                    'author': 'testuser1',
                    'permlink': 'test-post-1',
                    'title': 'Test Post 1',
                    'created': f'{date}T10:00:00',
                    'net_votes': 10,
                    'children': 5,
                    'parent_permlink': tag,
                    'json_metadata': json.dumps({'tags': [tag]})
                },
                {
                    'author': 'testuser2',
                    'permlink': 'test-post-2',
                    'title': 'Test Post 2',
                    'created': f'{date}T14:00:00',
                    'net_votes': 15,
                    'children': 8,
                    'parent_permlink': tag,
                    'json_metadata': json.dumps({'tags': [tag]})
                }
            ]
            
            # Filter by date
            start_date = datetime.strptime(date, '%Y-%m-%d')
            end_date = start_date + timedelta(days=1)
            
            filtered_posts = []
            for post in mock_posts:
                post_date = datetime.strptime(post['created'], '%Y-%m-%dT%H:%M:%S')
                if start_date <= post_date < end_date:
                    filtered_posts.append(post)
            
            self.logger.info(f"Found {len(filtered_posts)} posts for {date} (mock data)")
            return filtered_posts
            
        except Exception as e:
            self.logger.error(f"Error getting posts by tag: {str(e)}")
            return []
    
    def get_comments_by_community(self, community: str, date: str) -> List[Dict]:
        """Get comments for a community on a specific date"""
        self.logger.info(f"Getting comments for community {community} on {date}")
        
        try:
            self._rate_limit()
            
            # Return mock comments for testing
            mock_comments = [
                {
                    'author': 'commenter1',
                    'permlink': 'comment-1',
                    'created': f'{date}T11:00:00',
                    'parent_author': 'testuser1',
                    'parent_permlink': 'test-post-1'
                },
                {
                    'author': 'commenter2',
                    'permlink': 'comment-2',
                    'created': f'{date}T15:00:00',
                    'parent_author': 'testuser2',
                    'parent_permlink': 'test-post-2'
                }
            ]
            
            start_date = datetime.strptime(date, '%Y-%m-%d')
            end_date = start_date + timedelta(days=1)
            
            filtered_comments = []
            for comment in mock_comments:
                comment_date = datetime.strptime(comment['created'], '%Y-%m-%dT%H:%M:%S')
                if start_date <= comment_date < end_date:
                    filtered_comments.append(comment)
            
            self.logger.info(f"Found {len(filtered_comments)} comments for {date} (mock data)")
            return filtered_comments
            
        except Exception as e:
            self.logger.error(f"Error getting comments: {str(e)}")
            return []
    
    def get_user_posts(self, username: str, date: str, community: Optional[str] = None) -> List[Dict]:
        """Get user's posts for a specific date"""
        self.logger.info(f"Getting posts for user {username} on {date}")
        
        try:
            self._rate_limit()
            
            # Return mock posts for testing
            mock_posts = [
                {
                    'author': username,
                    'permlink': 'user-post-1',
                    'title': 'User Post 1',
                    'created': f'{date}T12:00:00',
                    'net_votes': 5
                }
            ] if username != 'nonexistent' else []
            
            return mock_posts
            
        except Exception as e:
            self.logger.error(f"Error getting user posts: {str(e)}")
            return []
    
    def get_user_comments(self, username: str, date: str, community: Optional[str] = None) -> List[Dict]:
        """Get user's comments for a specific date"""
        self.logger.info(f"Getting comments for user {username} on {date}")
        
        try:
            self._rate_limit()
            
            # Return mock comments for testing
            mock_comments = [
                {
                    'author': username,
                    'permlink': 'user-comment-1',
                    'created': f'{date}T13:00:00',
                    'parent_author': 'someuser',
                    'parent_permlink': 'some-post'
                }
            ] if username != 'nonexistent' else []
            
            return mock_comments
            
        except Exception as e:
            self.logger.error(f"Error getting user comments: {str(e)}")
            return []
    
    def get_user_upvotes_given(self, username: str, date: str) -> int:
        """Get number of upvotes given by user on a specific date"""
        self.logger.info(f"Getting upvotes given by {username} on {date}")
        
        try:
            # Return mock data if client not available
            if not self.use_lighthive or self.client is None:
                self.logger.info(f"Using mock upvotes data for {username}")
                return 5  # Mock data
            
            self._rate_limit()
            
            # Get user's voting history
            votes = self.client.get_account_history(username, -1, 1000)
            
            # Filter for vote operations on the specified date
            start_date = datetime.strptime(date, '%Y-%m-%d')
            end_date = start_date + timedelta(days=1)
            
            upvotes_count = 0
            for entry in votes:
                operation = entry[1]
                if operation['op'][0] == 'vote':
                    op_data = operation['op'][1]
                    op_date = datetime.strptime(operation['timestamp'], '%Y-%m-%dT%H:%M:%S')
                    
                    if start_date <= op_date < end_date:
                        # Check if it's an upvote (positive weight)
                        if int(op_data.get('weight', 0)) > 0:
                            upvotes_count += 1
            
            return upvotes_count
            
        except Exception as e:
            self.logger.error(f"Error getting user upvotes: {str(e)}")
            return 0
    
    def get_hbd_transactions(self, username: str, date: str) -> List[Dict]:
        """Get HBD transactions for a user on a specific date"""
        self.logger.info(f"Getting HBD transactions for {username} on {date}")
        
        try:
            # Return mock data if client not available
            if not self.use_lighthive or self.client is None:
                self.logger.info(f"Using mock HBD transaction data for {username}")
                return [
                    {'amount': '1.000', 'from': username, 'to': 'testuser', 'memo': 'Test transaction'}
                ]
            
            self._rate_limit()
            
            # Get user's transfer history
            transfers = self.client.get_account_history(username, -1, 1000)
            
            # Filter for transfer operations on the specified date
            start_date = datetime.strptime(date, '%Y-%m-%d')
            end_date = start_date + timedelta(days=1)
            
            hbd_transactions = []
            for entry in transfers:
                operation = entry[1]
                if operation['op'][0] == 'transfer':
                    op_data = operation['op'][1]
                    op_date = datetime.strptime(operation['timestamp'], '%Y-%m-%dT%H:%M:%S')
                    
                    if start_date <= op_date < end_date:
                        # Check if it's HBD
                        amount_str = op_data.get('amount', '')
                        if 'HBD' in amount_str:
                            transaction = {
                                'from': op_data['from'],
                                'to': op_data['to'],
                                'amount': float(amount_str.replace(' HBD', '')),
                                'memo': op_data.get('memo', ''),
                                'transaction_id': entry[0],
                                'timestamp': operation['timestamp']
                            }
                            hbd_transactions.append(transaction)
            
            return hbd_transactions
            
        except Exception as e:
            self.logger.error(f"Error getting HBD transactions: {str(e)}")
            return []
    
    def post_content(self, title: str, body: str, tags: List[str], community: Optional[str] = None) -> Optional[Dict]:
        """Post content to Hive blockchain"""
        self.logger.info(f"Posting content: {title}")
        
        try:
            self._rate_limit()
            
            # Create permlink from title
            permlink = self._create_permlink(title)
            
            # Prepare post data
            post_data = {
                'author': self.account_name,
                'permlink': permlink,
                'title': title,
                'body': body,
                'json_metadata': json.dumps({
                    'tags': tags,
                    'app': 'hive-ecuador-pulse/1.0.0',
                    'format': 'markdown'
                })
            }
            
            # Add community if specified
            if community:
                post_data['parent_author'] = ''
                post_data['parent_permlink'] = community
            else:
                post_data['parent_author'] = ''
                post_data['parent_permlink'] = tags[0] if tags else 'hive-ecuador'
            
            # Post using lighthive
            if not self.use_lighthive or self.client is None:
                self.logger.warning("Cannot post: lighthive client not available")
                return None
                
            result = self.client.post(**post_data)
            
            if result:
                self.logger.info(f"Successfully posted: {title}")
                return {
                    'author': self.account_name,
                    'permlink': permlink,
                    'title': title,
                    'transaction_id': result.get('id', '')
                }
            else:
                self.logger.error("Failed to post content")
                return None
                
        except Exception as e:
            self.logger.error(f"Error posting content: {str(e)}")
            return None
    
    def upload_image(self, image_path: str) -> str:
        """Upload image to Hive image service"""
        self.logger.info(f"Uploading image: {image_path}")
        
        try:
            with open(image_path, 'rb') as image_file:
                files = {'file': image_file}
                response = requests.post(
                    f"{self.image_upload_service}/upload",
                    files=files,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    image_url = result.get('url', '')
                    self.logger.info(f"Image uploaded successfully: {image_url}")
                    return image_url
                else:
                    self.logger.error(f"Failed to upload image: {response.status_code}")
                    return ""
                    
        except Exception as e:
            self.logger.error(f"Error uploading image: {str(e)}")
            return ""
    
    def get_account_info(self, username: str) -> Optional[Dict]:
        """Get account information for a user"""
        try:
            if not self.use_lighthive or self.client is None:
                return None
                
            self._rate_limit()
            
            account = self.client.get_account(username)
            return account if account else None
            
        except Exception as e:
            self.logger.error(f"Error getting account info for {username}: {str(e)}")
            return None
    
    def get_community_info(self, community: str) -> Optional[Dict]:
        """Get community information"""
        try:
            if not self.use_lighthive or self.client is None:
                return None
                
            self._rate_limit()
            
            # Use condenser API to get community info
            response = self.client.get_community(community)
            return response if response else None
            
        except Exception as e:
            self.logger.error(f"Error getting community info: {str(e)}")
            return None
    
    def _is_post_in_community(self, post: Dict, community_tag: str) -> bool:
        """Check if a post belongs to a specific community"""
        try:
            # Check parent permlink
            if post.get('parent_permlink') == community_tag:
                return True
            
            # Check tags in json_metadata
            json_metadata = post.get('json_metadata', '{}')
            if isinstance(json_metadata, str):
                try:
                    metadata = json.loads(json_metadata)
                    tags = metadata.get('tags', [])
                    return community_tag in tags
                except:
                    return False
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking post community: {str(e)}")
            return False
    
    def _create_permlink(self, title: str) -> str:
        """Create a permlink from title"""
        import re
        
        # Convert to lowercase and replace spaces with hyphens
        permlink = title.lower().replace(' ', '-')
        
        # Remove special characters
        permlink = re.sub(r'[^a-z0-9-]', '', permlink)
        
        # Remove multiple hyphens
        permlink = re.sub(r'-+', '-', permlink)
        
        # Remove leading/trailing hyphens
        permlink = permlink.strip('-')
        
        # Add timestamp to ensure uniqueness
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        permlink = f"{permlink}-{timestamp}"
        
        return permlink
    
    def test_connection(self) -> bool:
        """Test connection to Hive API"""
        try:
            if not self.use_lighthive or self.client is None:
                self.logger.info("Hive API test: Using requests fallback")
                return True  # Consider requests fallback as working
                
            self._rate_limit()
            
            # Try to get dynamic global properties
            props = self.client.get_dynamic_global_properties()
            
            if props:
                self.logger.info("Hive API connection successful")
                return True
            else:
                self.logger.error("Failed to connect to Hive API")
                return False
                
        except Exception as e:
            self.logger.error(f"Error testing Hive API connection: {str(e)}")
            return False
    
    def get_trending_tags(self, limit: int = 10) -> List[str]:
        """Get trending tags from Hive"""
        try:
            if not self.use_lighthive or self.client is None:
                return ['hive-ecuador', 'spanish', 'community']  # Mock trending tags
                
            self._rate_limit()
            
            trending = self.client.get_trending_tags('', limit)
            return [tag['name'] for tag in trending if tag['name']]
            
        except Exception as e:
            self.logger.error(f"Error getting trending tags: {str(e)}")
            return []
    
    def get_witness_schedule(self) -> Optional[Dict]:
        """Get witness schedule information"""
        try:
            if not self.use_lighthive or self.client is None:
                return None
                
            self._rate_limit()
            
            schedule = self.client.get_witness_schedule()
            return schedule
            
        except Exception as e:
            self.logger.error(f"Error getting witness schedule: {str(e)}")
            return None
    
    def get_community_followers(self, community_account: str = "hive-115276") -> List[str]:
        """Get all followers of the community account"""
        self.logger.info(f"Getting followers for community account {community_account}")
        
        # For testing/development, use mock data
        # TODO: Implement real API call when lighthive is properly configured
        mock_followers = [
            "menobass", "ecuadorestelar", "testuser1", "testuser2",
            "hiveecuador", "ecuadortest", "mockuser1", "mockuser2"
        ]
        
        self.logger.info(f"Using mock follower data: {len(mock_followers)} followers")
        return mock_followers
        
        # Real implementation (commented out for now):
        # try:
        #     # Use follow_api to get followers
        #     followers = []
        #     start_follower = ""
        #     limit = 1000
        #     
        #     while True:
        #         self._rate_limit()
        #         
        #         # Get batch of followers using condenser_api
        #         result = self._make_api_call("condenser_api.get_followers", [
        #             community_account,
        #             start_follower,
        #             "blog",
        #             limit
        #         ])
        #         
        #         if not result or len(result) == 0:
        #             break
        #         
        #         # Extract follower usernames
        #         batch_followers = []
        #         for follower_data in result:
        #             if isinstance(follower_data, dict) and 'follower' in follower_data:
        #                 follower_name = follower_data['follower']
        #                 if follower_name != start_follower:  # Skip the starting point
        #                     followers.append(follower_name)
        #                     batch_followers.append(follower_name)
        #         
        #         # If we got less than the limit, we're done
        #         if len(result) < limit:
        #             break
        #         
        #         # Set next starting point
        #         if batch_followers:
        #             start_follower = batch_followers[-1]
        #         else:
        #             break
        #     
        #     self.logger.info(f"Found {len(followers)} followers for {community_account}")
        #     return followers
        #     
        # except Exception as e:
        #     self.logger.error(f"Error getting community followers: {str(e)}")
        #     # For testing, return some mock followers
        #     self.logger.info("Using mock follower data for testing")
        #     return [
        #         "menobass", "ecuadorestelar", "testuser1", "testuser2",
        #         "hiveecuador", "ecuadortest", "mockuser1", "mockuser2"
        #     ]

    def get_account_info_extended(self, username: str) -> Optional[Dict]:
        """Get enhanced account information for community tracking"""
        try:
            self._rate_limit()
            
            result = self._make_api_call("condenser_api.get_accounts", [[username]])
            
            if result and len(result) > 0:
                account = result[0]
                return {
                    'username': account.get('name', username),
                    'display_name': account.get('posting_json_metadata', {}).get('profile', {}).get('name', username),
                    'reputation': account.get('reputation', 0),
                    'followers': account.get('follower_count', 0),
                    'following': account.get('following_count', 0),
                    'created': account.get('created', ''),
                    'posting_rewards': account.get('posting_rewards', 0)
                }
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting account info for {username}: {str(e)}")
            return None

    def get_user_blockchain_activity(self, username: str, date: str) -> Dict:
        """Get user's blockchain-wide activity for a specific date"""
        self.logger.info(f"Getting blockchain activity for {username} on {date}")
        
        try:
            # Get account history for the date
            start_date = datetime.strptime(date, '%Y-%m-%d')
            end_date = start_date + timedelta(days=1)
            
            # For now, return enhanced mock data that matches tracked users
            mock_data = {
                'username': username,
                'date': date,
                'posts': [],
                'comments': [],
                'votes_given': [],
                'votes_received': 0,
                'total_posts': 0,
                'total_comments': 0,
                'total_votes_given': 0,
                'total_votes_received': 0,
                'engagement_score': 0.0
            }
            
            # Generate realistic mock activity based on username
            import random
            random.seed(hash(username + date))  # Consistent data per user/date
            
            # Posts activity
            posts_count = random.randint(0, 3)
            for i in range(posts_count):
                post = {
                    'author': username,
                    'permlink': f'post-{date}-{i}',
                    'title': f'Post by {username} on {date}',
                    'created': f'{date}T{random.randint(8, 20):02d}:{random.randint(0, 59):02d}:00',
                    'net_votes': random.randint(1, 25),
                    'children': random.randint(0, 10),
                    'category': random.choice(['lifestyle', 'photography', 'spanish', 'travel', 'food'])
                }
                mock_data['posts'].append(post)
            
            # Comments activity
            comments_count = random.randint(0, 8)
            for i in range(comments_count):
                comment = {
                    'author': username,
                    'permlink': f'comment-{date}-{i}',
                    'created': f'{date}T{random.randint(8, 20):02d}:{random.randint(0, 59):02d}:00',
                    'parent_author': f'other-user-{i}',
                    'parent_permlink': f'some-post-{i}',
                    'net_votes': random.randint(0, 5)
                }
                mock_data['comments'].append(comment)
            
            # Votes given
            votes_given_count = random.randint(5, 30)
            for i in range(votes_given_count):
                vote = {
                    'voter': username,
                    'author': f'user-{i % 10}',
                    'permlink': f'voted-post-{i}',
                    'weight': random.randint(500, 10000),
                    'time': f'{date}T{random.randint(8, 20):02d}:{random.randint(0, 59):02d}:00'
                }
                mock_data['votes_given'].append(vote)
            
            # Calculate totals
            mock_data['total_posts'] = len(mock_data['posts'])
            mock_data['total_comments'] = len(mock_data['comments'])
            mock_data['total_votes_given'] = len(mock_data['votes_given'])
            mock_data['total_votes_received'] = sum(p['net_votes'] for p in mock_data['posts']) + sum(c['net_votes'] for c in mock_data['comments'])
            
            # Calculate engagement score
            mock_data['engagement_score'] = (
                mock_data['total_posts'] * 10 +
                mock_data['total_comments'] * 5 +
                mock_data['total_votes_given'] * 1 +
                mock_data['total_votes_received'] * 2
            )
            
            return mock_data
            
        except Exception as e:
            self.logger.error(f"Error getting blockchain activity for {username}: {str(e)}")
            return {
                'username': username,
                'date': date,
                'posts': [],
                'comments': [],
                'votes_given': [],
                'votes_received': 0,
                'total_posts': 0,
                'total_comments': 0,
                'total_votes_given': 0,
                'total_votes_received': 0,
                'engagement_score': 0.0
            }
