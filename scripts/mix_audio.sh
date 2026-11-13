#!/usr/bin/env bash
set -euo pipefail

VO_FILE="assets/audio/voiceover.mp3"
COMBINED_VID="renders/final/combined_video.mp4"
AMBIENT_WAV="renders/final/ambient_pad.wav"
FINAL_OUT="renders/final/jakarta_lowpoly_1080x1920.mp4"

VO_DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$VO_FILE")
DUR=$(awk -v v="$VO_DUR" 'BEGIN{t=v+2.5; d=int(t); if (d<t) d++; print d}')
FRAMES=$((DUR*30))
FADE_ST=$(awk -v d="$DUR" 'BEGIN{print d-2.5}')

echo "Voiceover Duration: ${VO_DUR}s | Target Total Duration: ${DUR}s (${FRAMES} frames @ 30fps)"

# 1. Concat all 10 rendered scene MP4s
> renders/scenes/scenes.txt
for i in $(seq -w 1 10); do
  echo "file 'scene_${i}.mp4'" >> renders/scenes/scenes.txt
done

ffmpeg -y -f concat -safe 0 -i renders/scenes/scenes.txt -c copy "$COMBINED_VID"

# 2. Generate soft synthetic ambient pad (C major warm chord, 48kHz stereo)
ffmpeg -y -f lavfi -i "aevalsrc=0.08*sin(2*PI*261.63*t)+0.06*sin(2*PI*329.63*t)+0.06*sin(2*PI*392.00*t)+0.04*sin(2*PI*493.88*t):s=48000:c=stereo:d=${DUR}" "$AMBIENT_WAV"

# 3. Mix Voiceover (delayed 1.0s) + Ambient Pad with Sidechain Ducking & 2.5s Outro Fade
ffmpeg -y -i "$COMBINED_VID"   -i "$VO_FILE"   -stream_loop -1 -i "$AMBIENT_WAV"   -filter_complex "\
[1:a]adelay=1000:all=1,apad=whole_dur=${DUR},atrim=0:${DUR},asetpts=PTS-STARTPTS,asplit=2[vo1][vo2];\
[2:a]atrim=0:${DUR},asetpts=PTS-STARTPTS,volume=0.28,afade=t=out:st=${FADE_ST}:d=2.5[bg];\
[bg][vo1]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=300[duck];\
[duck][vo2]amix=inputs=2:duration=longest:dropout_transition=0,volume=2,alimiter=limit=0.95[aout]"   -map 0:v -map "[aout]"   -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p -r 30 -frames:v "$FRAMES"   -c:a aac -b:a 192k -ar 48000 -t "$DUR"   -movflags +faststart "$FINAL_OUT"

echo "=== Final Video Exported: $FINAL_OUT ==="
