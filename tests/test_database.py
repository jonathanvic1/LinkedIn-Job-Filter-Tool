"""
Unit tests for database.py
"""
import pytest
from unittest.mock import Mock, patch
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestDatabaseSingleton:
    """Tests for Database singleton pattern."""
    
    @patch.dict(os.environ, {'SUPABASE_URL': 'https://test.supabase.co', 'SUPABASE_KEY': 'test_key'})
    @patch('database.create_client')
    def test_singleton_returns_same_instance(self, mock_create_client):
        """Test that Database() always returns the same instance."""
        import database
        database.Database._instance = None
        
        db1 = database.Database()
        db2 = database.Database()
        
        assert db1 is db2
    
    @patch.dict(os.environ, {}, clear=True)
    def test_missing_env_vars_sets_client_none(self):
        """Test that missing env vars result in client=None."""
        import database
        database.Database._instance = None
        
        os.environ.pop('SUPABASE_URL', None)
        os.environ.pop('SUPABASE_KEY', None)
        os.environ.pop('SUPABASE_SERVICE_ROLE_KEY', None)
        
        db = database.Database()
        assert db.client is None


class TestBatchSaveDismissedJobsLogic:
    """Tests logic within batch_save_dismissed_jobs."""
    
    @patch.dict(os.environ, {'SUPABASE_URL': 'https://test.supabase.co', 'SUPABASE_KEY': 'test_key'})
    @patch('database.create_client')
    def test_filters_out_none_values(self, mock_create_client):
        """Test that internal logic filters out invalid entries before calling DB."""
        import database
        database.Database._instance = None
        
        mock_client = Mock()
        mock_create_client.return_value = mock_client
        
        db = database.Database()
        
        jobs_data = [
            {'job_id': '123', 'title': 'Job 1'},
            None,
            {'job_id': '456', 'title': 'Job 2'},
            {}  # No job_id, should be filtered
        ]
        
        db.batch_save_dismissed_jobs(jobs_data)
        
        # Verify only valid records were passed to the upsert call
        upserted_data = mock_client.table.return_value.upsert.call_args[0][0]
        assert len(upserted_data) == 2
        assert upserted_data[0]['job_id'] == '123'
        assert upserted_data[1]['job_id'] == '456'
