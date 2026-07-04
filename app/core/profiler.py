import yaml
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))


class InfrastructureProfiler:
    """Checks if threat articles are relevant to user's tech stack"""
    
    def __init__(self, profile_path=None):
        if profile_path is None:
            profile_path = Path(__file__).parent / "profiles" / "default.yaml"
        
        if profile_path.exists():
            with open(profile_path) as f:
                self.profile = yaml.safe_load(f)
        else:
            self.profile = None
            print("Profile not found")  # Debug
    
    def check_relevance(self, article_text: str) -> dict:
        """Check if article mentions tech from user's stack"""
        if not self.profile:
            return {"priority": "LOW", "matched": [], "reason": "No profile"}
        
        text_lower = article_text.lower()
        matched = []
        
        for category, technologies in self.profile.get('infrastructure', {}).items():
            if isinstance(technologies, list):
                for tech in technologies:
                    if tech.lower() in text_lower:
                        matched.append(tech)
        
        if matched:
            return {
                "priority": "HIGH",
                "matched": matched,
                "reason": f"Matches: {', '.join(matched)}"
            }
        
        return {
            "priority": "LOW",
            "matched": [],
            "reason": "No stack match"
        }


if __name__ == "__main__":
    profiler = InfrastructureProfiler()
    
    # Test with a match
    result = profiler.check_relevance("New AWS S3 bucket exploit allows data theft")
    print(f"AWS article: {result}")
    
    # Test with no match
    result = profiler.check_relevance("Windows Active Directory zero-day found")
    print(f"Windows article: {result}")
