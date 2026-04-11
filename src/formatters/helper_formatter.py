
class HelperFormatter:
    
    @staticmethod
    def escape_underscores(text: str) -> str:
        """Escape underscores in a string by prefixing them with a backslash"""
        return text.replace("_", r"\_")
