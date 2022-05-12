# pi_watcher

A rpilocator RSS feed aggregator that posts to a webhook every 5 minutes if there is a new product to be found.

# Usage

1. Copy `.env.example` to `.env`
```bash
cp .env.example .env
```

2. Set `WEBHOOK_URL` to your preferred webhook url and `RSS_URL` to your [rpilocator rss feed](https://rpilocator.com/about.cfm)

3. Install required packages
```bash
python -m pip install -r requirement.txt
```

4. Run this command to start the watcher
```bash
python ./watcher.py
```

## Docker
 Alternatively, run using docker-compose, editting the `docker-compose.yml` file with your environment variables

```bash
docker-compose up
```

# Credit

Credit to [rpilocator](https://rpilocator.com/) for their service.
