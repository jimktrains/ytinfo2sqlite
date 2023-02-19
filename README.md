# ytinfo2sqlite
Converts the info.json from yt-dlp/youtube-dl either embedded into an mkv or as
a sidecar into a sqlite databse.

To process files in subdirectories, you can use

```sh
find . -iname \*mkv  -print0 | parallel --null --bar './process-file.py videos.sqlite3 {}'
```

sqlite3 will work with multiple processes sharing the same database. `parallel`
will correctly quote the filename passed in via `{}`, so there's no need to
quote it in the command template.

# Sample file '20221121 - Hacking a weird TV censoring device.info.json'

The video was optained via.

```sh
yt-dlp \
  --continue \
  --retries 3 \
  --no-overwrites \
  --write-info-json \
  --write-auto-subs \
  --embed-thumbnail \
  --sub-langs "en,it,es,fr,de" \
  --embed-metadata \
  --embed-chapters \
  --embed-info-json \
  --embed-subs \
  --download-archive "ytdlarchive" \
  --format "bestvideo[height<=720]+bestaudio/best[height<=720]" \
  --retry-sleep exp=1::2 \
  --sleep-requests 5 \
  --sleep-interval 30 \
  --sponsorblock-mark all \
  --sponsorblock-chapter-title "[SponsorBlock][%(category)s]: %(name)s" \
  --merge-output-format "mkv" \
  --output "%(channel)s/%(upload_date)s - %(title)s.%(ext)s" \
  "https://www.youtube.com/watch?v=a6EWIh2D1NQ"
```

(When I need to view the json as formatted in the terminal, I just
```sh
cat "20221121 - Hacking a weird TV censoring device.info.json" | jq | less
```
# Citations

```
Tange, O. (2022, October 22). GNU Parallel 20221022 ('Nord Stream').
Zenodo. https://doi.org/10.5281/zenodo.7239559
```
