from config import PARTY_THRESHOLDS

def get_party_level(people_count):
    """Convert people count to party level (0-10)."""
    for threshold, lvl in PARTY_THRESHOLDS:
        if people_count <= threshold:
            return lvl
    return 10

# For now, analysis will be done manually via Kiro CLI
# The Flask app will call: kiro chat with the image
