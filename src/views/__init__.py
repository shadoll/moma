"""Views package - assembles formatted data for display.

Views compose multiple formatters to create complex display outputs.
Unlike formatters which transform single values, views aggregate and
orchestrate multiple formatters to build complete UI panels.
"""

from .proposed_filename import ProposedFilenameView
from .media_panel import MediaPanelView
from .open_screen import OpenScreen
from .help_screen import HelpScreen
from .rename_confirm_screen import RenameConfirmScreen
from .settings_screen import SettingsScreen
from .convert_confirm_screen import ConvertConfirmScreen
from .delete_confirm_screen import DeleteConfirmScreen

__all__ = [
    'ProposedFilenameView',
    'MediaPanelView',
    'OpenScreen',
    'HelpScreen',
    'RenameConfirmScreen',
    'SettingsScreen',
    'ConvertConfirmScreen',
    'DeleteConfirmScreen',
]
