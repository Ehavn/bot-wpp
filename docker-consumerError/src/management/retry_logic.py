import json
import pika
from src.utils.rabbit_client import get_rabbit_connection

def requeue_message(message):
    connection, config = get_rabbit_connection()
    channel = connection.channel()
    
    main_queue = config["queue_main"]
    channel.queue_declare(queue=main_queue, durable=True)
    
    original_body = json.dumps(message["original_message"])
    
    channel.basic_publish(
        exchange="",
        routing_key=main_queue,
        body=original_body,
        properties=pika.BasicProperties(delivery_mode=2)
    )
    connection.close()
    return True