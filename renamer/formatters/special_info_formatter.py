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

    @staticmethod
    def format_database_info(database_info) -> str | None:
        """Format database info dictionary or tuple/list into a string"""
        import logging
        import os
        if isinstance(database_info, dict) and 'name' in database_info and 'id' in database_info:
            db_name = database_info['name']
            db_id = database_info['id']
            result = f"{db_name}id-{db_id}"
            return result
        elif isinstance(database_info, (tuple, list)) and len(database_info) == 2:
            db_name, db_id = database_info
            result = f"{db_name}id-{db_id}"
            return result
        if os.getenv("FORMATTER_LOG"):
            logging.info("Returning None")
        return None
