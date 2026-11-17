CLIP AI v21 — TWITCH CLIPPER · PREMIUM VIOLET · BY SENYA

WHAT'S NEW
- New standalone Twitch Clipper section in the left navigation and Home modules.
- LIVE mode: read Twitch chat over TLS IRC, retain timestamps, detect chat-activity spikes, add manual highlight markers, and save a local JSONL chat log.
- Optional native Twitch Clip action: with a matching Client ID and OAuth token carrying clips:edit, create a clip on Twitch directly from the live channel and open its Twitch edit page.
- VOD mode: import TwitchDownloader JSON / JSON.GZ, JSONL captured by LIVE mode, CSV, TXT or SRT chat logs; load a Twitch VOD URL or local video; score message bursts and export MP4 clips.
- Select clip length, number of clips and output aspect ratio (9:16 Shorts, original 16:9, or square 1:1).
- Exported clips and session metadata are saved locally and can be downloaded again.
- No new Python package is required for Twitch chat capture; live reading uses Python's standard TLS/socket libraries. VOD URL downloading uses existing yt-dlp; MP4 export uses the app's bundled FFmpeg.
- All previous CLIP AI functions and existing project data are retained.

IMPORTANT LIMITATIONS
- LIVE mode captures chat and stream-relative timestamps; it does not record the video. After the broadcast, use its VOD or a local recording plus the saved chat log to export MP4 clips.
- For stable Twitch IRC access use a Twitch user OAuth access token with the chat:read scope. The native Twitch Clip button additionally requires clips:edit, and the Client ID must match the OAuth token. Anonymous read-only mode is best-effort and Twitch may reject it. The app never sends chat messages.
- Export a chat log (for example with TwitchDownloader) and import it here. Chat offsets must be relative to the beginning of the same VOD. TwitchDownloader can export VOD/clip chat as JSON or timestamped plain text: https://github.com/lay295/TwitchDownloader/releases
- Twitch may restrict or change access to VODs and chat. Use only streams/videos you have permission to process. Some subscriber-only, private, geo-restricted or otherwise protected VODs may not download.

INSTALLATION
1. Close CLIP AI and its command window.
2. Extract the ZIP into its own folder.
3. Double-click INSTALL_V21.bat.
4. Wait for: SUCCESS: CLIP AI v21 installed.
5. Start C:\ClipAI\run_clip_ai.bat.

DATA SAFETY
- The installer backs up C:\ClipAI\app.py to C:\ClipAI\backups.
- Only C:\ClipAI\app.py is replaced.
- Existing data, projects, uploads and outputs are not deleted. Twitch logs and results are stored under data\twitch_clipper and outputs\twitch_clips.
