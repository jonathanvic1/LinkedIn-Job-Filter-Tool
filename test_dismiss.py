#!/ env python3
import os
import sys
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from linkedin_scraper import LinkedInScraper

def test_dismiss(job_id, dismiss_urn=None):
    if not os.path.exists(".env"):
        print("❌ .env file not found. Please ensure it contains LINKEDIN_COOKIES.")
        return

    load_dotenv()
    
    # Initialize scraper with defaults
    scraper = LinkedInScraper(
        keywords="",
        location="",
        limit_jobs=1
    )
    
    print(f"🚀 Attempting to dismiss Job ID: {job_id}")
    if dismiss_urn:
        print(f"📦 Dismiss URN: {dismiss_urn}")
    else:
        # Construct fallback URN
        dismiss_urn = f"urn:li:fsd_jobPostingRelevanceFeedback:urn:li:fsd_jobPosting:{job_id}"
        print(f"📦 Constructing fallback Dismiss URN: {dismiss_urn}")

    result = scraper.dismiss_job(
        job_id=job_id,
        title="Verification Test",
        company="Mock Company",
        location="Earth",
        dismiss_urn=dismiss_urn
    )
    
    if result:
        print("✅ SUCCESS: Job dismissed correctly!")
    else:
        print("❌ FAILURE: Dismissal failed. Check logs above.")

if __name__ == "__main__":
    # Use one of the job IDs that failed in the user's logs
    # e.g., 4368414650
    target_id = sys.argv[1] if len(sys.argv) > 1 else "4368153098"
    test_dismiss(target_id)
