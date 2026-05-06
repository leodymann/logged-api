import httpx

from backend.core.config import settings


class WhatsAppClient:
    def send_text(self, to: str, message: str) -> None:
        if settings.WHATSAPP_FAKE_MODE:
            print("\n========== FAKE WHATSAPP ==========")
            print(f"Para: {to}")
            print(message)
            print("===================================\n")
            return

        response = httpx.post(
            f"{settings.WHATSAPP_API_URL}/send/text",
            headers={
                "Authorization": f"Bearer {settings.WHATSAPP_API_TOKEN}",
            },
            json={
                "to": to,
                "message": message,
            },
            timeout=15,
        )

        response.raise_for_status()