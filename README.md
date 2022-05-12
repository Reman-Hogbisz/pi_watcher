# pi_watcher

A rpilocator RSS feed aggregator that posts to a webhook every 5 minutes if there is a new product to be found in the US.

# Usage

1. Set `WEBHOOK_URL` to your preferred webhook url and `RSS_FEED_URL` to your rpilocator rss feed

2. Run this command to start the watcher

```bash
python ./webhook.py
```

3. Or, alternatively, run using docker-compose, editting the `docker-compose.yml` file with your environment variables

```bash
docker-compose up
```

# Credit

Credit to [rpilocator](https://rpilocator.com/) for their service.
