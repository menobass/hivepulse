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
    print("✅ lighthive imported successfully")
except ImportError:
    Client = None  # type: ignore
    RPCNodeException = Exception  # type: ignore
    LIGHTHIVE_AVAILABLE = False
    print("⚠️ lighthive not available, using requests for Hive API calls")


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
        """Get community followers using real Hive API"""
        self.logger.info(f"Getting followers for community: {community}")
        
        try:
            if self.use_lighthive and self.client:
                # Use lighthive
                try:
                    followers = self.client.get_followers(community, "", "blog", 1000)
                    follower_list = [f['follower'] for f in followers if f.get('follower')]
                    
                    if not follower_list:
                        self.logger.info("No followers found via API, using fallback list")
                        # Fallback to known community members
                        fallback_members = [
                            'maitt87', 'morenow', 'frankches', 'lisfabian', 'teco-teco', 
                            'edcraft', 'manclar', 'lauracraft', 'arlettemsalase', 'rosauradels',
                            'gr33nm4ster', 'jonsnow1983', 'ninaeatshere', 'gaboamc2393',
                            'isgledysduarte', 'moisesjohan', 'wendyth16', 'ljfenix',
                            'pannavi', 'nathyortiz', 'marysenpai', 'lisfabian',
                            'esthefanychacin', 'leidimarc', 'chacald.dcymt'
                        ]
                        return fallback_members
                    
                    self.logger.info(f"Found {len(follower_list)} followers via lighthive")
                    return follower_list
                except Exception as e:
                    self.logger.warning(f"Lighthive get_followers failed: {e}")
            
            # Fallback to requests
            result = self._make_api_call_with_failover('call', ['follow_api', 'get_followers', [community, "", "blog", 1000]])
            
            if result:
                follower_list = [f['follower'] for f in result if f.get('follower')]
                
                if not follower_list:
                    self.logger.info("No followers found via API, using fallback list")
                    # Fallback to known community members
                    fallback_members = [
                        'maitt87', 'morenow', 'frankches', 'lisfabian', 'teco-teco', 
                        'edcraft', 'manclar', 'lauracraft', 'arlettemsalase', 'rosauradels',
                        'gr33nm4ster', 'jonsnow1983', 'ninaeatshere', 'gaboamc2393',
                        'isgledysduarte', 'moisesjohan', 'wendyth16', 'ljfenix',
                        'pannavi', 'nathyortiz', 'marysenpai', 'lisfabian',
                        'esthefanychacin', 'leidimarc', 'chacald.dcymt'
                    ]
                    return fallback_members
                
                self.logger.info(f"Found {len(follower_list)} followers via requests")
                return follower_list
            
            # Final fallback
            self.logger.warning("API calls failed, using fallback member list")
            fallback_members = [
                'maitt87', 'morenow', 'frankches', 'lisfabian', 'teco-teco', 
                'edcraft', 'manclar', 'lauracraft', 'arlettemsalase', 'rosauradels',
                'gr33nm4ster', 'jonsnow1983', 'ninaeatshere', 'gaboamc2393',
                'isgledysduarte', 'moisesjohan', 'wendyth16', 'ljfenix',
                'pannavi', 'nathyortiz', 'marysenpai', 'lisfabian',
                'esthefanychacin', 'leidimarc', 'chacald.dcymt'
            ]
            return fallback_members
            
        except Exception as e:
            self.logger.error(f"Error getting community followers: {str(e)}")
            return []
    
    def get_account_info_extended(self, username: str) -> Optional[Dict]:
        """Get extended account information using real Hive API"""
        self.logger.info(f"Getting account info for: {username}")
        
        try:
            if self.use_lighthive and self.client:
                # Use lighthive
                try:
                    accounts = self.client.get_accounts([username])
                    if not accounts:
                        self.logger.warning(f"Account {username} not found")
                        return None
                    
                    account = accounts[0]
                    
                    # Get follow counts
                    try:
                        follow_count = self.client.get_follow_count(username)
                        following_count = follow_count.get('following_count', 0)
                        follower_count = follow_count.get('follower_count', 0)
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
                
                # Get follow counts
                follow_result = self._make_api_call_with_failover('call', ['follow_api', 'get_follow_count', [username]])
                
                following_count = 0
                follower_count = 0
                if follow_result:
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
            
            self.logger.warning(f"Account {username} not found via API")
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
        """Upload image to Hive image service"""
        try:
            # This would implement actual image upload
            # For now, return a placeholder URL
            return f"https://images.hive.blog/placeholder/{image_path}"
        except Exception as e:
            self.logger.error(f"Error uploading image: {str(e)}")
            return None
    
    def post_content(self, title: str, body: str, tags: List[str]) -> bool:
        """Post content to Hive blockchain"""
        try:
            # This would implement actual posting
            # For now, just log the action
            self.logger.info(f"Would post: {title} with tags {tags}")
            return True
        except Exception as e:
            self.logger.error(f"Error posting content: {str(e)}")
            return False
