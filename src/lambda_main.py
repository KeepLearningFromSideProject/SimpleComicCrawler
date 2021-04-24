import logging

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

def handler(event, context):
    LOGGER.info('Event: %s', event)

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
