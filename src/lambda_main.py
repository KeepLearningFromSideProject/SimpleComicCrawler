import logging
import json
import time
import subprocess

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

def handler(event, context):
    LOGGER.info('Event: %s', event)

    proxy_process = subprocess.Popen("/proxy_launch.sh")
    time.sleep(10)
    proxy_process.terminate()

    return {
        'statusCode': 200,
        'body': json.dumps(event, indent=4)
    }
