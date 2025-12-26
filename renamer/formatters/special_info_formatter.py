class SpecialInfoFormatter:
    """Formatter for special info lists"""

    @staticmethod
    def format_special_info(special_info):
        """Convert special info list to comma-separated string"""
        if isinstance(special_info, list):
            return ", ".join(special_info)
        return special_info or ""