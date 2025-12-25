Project: Media File Renamer and Metadata Editor (Python TUI with Textual)

TODO Steps:
1. ✅ Set up Python project structure with UV package manager
2. ✅ Install dependencies: textual, mutagen, pymediainfo, python-magic, pathlib for file handling
3. ✅ Implement recursive directory scanning for video files (*.mkv, *.avi, *.mov, *.mp4, *.wmv, *.flv, *.webm, etc.)
4. ✅ Detect real media container type using mutagen and python-magic
5. ✅ Create Textual TUI application with split layout (left: file tree, right: file details)
6. ✅ Implement file tree display with navigation (keyboard arrows, mouse support)
7. ✅ Add bottom command bar with 'quit', 'open directory', 'scan' commands
8. ✅ Display file details on right side: file size, extension from filename, extension from metadata, file date
9. ✅ Add functionality to select files in the tree and update right panel
10. ✅ Implement detailed metadata display including video/audio/subtitle tracks with colors
11. ✅ Add custom tree styling with file icons and colored guides
12. ✅ Add scrollable details panel
13. ✅ Handle markup escaping for file names with brackets
14. Implement metadata editing capabilities (future steps)
15. Implement file renaming functionality (future steps)