# YouTube Channel Analysis Commands

Proven `yt-dlp` commands for channel-level analysis. Run these from `terminal()`.

## Channel Metadata

Get description, subscriber count, and title:

```bash
yt-dlp --print '%(title)s|||%(description).500s|||%(channel_follower_count)s' \
  'https://www.youtube.com/@CHANNEL' 2>/dev/null
```

**Warning:** This can take 30+ seconds. If it times out, skip it and rely on the video listing.

## Video Listing

Get the most recent 50 videos with titles and IDs:

```bash
yt-dlp --flat-playlist --dump-single-json \
  'https://www.youtube.com/@CHANNEL/videos' 2>/dev/null | python3 -c "
import json, sys
data = json.load(sys.stdin)
for i, v in enumerate(data.get('entries', [])[:50]):
    print(f'{i+1}. [{v.get(\"id\")}] {v.get(\"title\")} | Duration: {v.get(\"duration\",0)}s')
print(f'Total videos: {len(data.get(\"entries\", []))}')
"
```

**Note:** `--flat-playlist` does not include view counts. For view/like data, fetch individual video metadata or use `--dump-single-json` on specific video URLs.

## Video Metadata (Individual)

Get title, description, and stats for a specific video:

```bash
yt-dlp --print '%(title)s|||%(description).500s|||%(view_count)s|||%(like_count)s|||%(upload_date)s' \
  'https://www.youtube.com/watch?v=VIDEO_ID' 2>/dev/null
```

## Transcript Fetching

Use the `youtube-content` skill's helper script (preferred):

```bash
python3 ~/.hermes/skills/youtube/youtube-content/scripts/fetch_transcript.py "VIDEO_ID" --text-only
```

Fallback via `youtube-transcript-api` directly:

```bash
pip3 install youtube-transcript-api  # one-time
python3 -c "
from youtube_transcript_api import YouTubeTranscriptApi
t = YouTubeTranscriptApi.get_transcript('VIDEO_ID')
print(' '.join([s['text'] for s in t]))
"
```

## Channel Content Categorization

After fetching 30+ video titles, categorize them manually by scanning for patterns:
- Count videos per tool/library (e.g., "Plotly" appears in N titles → data viz category)
- Identify series (consecutive videos on same topic with "PT N" numbering)
- Note which categories are most frequent and which are absent (content gaps)