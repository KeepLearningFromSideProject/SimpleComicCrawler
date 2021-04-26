import logging
import json
import time
import subprocess
import os

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

def handler(event, context):
    LOGGER.info('Event: %s', event)

    proxy_process = subprocess.Popen(["bash", "/proxy_launch.sh"])
    time.sleep(10)
    os.system("killall -9 ssh")
    proxy_process.terminate()

    return {
        'statusCode': 200,
        'body': "success"
    }

if __name__ == "__main__":
    print(handler([], []))
