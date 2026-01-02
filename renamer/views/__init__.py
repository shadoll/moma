"""Views package - assembles formatted data for display.

Views compose multiple formatters to create complex display outputs.
Unlike formatters which transform single values, views aggregate and
orchestrate multiple formatters to build complete UI panels.
"""

from .proposed_filename import ProposedFilenameView
from .media_panel import MediaPanelView

__all__ = [
    'ProposedFilenameView',
    'MediaPanelView',
]
