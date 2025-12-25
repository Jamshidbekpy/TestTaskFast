import os
from aio_pika import connect_robust, Message, IncomingMessage, DeliveryMode
from typing import Callable, Dict, Any
from dotenv import load_dotenv
import json
from datetime import datetime
import uuid

from ..utils.fake_nlp import FakeEventParser, FakeParseRequest

load_dotenv()

class RabbitMQBroker:
    def __init__(self, url=os.getenv("CELERY_BROKER_URL"), exchange_name="chat_direct"):
        self.url = url
        self.exchange_name = exchange_name
        self.queues: Dict[str, Any] = {}
        self.consumers: Dict[str, str] = {}
        self.connection = None
        self.channel = None
        self.exchange = None
        self.pending_responses: Dict[str, Dict[str, Any]] = {}

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
                    # Xabarni qayta ishlash
                    processed_message = self._process_message(message, client_id)
                    await on_message(processed_message)
                    await msg.ack()
                except Exception as e:
                    print(f"[ERROR] Xabar yuborilmadi: {e}")
                    await msg.nack(requeue=True)

            consumer_tag = await queue.consume(handle)
            self.consumers[client_id] = consumer_tag

    def _process_message(self, message: str, client_id: str) -> str:
        """
        Xabarni qayta ishlash - avtomatik tasdiq talab qiladigan versiya
        """
        try:
            data = json.loads(message)
            original_text = data.get("text", message)
        except:
            original_text = message

        try:
            parser = FakeEventParser()
            request = FakeParseRequest(prompt=original_text)
            response = parser.parse(request)
            
            # Avtomatik ravishda message_id yaratish
            message_id = f"msg_{int(datetime.now().timestamp())}_{uuid.uuid4().hex[:8]}"
            
            # HAR QANDAY xabar uchun tasdiq talab qilamiz (test uchun)
            requires_confirmation = True  # HAR DOIM true qilamiz
            
            result_dict = {
                "original_text": str(original_text),
                "success": bool(response.success),
                "client_id": str(client_id),
                "timestamp": str(datetime.now().isoformat()),
                "type": "parsed_result",
                "requires_confirmation": requires_confirmation,  # TEST: har doim true
                "message_id": message_id
            }
            
            if response.success and response.data:
                data = response.data
                
                # Convert all attributes to string
                result_dict.update({
                    "intent": str(data.intent.value if hasattr(data.intent, 'value') else data.intent),
                    "language": str(data.language.value if hasattr(data.language, 'value') else data.language),
                    "confidence": str(round(data.confidence, 2) if hasattr(data, 'confidence') else 'N/A'),
                    "title": str(data.title) if hasattr(data, 'title') else original_text[:30],
                    "time_start": str(data.time_start) if hasattr(data, 'time_start') else '',
                    "time_end": str(data.time_end) if hasattr(data, 'time_end') else '',
                    "all_day": str(data.all_day) if hasattr(data, 'all_day') else 'False',
                    "repeat": str(data.repeat) if hasattr(data, 'repeat') else '',
                    "invites": str(data.invites) if hasattr(data, 'invites') else '[]',
                    "alerts": str(data.alerts) if hasattr(data, 'alerts') else '[]',
                    "url": str(data.url) if hasattr(data, 'url') else '',
                    "note": str(data.note) if hasattr(data, 'note') else '',
                    "warnings": str(data.warnings) if hasattr(data, 'warnings') else '[]'
                })
                
                # Tasdiq so'rash uchun savol
                if requires_confirmation:
                    title = result_dict.get('title', 'Tadbiringiz')
                    result_dict["confirmation_question"] = f"'{title}' tadbirini yaratishni tasdiqlaysizmi? (Ha/Yo'q)"
            
            # Agar parsing muvaffaqiyatsiz bo'lsa ham tasdiq talab qilamiz
            elif requires_confirmation:
                result_dict["confirmation_question"] = f"'{original_text[:30]}' uchun amalni tasdiqlaysizmi? (Ha/Yo'q)"
            
            return json.dumps(result_dict, ensure_ascii=False)
            
        except Exception as e:
            # Xatolikda ham tasdiq talab qilamiz
            message_id = f"msg_{int(datetime.now().timestamp())}_{uuid.uuid4().hex[:8]}"
            return json.dumps({
                "original_text": str(original_text),
                "error": str(e),
                "client_id": str(client_id),
                "timestamp": str(datetime.now().isoformat()),
                "success": False,
                "type": "error",
                "requires_confirmation": True,  # TEST: hatoda ham true
                "message_id": message_id,
                "confirmation_question": f"Xatolik yuz berdi, amalni davom ettirishni xohlaysizmi? (Ha/Yo'q)"
            }, ensure_ascii=False)

    async def publish(self, target_client_id: str, message: str):
        print(f"[DEBUG] Publishing to {target_client_id}")
        print(f"[DEBUG] Message preview: {message[:200]}")
        if not self.exchange:
            raise Exception("Exchange ochilmagan. connect() chaqirilmadi.")

        await self.exchange.publish(
            Message(message.encode(), delivery_mode=DeliveryMode.PERSISTENT),
            routing_key=target_client_id
        )

    async def process_response(self, client_id: str, response_message: str):
        """
        Clientdan kelgan javobni qayta ishlash - soddalashtirilgan
        """
        try:
            print(f"[DEBUG] Processing response from {client_id}: {response_message}")
            data = json.loads(response_message)
            response_text = data.get("text", "").lower().strip()
            response_to = data.get("response_to")
            
            # Javob matnini tekshirish
            if response_text in ["ha", "yes", "да", "ok", "1"]:
                
                # Tasdiq javobi
                confirmation_msg = json.dumps({
                    "text": "✅ Tasdiqlandi! Tadbir yaratildi.",
                    "type": "confirmation",
                    "client_id": client_id,
                    "timestamp": datetime.now().isoformat(),
                    "original_message_id": response_to
                })
                await self.publish(client_id, confirmation_msg)
                print(f"[INFO] Confirmation sent to {client_id}")
                
            elif response_text in ["yo'q", "no", "нет", "cancel", "0"]:
                # Rad etish javobi
                rejection_msg = json.dumps({
                    "text": "❌ Bekor qilindi.",
                    "type": "rejection", 
                    "client_id": client_id,
                    "timestamp": datetime.now().isoformat(),
                    "original_message_id": response_to
                })
                await self.publish(client_id, rejection_msg)
                print(f"[INFO] Rejection sent to {client_id}")
                
            else:
                # Noto'g'ri javob
                error_msg = json.dumps({
                    "text": f"⚠️ Noto'g'ri javob: '{response_text}'. Iltimos, 'Ha' yoki 'Yo'q' deb javob bering.",
                    "type": "error",
                    "client_id": client_id,
                    "timestamp": datetime.now().isoformat()
                })
                await self.publish(client_id, error_msg)
                print(f"[WARNING] Invalid response from {client_id}: {response_text}")
                
        except Exception as e:
            print(f"[ERROR] Failed to process response: {e}")
            import traceback
            print(traceback.format_exc())

    async def disconnect_consumer(self, client_id: str):
        queue_name = f"queue_{client_id}"
        queue = self.queues.get(queue_name)
        consumer_tag = self.consumers.get(client_id)

        if queue and consumer_tag:
            await queue.cancel(consumer_tag)
            print(f"[INFO] Consumer to'xtatildi: {client_id}")
            del self.consumers[client_id]
            
            if queue.consumer_count == 0:
                await queue.delete()
                del self.queues[queue_name]