"""Test configuration and utilities"""

import tempfile
import os
import shutil

class TestEnvironment:
    """Setup test environment"""
    
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp()
        
    def cleanup(self):
        """Clean up test environment"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            
    def get_temp_file(self, filename):
        """Get path to temporary file"""
        return os.path.join(self.temp_dir, filename)