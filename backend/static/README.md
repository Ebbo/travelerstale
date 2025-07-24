# Static Files Directory

This directory contains static files served by the FastAPI backend:

## Subdirectories

- `/audio/` - Generated voice files from ElevenLabs
- `/bgm/` - Background music files (linked from ../bgm folder)

## Notes

- Voice files are cached in the `voice_cache` directory
- Background music files should be placed in the root `bgm` folder
- Supported audio formats: MP3, WAV, OGG, M4A