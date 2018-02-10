import os

from celery import Celery


# Setup Celery with RabbitMQ as the broker.
broker_user = os.getenv('RABBITMQ_USER')
broker_pass = os.getenv('RABBITMQ_PASS')
assert broker_pass and broker_pass, "Both 'RABBITMQ_USER' and " + \
                                    "'RABBITMQ_PASS' have to be set in ENV"
worker = Celery('genius_lyrics_crawler',
                broker='amqp://gavin:hooli@rabbitmq:5672')
