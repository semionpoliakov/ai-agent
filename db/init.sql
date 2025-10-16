CREATE DATABASE IF NOT EXISTS marketing;

CREATE TABLE IF NOT EXISTS marketing.ad_performance (
  date Date,
  source String,
  campaign_id UInt32,
  campaign_name String,
  country String,
  impressions UInt32,
  clicks UInt32,
  spend Float32,
  conversions UInt32,
  revenue Float32
)
ENGINE = MergeTree()
ORDER BY (date, source);
