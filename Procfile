web: gunicorn challenge_leaderboard.wsgi --log-file -
worker: celery -A challenge_leaderboard worker
beat: celery -A challenge_leaderboard beat -S djang