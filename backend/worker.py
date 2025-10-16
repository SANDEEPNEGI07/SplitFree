"""
RQ Worker for processing background email jobs.
This script runs as a separate process/container and listens to the Redis queue.
"""
import os
import sys
import logging
from dotenv import load_dotenv
import redis
from rq import Worker, Queue

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main worker function"""
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    logger.info(f"🚀 Starting RQ worker...")
    logger.info(f"📡 Connecting to Redis: {redis_url}")
    
    try:
        # Connect to Redis
        redis_conn = redis.from_url(redis_url)
        redis_conn.ping()
        logger.info("Redis connection successful")
        
        # Listen to the 'emails' queue
        listen = ['emails']
        logger.info(f"Listening to queues: {listen}")
        
        # Create worker and start processing jobs
        worker = Worker(listen, connection=redis_conn)
        logger.info("Worker is ready to process jobs!")
        worker.work(with_scheduler=True)
            
    except redis.ConnectionError as e:
        logger.error(f"Failed to connect to Redis: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Worker error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == '__main__':
    main()
