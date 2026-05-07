import httpx

from backend.core.config import settings


class WhatsAppSendError(Exception):
    pass

# Ponte entre API WhatsApp e a LOGGED API
class WhatsAppClient:
    def send_text(self, to: str, message: str) -> dict:
        # Modo local sem consumir a UAZAPI
        if settings.WHATSAPP_FAKE_MODE:
            print("\n========== local test ==========")
            print(f"Para: {to}")
            print(message)
            print("===================================\n")

            return {
                "fake": True,
                "number": to,
                "text": message,
            }

        url = f"{settings.WHATSAPP_API_URL.rstrip('/')}/send/text"

        payload = {
            "number": to,
            "text": message,
        }

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "token": settings.WHATSAPP_API_TOKEN,
        }

        try:
            response = httpx.post(
                url,
                headers=headers,
                json=payload,
                timeout=20,
            )

            response.raise_for_status()

        except httpx.HTTPStatusError as error:
            status_code = error.response.status_code
            response_text = error.response.text

            raise WhatsAppSendError(
                f"Error sending via WhatsApp. Status: {status_code}. Response: {response_text}"
            ) from error

        except httpx.RequestError as error:
            raise WhatsAppSendError(
                f"API connection error: {str(error)}"
            ) from error

        if not response.content:
            return {
                "success": True,
                "status_code": response.status_code,
            }

        try:
            return response.json()
        except ValueError:
            return {
                "success": True,
                "status_code": response.status_code,
                "raw_response": response.text,
            }