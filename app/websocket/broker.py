import os
from aio_pika import connect_robust, Message, IncomingMessage, DeliveryMode
from typing import Callable, Dict
from dotenv import load_dotenv

load_dotenv()

class RabbitMQBroker:
    def __init__(self, url=os.getenv("CELERY_BROKER_URL"), exchange_name="chat_direct"):
        self.url = url
        self.exchange_name = exchange_name
        self.queues: Dict[str, any] = {}
        self.consumers: Dict[str, str] = {}
        self.connection = None
        self.channel = None
        self.exchange = None

    async def connect(self, client_id: str, on_message: Callable[[str], None]):
        queue_name = f"queue_{client_id}"
        routing_key = client_id

        if not self.connection:
            self.connection = await connect_robust(self.url)
            self.channel = await self.connection.channel()

        if not self.exchange:
            self.exchange = await self.channel.declare_exchange(
                self.exchange_name, type="direct", durable=True
            )

        if queue_name not in self.queues:
            queue = await self.channel.declare_queue(
                name=queue_name, durable=True, exclusive=False, auto_delete=False
            )
            await queue.bind(self.exchange, routing_key=routing_key)
            self.queues[queue_name] = queue
        else:
            queue = self.queues[queue_name]

        if client_id not in self.consumers:
            async def handle(msg: IncomingMessage):
                message = msg.body.decode()
                try:
                    await on_message(message)
                    await msg.ack()
                except Exception as e:
                    print(f"[ERROR] Xabar yuborilmadi: {e}")
                    await msg.nack(requeue=True)

            consumer_tag = await queue.consume(handle)
            self.consumers[client_id] = consumer_tag

    async def publish(self, target_client_id: str, message: str):
        print(f"[DEBUG] Publishing to {target_client_id}")
        if not self.exchange:
            raise Exception("Exchange ochilmagan. connect() chaqirilmadi.")

        await self.exchange.publish(
            Message(message.encode(), delivery_mode=DeliveryMode.PERSISTENT),
            routing_key=target_client_id
        )

    async def disconnect_consumer(self, client_id: str):
        queue = self.queues.get(f"queue_{client_id}")
        consumer_tag = self.consumers.get(client_id)

        if queue and consumer_tag:
            await queue.cancel(consumer_tag)
            print(f"[INFO] Consumer to‘xtatildi: {client_id}")
            del self.consumers[client_id]