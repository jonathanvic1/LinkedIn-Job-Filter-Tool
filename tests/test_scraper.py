"""
Unit tests for linkedin_scraper.py
"""
import pytest
from unittest.mock import Mock, patch
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def mock_load_cookies(self):
    """Helper to mock load_cookies and set csrf_token."""
    self.csrf_token = None

class TestLinkedInScraperInit:
    """Tests for LinkedInScraper internal logic during initialization."""
    
    @patch('linkedin_scraper.db')
    @patch('linkedin_scraper.requests.Session')
    def test_init_with_defaults(self, mock_session, mock_db):
        from linkedin_scraper import LinkedInScraper
        with patch.object(LinkedInScraper, 'load_cookies', mock_load_cookies):
            scraper = LinkedInScraper(cookie_string="test_cookie=value")
            
            assert scraper.location == 'Canada'
            assert scraper.limit_jobs == 0
    
    @patch('linkedin_scraper.db')
    @patch('linkedin_scraper.requests.Session')
    def test_dismiss_titles_lowercase(self, mock_session, mock_db):
        """Test keyword normalization logic."""
        from linkedin_scraper import LinkedInScraper
        with patch.object(LinkedInScraper, 'load_cookies', mock_load_cookies):
            scraper = LinkedInScraper(
                dismiss_keywords=['SENIOR', 'Manager'],
                cookie_string="test=1"
            )
            assert 'senior' in scraper.dismiss_titles
            assert 'manager' in scraper.dismiss_titles
    
    @patch('linkedin_scraper.db')
    @patch('linkedin_scraper.requests.Session')
    def test_company_url_extraction(self, mock_session, mock_db):
        """Test company slug extraction logic."""
        from linkedin_scraper import LinkedInScraper
        with patch.object(LinkedInScraper, 'load_cookies', mock_load_cookies):
            scraper = LinkedInScraper(
                dismiss_companies=[
                    'https://www.linkedin.com/company/google/',
                    'amazon'
                ],
                cookie_string="test=1"
            )
            assert 'google' in scraper.dismiss_companies
            assert 'amazon' in scraper.dismiss_companies

class TestProcessPageResultLogic:
    """Tests for core filtering and stats logic in process_page_result."""
    
    @patch('linkedin_scraper.db')
    @patch('linkedin_scraper.requests.Session')
    def test_empty_page_returns_zeros(self, mock_session, mock_db):
        from linkedin_scraper import LinkedInScraper
        with patch.object(LinkedInScraper, 'load_cookies', mock_load_cookies):
            scraper = LinkedInScraper(cookie_string="test=1")
            stats, dismissed = scraper.process_page_result([])
            assert stats == (0, 0, 0, 0, 0, 0, 0, 0, 0)
    
    @patch('linkedin_scraper.db')
    @patch('linkedin_scraper.requests.Session')
    def test_skips_already_dismissed(self, mock_session, mock_db):
        """Test filtering logic to skip seen jobs."""
        from linkedin_scraper import LinkedInScraper
        mock_db.get_dismissed_job_ids.return_value = {'123'}
        
        with patch.object(LinkedInScraper, 'load_cookies', mock_load_cookies):
            scraper = LinkedInScraper(cookie_string="test=1")
            page_jobs = [{'job_id': '123', 'title': 'Test Job'}]
            stats, dismissed = scraper.process_page_result(page_jobs)
            
            assert stats[0] == 1  # processed
            assert stats[2] == 1  # skipped
            assert stats[1] == 0  # dismissed
    
    @patch('linkedin_scraper.db')
    @patch('linkedin_scraper.requests.Session')
    def test_matches_title_blocklist(self, mock_session, mock_db):
        """Test blocklist matching logic."""
        from linkedin_scraper import LinkedInScraper
        mock_db.get_dismissed_job_ids.return_value = set()
        
        with patch.object(LinkedInScraper, 'load_cookies', mock_load_cookies):
            scraper = LinkedInScraper(
                dismiss_keywords=['senior'],
                cookie_string="test=1"
            )
            # Mock dismiss_job to stop it from trying to hit LinkedIn API
            with patch.object(scraper, 'dismiss_job', return_value={'job_id': '456'}):
                page_jobs = [{'job_id': '456', 'title': 'Senior Engineer'}]
                stats, dismissed = scraper.process_page_result(page_jobs)
                assert stats[1] == 1
                assert len(dismissed) == 1
