#!/usr/bin/env python3
"""
🏢 Hive Ecuador Business Management Dashboard
Simple CLI tool to manage businesses tracked in daily reports
"""

import sys
import os
from datetime import datetime
from typing import List, Dict

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.manager import DatabaseManager
from utils.hive_api import HiveAPIClient
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BusinessManager:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.hive_api = HiveAPIClient({})
        
    def display_header(self):
        """Display dashboard header"""
        print("\n" + "="*60)
        print("🏢 HIVE ECUADOR BUSINESS MANAGEMENT DASHBOARD")
        print("="*60)
        print("Manage businesses tracked in daily reports")
        print("="*60 + "\n")
    
    def list_businesses(self):
        """List all registered businesses"""
        businesses = self.db_manager.get_registered_businesses()
        
        if not businesses:
            print("📭 No businesses currently registered")
            return
            
        print(f"📊 {len(businesses)} businesses registered:\n")
        print(f"{'#':<3} {'Username':<20} {'Business Name':<25} {'Registered':<12}")
        print("-" * 70)
        
        for i, business in enumerate(businesses, 1):
            username = business.get('username', 'N/A')
            name = business.get('display_name', 'N/A')
            created = business.get('created_at', 'N/A')
            if created != 'N/A':
                try:
                    date_obj = datetime.fromisoformat(created.replace('Z', ''))
                    created = date_obj.strftime('%Y-%m-%d')
                except:
                    created = created[:10]
            
            print(f"{i:<3} @{username:<19} {name:<25} {created:<12}")
    
    def add_business(self):
        """Add a new business"""
        print("\n➕ ADD NEW BUSINESS")
        print("-" * 30)
        
        username = input("Hive Username (without @): ").strip().lower()
        if not username:
            print("❌ Username is required")
            return
            
        # Validate username exists on Hive
        print(f"🔍 Checking if @{username} exists on Hive...")
        account_info = self.hive_api.get_account_info_extended(username)
        if not account_info:
            print(f"❌ Account @{username} not found on Hive blockchain")
            return
            
        business_name = input("Business/Display Name: ").strip()
        if not business_name:
            business_name = username
            
        description = input("Business Description (optional): ").strip()
        
        # Confirm addition
        print(f"\n📋 CONFIRM BUSINESS REGISTRATION:")
        print(f"   Username: @{username}")
        print(f"   Business Name: {business_name}")
        print(f"   Description: {description or 'None'}")
        
        confirm = input("\nAdd this business? (y/N): ").strip().lower()
        if confirm != 'y':
            print("❌ Business registration cancelled")
            return
            
        # Add to database
        success = self.db_manager.add_business(username, business_name, description=description)
        
        if success:
            print(f"✅ Successfully added business: {business_name} (@{username})")
            print("💡 They will appear in tomorrow's HUB FINANCIERO section!")
        else:
            print(f"❌ Failed to add business. Check logs for details.")
    
    def remove_business(self):
        """Remove a business"""
        businesses = self.db_manager.get_registered_businesses()
        
        if not businesses:
            print("📭 No businesses to remove")
            return
            
        print("\n➖ REMOVE BUSINESS")
        print("-" * 25)
        
        # Show numbered list
        for i, business in enumerate(businesses, 1):
            username = business.get('username', 'N/A')
            name = business.get('display_name', 'N/A')
            print(f"{i}. @{username} - {name}")
        
        try:
            choice = int(input(f"\nSelect business to remove (1-{len(businesses)}): "))
            if 1 <= choice <= len(businesses):
                business = businesses[choice - 1]
                username = business.get('username', '')
                name = business.get('display_name', '')
                
                if not username:
                    print("❌ Invalid business data")
                    return
                
                confirm = input(f"Remove @{username} ({name})? (y/N): ").strip().lower()
                if confirm == 'y':
                    # Mark as inactive instead of deleting
                    success = self.db_manager.remove_business(username)
                    if success:
                        print(f"✅ Successfully removed business: {name}")
                    else:
                        print("❌ Failed to remove business")
                else:
                    print("❌ Removal cancelled")
            else:
                print("❌ Invalid selection")
        except ValueError:
            print("❌ Please enter a valid number")
    
    def show_menu(self):
        """Show main menu"""
        while True:
            self.display_header()
            self.list_businesses()
            
            print("\n🔧 ACTIONS:")
            print("1. ➕ Add Business")
            print("2. ➖ Remove Business") 
            print("3. 🔄 Refresh List")
            print("4. 🚪 Exit")
            
            choice = input("\nSelect option (1-4): ").strip()
            
            if choice == '1':
                self.add_business()
                input("\nPress Enter to continue...")
            elif choice == '2':
                self.remove_business()
                input("\nPress Enter to continue...")
            elif choice == '3':
                continue  # Just refresh
            elif choice == '4':
                print("\n👋 Business management closed")
                break
            else:
                print("❌ Invalid option")
                input("Press Enter to continue...")

def main():
    """Main entry point"""
    try:
        manager = BusinessManager()
        manager.show_menu()
    except KeyboardInterrupt:
        print("\n\n👋 Business management closed")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        logger.error(f"Business manager error: {str(e)}")

if __name__ == "__main__":
    main()
