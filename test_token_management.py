"""
NOVAXA Bot Token Management Test Script
--------------------------------------
This script tests the token management system.
"""

import os
import sys
from security import TokenManager, SecurityMonitor

def main():
    """Main test function."""
    print("=" * 50)
    print("🔑 NOVAXA Bot Token Management Test")
    print("=" * 50)
    print()
    
    os.environ["NOVAXA_MASTER_KEY"] = "test_master_key"
    print("✅ Master key set for testing")
    
    token_manager = TokenManager()
    print("✅ Token manager initialized")
    
    token_id = token_manager.add_token("test_token_123456789", "Test Token", 123456789)
    print(f"✅ Test token added with ID: {token_id}")
    
    tokens = token_manager.get_tokens()
    print("\n📋 Token List:")
    for token in tokens:
        status = "ACTIVE" if token["active"] else token["status"].upper()
        print(f"  - ID: {token['id']}")
        print(f"    Name: {token['name']}")
        print(f"    Status: {status}")
        print(f"    Created: {token['created'][:10]}")
        print()
    
    if token_manager.activate_token(token_id):
        print(f"✅ Token {token_id} activated")
    else:
        print(f"❌ Failed to activate token {token_id}")
    
    active_token = token_manager.get_token()
    print(f"✅ Active token: {active_token[:5]}...{active_token[-5:]}")
    
    security_monitor = SecurityMonitor()
    security_monitor.log_event("token_test", {"token_id": token_id}, 123456789)
    print("✅ Security event logged")
    
    print("\n✅ Token management test completed successfully")

if __name__ == "__main__":
    main()
