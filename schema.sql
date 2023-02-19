create table ytvideo (
  video_id text primary key,
  title text,
  thumbnail_url text,
  description text,
  uploader text,
  uploader_id text,
  uploader_url text,
  channel_id text,
  channel_url text,
  duration_ms integer,
  webpage_url text,
  channel text,
  upload_date date,
  fulltitle text,
  downloaded_at timestamp
);

create table ytvideocategory (
  video_id text,
  category text,
  primary key(video_id, category),
  foreign key(video_id) references ytvideo(video_id)
);

create table ytchapter (
  video_id text,
  title text,
  start_time_ms integer,
  end_time_ms integer,
  primary key(video_id, start_time_ms),
  foreign key(video_id) references ytvideo(video_id)
);

create table ytsponsorblockchapter (
  video_id text,
  start_time_ms integer,
  end_time_ms integer,
  category text,
  title text,
  chaptertype text,
  foreign key(video_id) references ytvideo(video_id),
  primary key(video_id, start_time_ms)
);

create table ytsponsorblockchaptercategory (
  video_id text,
  chapter_start_time_ms integer,
  category text,
  start_time_ms integer,
  end_time_ms integer,
  title text,
  foreign key(video_id, chapter_start_time_ms) references ytsponsorblockchapter(video_id, start_time_ms)
);

create table ytvideotag (
  video_id text,
  tag text,
  primary key(video_id, tag),
  foreign key(video_id) references ytvideo(video_id)
);
