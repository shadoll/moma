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
14. ✅ Implement file renaming functionality with confirmation dialog
15. ✅ Add proposed name generation based on metadata extraction
16. ✅ Add help screen with key bindings and usage information
17. ✅ Add tree expansion/collapse toggle functionality
18. ✅ Add file refresh functionality to reload metadata for selected file
19. ✅ Optimize tree updates to avoid full reloads after renaming
20. ✅ Add loading indicators for metadata extraction
21. ✅ Add error handling for file operations and metadata extraction
22. 🔄 Implement blue highlighting for changed parts in proposed filename display (show differences between current and proposed names)
23. 🔄 Implement build script to exclude dev commands (bump-version, release) from distributed package
24. Implement metadata editing capabilities (future enhancement)
25. Add batch rename operations (future enhancement)
26. Add configuration file support (future enhancement)
27. Add plugin system for custom extractors/formatters (future enhancement)