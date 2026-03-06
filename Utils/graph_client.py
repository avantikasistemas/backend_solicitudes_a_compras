import requests
from .constants import MICROSOFT_CLIENT_ID, MICROSOFT_CLIENT_SECRET, MICROSOFT_TENANT_ID, MICROSOFT_URL, SMTP_EMAIL_SEND


class GraphClient:
    """Cliente para Microsoft Graph API — envío de correos via app registrada."""

    GRAPH_SEND_MAIL_URL = "https://graph.microsoft.com/v1.0/users/{sender}/sendMail"

    def __init__(self):
        self.client_id = MICROSOFT_CLIENT_ID
        self.client_secret = MICROSOFT_CLIENT_SECRET
        self.tenant_id = MICROSOFT_TENANT_ID
        self.authority = f"{MICROSOFT_URL}{self.tenant_id}/oauth2/v2.0/token"
        self.sender = SMTP_EMAIL_SEND
        self._token = None

    # ── Token ──────────────────────────────────────────────────────────────────

    def get_token(self) -> str:
        """Obtiene un token de acceso mediante client_credentials."""
        payload = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scope": "https://graph.microsoft.com/.default",
        }
        print(f"[Graph] Solicitando token en: {self.authority}")
        print(f"[Graph] client_id: {self.client_id}")
        print(f"[Graph] tenant_id: {self.tenant_id}")
        response = requests.post(self.authority, data=payload, timeout=15)
        if not response.ok:
            print(f"[Graph] Error al obtener token — status: {response.status_code}")
            print(f"[Graph] Respuesta Microsoft: {response.text}")
            response.raise_for_status()
        self._token = response.json().get("access_token")
        print("[Graph] Token obtenido correctamente.")
        return self._token

    # ── Envío de correo ────────────────────────────────────────────────────────

    def send_mail(
        self,
        subject: str,
        html_body: str,
        to_recipients: list[str],
        cc_recipients: list[str] | None = None,
    ):
        """
        Envía un correo HTML usando la cuenta configurada en SMTP_EMAIL_SEND.

        :param subject:        Asunto del correo.
        :param html_body:      Cuerpo en HTML.
        :param to_recipients:  Lista de correos destino (TO).
        :param cc_recipients:  Lista de correos en copia (CC), opcional.
        """
        token = self.get_token()

        def _fmt(email: str) -> dict:
            return {"emailAddress": {"address": email}}

        message = {
            "subject": subject,
            "body": {"contentType": "HTML", "content": html_body},
            "toRecipients": [_fmt(e) for e in to_recipients if e],
        }
        if cc_recipients:
            message["ccRecipients"] = [_fmt(e) for e in cc_recipients if e]

        payload = {"message": message, "saveToSentItems": "false"}

        url = self.GRAPH_SEND_MAIL_URL.format(sender=self.sender)
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        if not response.ok:
            print(f"[Graph] Error al enviar correo — status: {response.status_code}")
            print(f"[Graph] Respuesta Microsoft: {response.text}")
            response.raise_for_status()
        print(f"Correo enviado via Graph a: {to_recipients}")
