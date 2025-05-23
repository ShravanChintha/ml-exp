"""
SSL certificate fix module for Hugging Face Transformers.
This module completely disables SSL verification for testing purposes.
WARNING: This bypasses security measures and should only be used in testing environments.
"""
import os
import ssl
import certifi
import urllib3
import requests
from urllib.request import urlopen

def patch_ssl_context():
    """
    Patch the SSL context to disable verification.
    WARNING: This is insecure and should only be used for testing purposes.
    """
    # Create a new SSL context that doesn't verify certificates
    new_context = ssl._create_unverified_context()
    
    # Replace default HTTPS context with our insecure one
    ssl._create_default_https_context = lambda: new_context
    
    # Disable warnings for urllib3 (used by requests)
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    # Make requests ignore SSL verification by default
    old_merge_environment_settings = requests.Session.merge_environment_settings
    def merge_environment_settings(self, url, proxies, stream, verify, cert):
        settings = old_merge_environment_settings(self, url, proxies, stream, verify, cert)
        settings['verify'] = False
        return settings
    requests.Session.merge_environment_settings = merge_environment_settings
    
    print("⚠️ WARNING: SSL verification has been DISABLED. This is INSECURE and should only be used for testing.")
    return new_context

# Apply the patch when the module is imported
patch_ssl_context()
