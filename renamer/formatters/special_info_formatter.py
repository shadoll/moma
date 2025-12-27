class SpecialInfoFormatter:
    """Formatter for special info lists"""

    @staticmethod
    def format_special_info(special_info):
        """Convert special info list to comma-separated string"""
        if isinstance(special_info, list):
            # Filter out None values and ensure all items are strings
            filtered = [str(item) for item in special_info if item is not None]
            return ", ".join(filtered)
        return special_info or ""