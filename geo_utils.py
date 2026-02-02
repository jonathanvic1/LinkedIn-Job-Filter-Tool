import re

# Mapping of 2-letter codes to (Full Name, Country)
USA_STATES = {
    'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas', 'CA': 'California',
    'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware', 'FL': 'Florida', 'GA': 'Georgia',
    'HI': 'Hawaii', 'ID': 'Idaho', 'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa',
    'KS': 'Kansas', 'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland',
    'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi', 'MO': 'Missouri',
    'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada', 'NH': 'New Hampshire', 'NJ': 'New Jersey',
    'NM': 'New Mexico', 'NY': 'New York', 'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio',
    'OK': 'Oklahoma', 'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island', 'SC': 'South Carolina',
    'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah', 'VT': 'Vermont',
    'VA': 'Virginia', 'WA': 'Washington', 'WV': 'West Virginia', 'WI': 'Wisconsin', 'WY': 'Wyoming',
    'DC': 'District of Columbia', 'PR': 'Puerto Rico', 'VI': 'Virgin Islands'
}

CANADA_PROVINCES = {
    'AB': 'Alberta', 'BC': 'British Columbia', 'MB': 'Manitoba', 'NB': 'New Brunswick',
    'NL': 'Newfoundland and Labrador', 'NS': 'Nova Scotia', 'NT': 'Northwest Territories',
    'NU': 'Nunavut', 'ON': 'Ontario', 'PE': 'Prince Edward Island', 'QC': 'Quebec',
    'SK': 'Saskatchewan', 'YT': 'Yukon'
}

def normalize_location_name(name):
    """
    Automates generating a 'Corrected Name' for US and Canada locations.
    Returns: "City, State/Province, Country" or None if data is low quality.
    """
    if not name:
        return None
        
    s = name.strip()
    
    # 1. Pattern: "City, ST" (Upper case 2-letter state)
    # Allows for trailing spaces or other artifacts
    match = re.search(r'^([^,]+),\s*([A-Z]{2})(?:\s|,|$)', s)
    if match:
        city = match.group(1).strip().title()
        st_code = match.group(2).upper()
        
        # Check Canada
        if st_code in CANADA_PROVINCES:
            return f"{city}, {CANADA_PROVINCES[st_code]}, Canada"
        
        # Check USA
        if st_code in USA_STATES:
            return f"{city}, {USA_STATES[st_code]}, United States"

    # 2. Pattern: "City, Full State Name" 
    # (Sometimes LinkedIn returns full names already)
    for code, full_name in CANADA_PROVINCES.items():
        if f", {full_name}".lower() in s.lower():
            city = s.split(',')[0].strip().title()
            return f"{city}, {full_name}, Canada"
            
    for code, full_name in USA_STATES.items():
        if f", {full_name}".lower() in s.lower():
            city = s.split(',')[0].strip().title()
            return f"{city}, {full_name}, United States"

    # 3. Filtering Logic for "Shitty" data
    # If it's a single word (no comma) and not a known country/major region, discard
    # This filters: "wide open", "Newcastle Upon Tyne", etc.
    if ',' not in s:
        # Allow major high-level regions if applicable, otherwise discard
        if s.lower() in ['canada', 'united states', 'usa']:
            return s.title()
        return None

    # New requirement: If it doesn't match any of the above patterns (which ensure State/Province),
    # then it doesn't have a "State ID" or clear hierarchy we want.
    # This will now return None for "Newcastle Upon Tyne, UK" etc.
    return None

def is_valid_location(name):
    """Boolean check to filter out non-standard or 'shitty' data."""
    if not name:
        return False
        
    normalized = normalize_location_name(name)
    if normalized is None:
        return False
        
    # Additional noise patterns to discard
    noise_patterns = [
        r'wide\s*open',
        r'work\s*from\s*home',
        r'anywhere',
        r'remote',
        r'opportunity'
    ]
    
    for pattern in noise_patterns:
        if re.search(pattern, name.lower()):
            return False
            
    return True

if __name__ == "__main__":
    # Test Cases
    test_cases = [
        "Toronto, ON",
        "New York, NY",
        "Calgary, Alberta",
        "wide open",
        "Newcastle Upon Tyne",
        "Canada",
        "Vancouver, BC Canada",
        "Austin, TX, US"
    ]
    
    print("--- Geo Utils Test ---")
    for tc in test_cases:
        norm = normalize_location_name(tc)
        valid = is_valid_location(tc)
        print(f"Original: '{tc}' -> Normalized: '{norm}' (Valid: {valid})")
