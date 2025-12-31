# Decorators package
# Import from new unified cache module
from renamer.cache import cached_method, cached, cached_api, cached_property

# Keep backward compatibility
__all__ = ['cached_method', 'cached', 'cached_api', 'cached_property']