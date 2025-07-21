"""
Hive API Client Module
Handles interactions with the Hive blockchain API with multi-node failover
"""

import logging
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json
import time
import random

# Import lighthive if available
try:
    from lighthive.client import Client  # type: ignore
    from lighthive.exceptions import RPCNodeException  # type: ignore
    LIGHTHIVE_AVAILABLE = True
    print("lighthive imported successfully")
except ImportError:
    Client = None  # type: ignore
    RPCNodeException = Exception  # type: ignore
    LIGHTHIVE_AVAILABLE = False
    print("lighthive not available, using requests for Hive API calls")


class HiveAPIClient:
    """Client for interacting with Hive blockchain APIs with multi-node failover"""
    
    def __init__(self, config: Dict):
        """Initialize Hive API client with configuration"""
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Multi-node configuration for failover
        self.hive_nodes = [
            'https://api.hive.blog',
            'https://api.syncad.com',
            'https://api.deathwing.me', 
            'https://hive-api.arcange.eu',
            'https://api.openhive.network',
            'https://rpc.mahdiyari.info',
            'https://hive-api.3speak.tv',
            'https://anyx.io',
            'https://techcoderx.com',
            'https://c0ff33a.hive.blog',
            'https://hive.roelandp.nl'
        ]
        
        self.current_node_index = 0
        self.max_retries = 3
        
        # Initialize client based on availability
        self.client: Optional[Any] = None
        self.use_lighthive = False
        
        if LIGHTHIVE_AVAILABLE and Client is not None:
            self.use_lighthive = True
            self.client = None
            self._initialize_client()
        else:
            self.use_lighthive = False
            self.client = None
            self.logger.warning("lighthive not available, using requests fallback")
        
        # Configuration
        self.account_name = config.get('HIVE_ACCOUNT_NAME', '')
        self.image_upload_service = config.get('IMAGE_UPLOAD_SERVICE', 'https://images.hive.blog')
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 0.1  # 100ms between requests
    
    def _initialize_client(self):
        """Initialize lighthive client with failover"""
        if not self.use_lighthive:
            return
            
        try:
            # Initialize with all nodes for automatic failover
            if Client is not None:
                self.client = Client(nodes=self.hive_nodes)
                self.logger.info(f"Lighthive client initialized with {len(self.hive_nodes)} nodes for failover")
            else:
                raise Exception("Client class is None")
        except Exception as e:
            self.logger.warning(f"Failed to initialize lighthive: {e}")
            self.client = None
            self.use_lighthive = False
    
    def _get_next_node(self) -> str:
        """Get next node for failover"""
        node = self.hive_nodes[self.current_node_index]
        self.current_node_index = (self.current_node_index + 1) % len(self.hive_nodes)
        return node
    
    def _rate_limit(self):
        """Implement rate limiting for API requests"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last)
        
        self.last_request_time = time.time()
    
    def _make_api_call_with_failover(self, method: str, params: Optional[List] = None) -> Optional[Dict]:
        """Make API call with node failover using requests"""
        if not params:
            params = []
            
        for attempt in range(self.max_retries):
            node = self._get_next_node()
            
            try:
                self._rate_limit()
                
                payload = {
                    "jsonrpc": "2.0",
                    "method": method,
                    "params": params,
                    "id": 1
                }
                
                response = requests.post(
                    node,
                    json=payload,
                    timeout=15,
                    headers={'Content-Type': 'application/json'}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if 'result' in data:
                        return data['result']
                    elif 'error' in data:
                        self.logger.warning(f"API error from {node}: {data['error']}")
                        continue
                else:
                    self.logger.warning(f"HTTP error {response.status_code} from {node}")
                    continue
                    
            except Exception as e:
                self.logger.warning(f"Error with node {node}: {str(e)}")
                continue
        
        self.logger.error(f"All nodes failed for method {method}")
        return None
    
    def get_community_followers(self, community: str) -> List[str]:
        """Get community subscribers using real Hive API"""
        self.logger.info(f"Getting subscribers for community: {community}")
        
        try:
            # Try bridge.list_subscribers API first (correct method for community members)
            # Use smaller limit (max 100) and collect in batches if needed
            all_subscribers = []
            start = ""
            limit = 100  # Maximum allowed by API
            
            while True:
                params = {
                    "community": community,
                    "limit": limit
                }
                if start:
                    params["start"] = start
                
                result = self._make_api_call_with_failover('bridge.list_subscribers', [params])
                
                if not result or not isinstance(result, list):
                    self.logger.warning(f"bridge.list_subscribers failed or returned no data")
                    break
                
                # Process subscribers from this batch
                # API returns: [username, role, title, joined_date]
                batch_subscribers = []
                for subscriber in result:
                    username = None
                    
                    if isinstance(subscriber, list) and len(subscriber) > 0:
                        # Handle array format [username, role, title, joined_date]
                        username = str(subscriber[0])
                    elif isinstance(subscriber, dict) and 'account' in subscriber:
                        username = subscriber['account']
                    elif isinstance(subscriber, str):
                        # Sometimes the API returns just usernames
                        username = subscriber
                    
                    # Validate username and exclude system accounts
                    if (username and 
                        username not in ['hiveecuador', 'meno']):
                        batch_subscribers.append(username)
                
                if not batch_subscribers:
                    break  # No more subscribers to process
                
                all_subscribers.extend(batch_subscribers)
                
                # If we got less than the limit, we're done
                if len(batch_subscribers) < limit:
                    break
                
                # Set start for next batch (last username from this batch)
                start = batch_subscribers[-1]
            
            if all_subscribers:
                # Remove duplicates while preserving order
                unique_subscribers = list(dict.fromkeys(all_subscribers))
                self.logger.info(f"Found {len(unique_subscribers)} real subscribers via bridge API")
                return unique_subscribers
            
            # Fallback: try lighthive if available
            if self.use_lighthive and self.client:
                try:
                    # Try using lighthive bridge API with correct limit
                    subscribers = self.client.call('bridge', 'list_subscribers', {
                        'community': community,
                        'limit': 100  # Use valid limit
                    })
                    
                    if subscribers and isinstance(subscribers, list):
                        subscriber_list = []
                        for subscriber in subscribers:
                            username = None
                            
                            if isinstance(subscriber, list) and len(subscriber) > 0:
                                # Handle array format [username, role, title, joined_date]
                                username = str(subscriber[0])
                            elif isinstance(subscriber, dict) and 'account' in subscriber:
                                username = subscriber['account']
                            elif isinstance(subscriber, str):
                                username = subscriber
                            
                            # Validate username and exclude system accounts
                            if (username and 
                                username not in ['hiveecuador', 'meno']):
                                subscriber_list.append(username)
                        
                        if subscriber_list:
                            self.logger.info(f"Found {len(subscriber_list)} subscribers via lighthive bridge")
                            return subscriber_list
                except Exception as e:
                    self.logger.warning(f"Lighthive bridge API failed: {e}")
            
            # If no real subscribers found, use fallback list
            self.logger.info("No subscribers found via API, using fallback list")
            fallback_members = [
                'ibmren', 'supermarketrio', 'felixls1', 'joboss', 'jarivv23', 
                'artmila32', 'pagutl', 'fernando', 'chiquida444', 'caro-lina',
                'jesusromero', 'alzamora', 'irv10', 'venezuelaestalar', 'mariiott87', 
                'veneco224', 'kamarin625', 'dantorior', 'lpzsalvador', 'ikercheb',
                'prospec3d', 'menorkchba', 'diegogla', 'gilcarlos', 'albenis',
                'coolmade', 'bateman', 'netecalibres', 'comozele', 'nateheart',
                'paisapollo', 'zocres', 'rauljeno', 'palmiriam', 'comozale',
                'jpe98', 'jmcantu', 'edbchol', 'glafada', 'melvin73',
                'albento', 'aiverson15', 'yoymiriam', 'edmundas2018',
                'artejean', 'eliezeruniverse', 'bichonfris', 'reolhaber', 'mayjonny',
                'jocadetores', 'zerasole', 'fernanding', 'danielleos',
                'angulus7', 'lilmom3', 'dra-chalito', 'libert', 'melwin134456',
                'jlenzore', 'veronicamartins', 'loquatecnic21', 'franvenezuela',
                'albento3', 'jonznoiz', 'emmanuellcrc', 'menofar12345',
                'carmela', 'cmdc04', 'zamgo4'
            ]
            return fallback_members
            
        except Exception as e:
            self.logger.error(f"Error getting community subscribers: {str(e)}")
            return []
    
    def _is_valid_hive_username(self, username: str) -> bool:
        """
        Validate if a username follows Hive username rules:
        - 3-16 characters
        - Only lowercase letters, numbers, and dashes
        - Cannot start or end with dash
        - Cannot have consecutive dashes
        """
        if not username or not isinstance(username, str):
            return False
        
        # Check length
        if len(username) < 3 or len(username) > 16:
            return False
        
        # Check characters (only lowercase letters, numbers, and dashes)
        if not all(c.islower() or c.isdigit() or c == '-' for c in username):
            return False
        
        # Cannot start or end with dash
        if username.startswith('-') or username.endswith('-'):
            return False
        
        # Cannot have consecutive dashes
        if '--' in username:
            return False
        
        return True

    def get_account_info_extended(self, username: str) -> Optional[Dict]:
        """Get extended account information using real Hive API"""
        
        # Validate username format first
        if not self._is_valid_hive_username(username):
            self.logger.warning(f"Invalid username format: {username}")
            return None
            
        self.logger.info(f"Getting account info for: {username}")
        
        try:
            
            if self.use_lighthive and self.client:
                # Use lighthive
                try:
                    accounts = self.client.get_accounts([username])
                    if not accounts or len(accounts) == 0:
                        self.logger.warning(f"Account {username} not found")
                        return None
                    
                    # Additional validation for accounts response
                    if not isinstance(accounts, list):
                        self.logger.warning(f"Invalid accounts response type for {username}: {type(accounts)}")
                        return None
                    
                    account = accounts[0]
                    
                    # Validate that account is a dict and not a list
                    if not isinstance(account, dict):
                        self.logger.warning(f"Account {username} returned invalid data type: {type(account)} - likely doesn't exist")
                        return None
                    
                    # Validate that the account has the expected structure
                    if 'name' not in account:
                        self.logger.warning(f"Account {username} missing expected fields - likely invalid response")
                        return None
                    
                    # Get follow counts
                    try:
                        follow_count = self.client.get_follow_count(username)
                        if isinstance(follow_count, dict):
                            following_count = follow_count.get('following_count', 0)
                            follower_count = follow_count.get('follower_count', 0)
                        else:
                            following_count = 0
                            follower_count = 0
                    except:
                        following_count = 0
                        follower_count = 0
                    
                    # Parse JSON metadata
                    try:
                        posting_json_metadata = json.loads(account.get('posting_json_metadata', '{}'))
                    except:
                        posting_json_metadata = {}
                    
                    return {
                        'name': account.get('name', username),
                        'created': account.get('created', ''),
                        'reputation': account.get('reputation', 0),
                        'post_count': account.get('post_count', 0),
                        'following_count': following_count,
                        'follower_count': follower_count,
                        'balance': account.get('balance', '0.000 HIVE'),
                        'hbd_balance': account.get('hbd_balance', '0.000 HBD'),
                        'voting_power': account.get('voting_power', 0),
                        'last_post': account.get('last_post', ''),
                        'last_vote_time': account.get('last_vote_time', ''),
                        'profile': posting_json_metadata.get('profile', {}),
                        'json_metadata': posting_json_metadata
                    }
                except Exception as e:
                    self.logger.warning(f"Lighthive get_accounts failed: {e}")
            
            # Fallback to requests
            result = self._make_api_call_with_failover('call', ['database_api', 'get_accounts', [[username]]])
            
            if result and len(result) > 0:
                account = result[0]
                
                # Validate that account is a dict and not a list
                if not isinstance(account, dict):
                    self.logger.debug(f"Account {username} returned invalid data type via requests: {type(account)} - likely doesn't exist")
                    return None
                
                # Get follow counts
                follow_result = self._make_api_call_with_failover('call', ['follow_api', 'get_follow_count', [username]])
                
                following_count = 0
                follower_count = 0
                if follow_result and isinstance(follow_result, dict):
                    following_count = follow_result.get('following_count', 0)
                    follower_count = follow_result.get('follower_count', 0)
                
                # Parse JSON metadata
                try:
                    posting_json_metadata = json.loads(account.get('posting_json_metadata', '{}'))
                except:
                    posting_json_metadata = {}
                
                return {
                    'name': account.get('name', username),
                    'created': account.get('created', ''),
                    'reputation': account.get('reputation', 0),
                    'post_count': account.get('post_count', 0),
                    'following_count': following_count,
                    'follower_count': follower_count,
                    'balance': account.get('balance', '0.000 HIVE'),
                    'hbd_balance': account.get('hbd_balance', '0.000 HBD'),
                    'voting_power': account.get('voting_power', 0),
                    'last_post': account.get('last_post', ''),
                    'last_vote_time': account.get('last_vote_time', ''),
                    'profile': posting_json_metadata.get('profile', {}),
                    'json_metadata': posting_json_metadata
                }
            
            self.logger.debug(f"Account {username} not found via API")
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting account info for {username}: {str(e)}")
            return None
    
    def get_user_blockchain_activity(self, username: str, days: int = 7) -> List[Dict]:
        """Get user's blockchain activity using real Hive API"""
        self.logger.info(f"Getting blockchain activity for {username} (last {days} days)")
        
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            if self.use_lighthive and self.client:
                # Use lighthive
                try:
                    # Get account history (last 1000 operations)
                    history = self.client.get_account_history(username, -1, 1000)
                    
                    activities = []
                    for item in history:
                        if len(item) >= 2:
                            op_data = item[1]
                            timestamp_str = op_data.get('timestamp', '')
                            
                            if timestamp_str:
                                try:
                                    op_time = datetime.strptime(timestamp_str, '%Y-%m-%dT%H:%M:%S')
                                    if op_time >= start_date:
                                        op_type = op_data.get('op', ['unknown', {}])[0]
                                        activities.append({
                                            'timestamp': timestamp_str,
                                            'type': op_type,
                                            'data': op_data
                                        })
                                except:
                                    continue
                    
                    self.logger.info(f"Found {len(activities)} recent activities for {username} via lighthive")
                    return activities
                except Exception as e:
                    self.logger.warning(f"Lighthive get_account_history failed: {e}")
            
            # Fallback to requests
            result = self._make_api_call_with_failover('call', ['account_history_api', 'get_account_history', [username, -1, 1000]])
            
            if result:
                activities = []
                for item in result:
                    if len(item) >= 2:
                        op_data = item[1]
                        timestamp_str = op_data.get('timestamp', '')
                        
                        if timestamp_str:
                            try:
                                op_time = datetime.strptime(timestamp_str, '%Y-%m-%dT%H:%M:%S')
                                if op_time >= start_date:
                                    op_type = op_data.get('op', ['unknown', {}])[0]
                                    activities.append({
                                        'timestamp': timestamp_str,
                                        'type': op_type,
                                        'data': op_data
                                    })
                            except:
                                continue
                
                self.logger.info(f"Found {len(activities)} recent activities for {username} via requests")
                return activities
            
            self.logger.warning(f"No activity data found for {username}")
            return []
            
        except Exception as e:
            self.logger.error(f"Error getting blockchain activity for {username}: {str(e)}")
            return []
    
    def upload_image(self, image_path: str) -> Optional[str]:
        """Upload image to Imgur (requires IMGUR_CLIENT_ID in environment)"""
        try:
            import requests
            import os
            import base64
            
            if not os.path.exists(image_path):
                self.logger.error(f"Image file not found: {image_path}")
                return None
            
            # Get Imgur client ID from environment
            client_id = os.getenv('IMGUR_CLIENT_ID')
            if not client_id or client_id == 'your_imgur_client_id_here':
                self.logger.error("IMGUR_CLIENT_ID not set in environment variables")
                self.logger.info("Please get a free client ID from: https://api.imgur.com/oauth2/addclient")
                return None
            
            # Use Imgur API v3
            api_base = "https://api.imgur.com/3"
            
            # Read and encode image
            with open(image_path, 'rb') as image_file:
                image_bytes = image_file.read()
                image_b64 = base64.b64encode(image_bytes).decode('utf-8')
            
            headers = {
                'Authorization': f'Client-ID {client_id}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'image': image_b64,
                'type': 'base64',
                'title': f'Hive Ecuador Pulse - {os.path.basename(image_path)}',
                'description': 'Analytics chart from Hive Ecuador Pulse Bot'
            }
            
            response = requests.post(
                f"{api_base}/image",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    url = result['data']['link']
                    self.logger.info(f"Image uploaded to Imgur: {url}")
                    return url
                else:
                    self.logger.error(f"Imgur upload failed: {result.get('data', {}).get('error', 'Unknown error')}")
                    return None
            else:
                self.logger.error(f"Imgur API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error uploading image: {str(e)}")
            return None
    
    def post_content(self, title: str, body: str, tags: List[str]) -> bool:
        """Post content to Hive blockchain using lighthive Operation class"""
        try:
            if not self.use_lighthive or self.client is None:
                self.logger.error("Cannot post: lighthive client not available")
                return False
            
            # Get posting key from environment
            import os
            posting_key = os.getenv('HIVE_POSTING_KEY')
            if not posting_key:
                self.logger.error("Cannot post: HIVE_POSTING_KEY not set in environment")
                return False
            
            # Create permlink from title
            import re
            from datetime import datetime
            
            # Clean title for permlink
            permlink = re.sub(r'[^a-zA-Z0-9\s-]', '', title.lower())
            permlink = re.sub(r'\s+', '-', permlink.strip())
            # Add timestamp to make permlinks unique and prevent editing previous posts
            permlink = f"pulse-{datetime.now().strftime('%Y-%m-%d-%H%M%S')}-{permlink[:30]}"
            
            # Set up client with posting key
            from lighthive.client import Client
            from lighthive.datastructures import Operation
            posting_client = Client(keys=[posting_key])
            
            # Create comment operation following lighthive documentation exactly
            operation = Operation('comment', {
                'parent_author': None,  # None for main posts (not empty string)
                'parent_permlink': tags[0] if tags else 'hive-ecuador',  # First tag as parent_permlink
                'author': self.account_name,
                'permlink': permlink,
                'title': title,
                'body': body,
                'json_metadata': json.dumps({  # Must be JSON string, not dict
                    'tags': tags,
                    'app': 'hive-ecuador-pulse/1.0.0',
                    'format': 'markdown'
                })
            })
            
            # Broadcast operation synchronously to get transaction ID
            result = posting_client.broadcast_sync(operation)
            
            if result and 'id' in result:
                post_url = f"https://hive.blog/@{self.account_name}/{permlink}"
                self.logger.info(f"Successfully posted to Hive: {post_url} (TX: {result['id']})")
                return True
            else:
                self.logger.error(f"Failed to post to Hive blockchain - unexpected result: {result}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error posting content: {str(e)}")
            return False
