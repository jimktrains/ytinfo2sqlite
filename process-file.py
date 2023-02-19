#!/usr/bin/env python3

import subprocess
import argparse
import json
from dataclasses import dataclass
import os
from lxml import etree
import re
import math
import tempfile
import sqlite3

class BaseSQL:
    def to_insert(self):
        keys = []
        values = []
        for k,v in self.__dict__.items():
            keys.append(k)
            values.append(v)
        insertfields = ",".join(keys)
        insertplaceholders = ','.join(['?' for v in values])
        return (f"insert or ignore into {type(self).__name__} ({insertfields}) values ({insertplaceholders})",
                values
                )

@dataclass
class ytvideo(BaseSQL):
  video_id: str
  title: str
  thumbnail_url: str
  description: str
  uploader: str
  uploader_id: str
  uploader_url: str
  channel_id: str
  channel_url: str
  duration_ms: str
  webpage_url: str
  channel: str
  upload_date: str
  fulltitle: str
  downloaded_at: int

  @staticmethod
  def from_json(j):
      ytv = ytvideo(
              video_id=j['id'],
              title=j['title'],
              thumbnail_url=j['thumbnail'],
              description=j['description'],
              uploader=j['uploader'],
              uploader_id=j['uploader_id'],
              uploader_url=j['uploader_url'],
              channel_id=j['channel_id'],
              channel_url=j['channel_url'],
              duration_ms=math.floor(float(j['duration'])*1000),
              webpage_url=j['webpage_url'],
              channel=j['channel'],
              upload_date=j['upload_date'],
              fulltitle=j['fulltitle'],
              downloaded_at=j['epoch']
      )
      return ytv

@dataclass
class ytvideocategory(BaseSQL):
  video_id: str
  category: str

  @staticmethod
  def from_json(j):
   i = j['id']
   cats = []
   for c in j.get('categories', []):
       cats.append(ytvideocategory(video_id=i, category=c))
   return cats

@dataclass
class ytchapter(BaseSQL):
  video_id: str
  title: str
  start_time_ms: str
  end_time_ms: str

  @staticmethod
  def from_json(j):
    i = j['id']
    chapters = []
    for c in j.get('chapters', []):
        chapters.append(ytchapter(
            video_id=i,
            title=c.get('title'),
            start_time_ms=math.floor(float(c.get('start_time'))*1000),
            end_time_ms=math.floor(float(c.get('end_time'))*1000)
        ))
    return chapters

@dataclass
class ytsponsorblockchapter(BaseSQL):
  video_id: str
  start_time_ms: str
  end_time_ms: str
  category: str
  title: str
  chaptertype: str

  @staticmethod
  def from_json(j):
    i = j['id']
    chapters = []
    for c in j.get('sponsorblock_chapters', []):
        start_time_ms=math.floor(float(c['start_time'])*1000)
        chapters.append((
            ytsponsorblockchapter(
                video_id=i,
                start_time_ms=start_time_ms,
                end_time_ms=math.floor(float(c['end_time'])*1000),
                category=c['category'],
                title=c['title'],
                chaptertype=c['type'],
            ),
            ytsponsorblockchaptercategory.from_json(i, start_time_ms, c.get('_categories', []))))
    return chapters

@dataclass
class ytsponsorblockchaptercategory(BaseSQL):
  video_id: str
  chapter_start_time_ms: str
  category: str
  start_time_ms: str
  end_time_ms: str
  title: str

  @staticmethod
  def from_json(video_id, chapter_start_time_ms, j):
    chapters = []
    for cc in j:
        chapters.append(ytsponsorblockchaptercategory(
          video_id=video_id,
          chapter_start_time_ms=chapter_start_time_ms,
          category=cc[0],
          start_time_ms=math.floor(float(cc[1])*1000),
          end_time_ms=math.floor(float(cc[2])*1000),
          title=cc[3]
        ))
    return chapters
    
@dataclass
class ytvideotag(BaseSQL):
  video_id: str
  tag: str

  @staticmethod
  def from_json(j):
    i = j['id']
    tags = []
    for  tag in j.get('tags', []):
        tags.append(ytvideotag(video_id=1, tag=tag))
    return tags

parser = argparse.ArgumentParser()
parser.add_argument('dbfilename')
parser.add_argument('videojsonfilename')
args = parser.parse_args()

file_name, file_ext = os.path.splitext(args.videojsonfilename)

jsonblob = None
if file_ext == '.mkv':
    result = subprocess.run(['mkvmerge', '--identification-format', 'json', '--identify', args.videojsonfilename], stdout=subprocess.PIPE)
    if result.returncode != 0:
        print(result)
        exit(result.returncode)
    ident = json.loads(result.stdout)
    infojsonattachment = None
    for a in ident.get('attachments',[]):
        if a.get('file_name') == 'info.json':
            infojsonattachment = a
            break

    if infojsonattachment is None:
        print("Not attachment with a name of 'info.json' was found")
        exit(0)

    result = subprocess.run(['mkvextract', '--redirect-output', '/dev/null', args.videojsonfilename, 'attachments', f"{a.get('id')}:/dev/stdout"], stdout=subprocess.PIPE)
    if result.returncode != 0:
        print(result)
        exit(result.returncode)
    jsonblob = result.stdout

elif file_ext == '.json':
    with open(args.videojsonfilename, 'r') as f:
        jsonblob = f.read()
else:
    print(f"{file_ext} isn't supported. Only mkv and json.")
    exit(1)

if jsonblob is None:
    print("No JSON?")
    exit(0)

j = json.loads(jsonblob)

ytv = ytvideo.from_json(j)
ytcs = ytvideocategory.from_json(j)
ytchs = ytchapter.from_json(j)
ytsbchs = ytsponsorblockchapter.from_json(j)
ytts = ytvideotag.from_json(j)

with sqlite3.connect(args.dbfilename) as con:
    cur = con.cursor()
    cur.execute(*ytv.to_insert())
    for ytc in ytcs:
        cur.execute(*ytc.to_insert())
    for ytch in ytchs:
        cur.execute(*ytch.to_insert())
    for (ytsbch, ytsbchcs) in ytsbchs:
        cur.execute(*ytsbch.to_insert())
        for ytsbchc in ytsbchcs:
            cur.execute(*ytsbchc.to_insert())
    for ytt in ytts:
        cur.execute(*ytt.to_insert())
