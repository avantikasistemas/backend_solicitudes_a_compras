from fastapi.responses import JSONResponse, Response
from fastapi.encoders import jsonable_encoder
import pytz
from datetime import datetime, timezone
from decimal import Decimal
from .graph_client import GraphClient

class Tools:

    def outputpdf(self, codigo, file_name, data={}):
        response = Response(
            status_code=codigo,
            content=data,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={file_name}"
            }
        )
        return response

    def output(self, codigo, message, data={}):
        response = JSONResponse(
            status_code=codigo,
            content=jsonable_encoder({
                "code": codigo,
                "message": message,
                "data": data,
            }),
            media_type="application/json"
        )
        return response

    def result(self, msg, code=400, error="", data=[]):
        return {
            "body": {
                "statusCode": code,
                "message": msg,
                "data": data,
                "Exception": error
            }
        }

    def format_date(self, date, normal_format, output_format):
        fecha_objeto = datetime.strptime(date, normal_format)
        fecha_formateada = fecha_objeto.strftime(output_format)
        return fecha_formateada

    def format_date_flexible(self, date_str, output_format="%Y-%m-%d %H:%M:%S"):
        try:
            formatos_posibles = [
                "%Y-%m-%d %H:%M:%S.%f",
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%dT%H:%M:%S.%f",
                "%Y-%m-%dT%H:%M:%S",
            ]
            fecha_objeto = None
            for formato in formatos_posibles:
                try:
                    fecha_objeto = datetime.strptime(date_str, formato)
                    break
                except ValueError:
                    continue
            if fecha_objeto is None:
                return date_str
            return fecha_objeto.strftime(output_format)
        except Exception as e:
            print(f"Error al formatear fecha {date_str}: {e}")
            return date_str

    def format_date2(self, date):
        fecha_objeto = datetime.fromisoformat(date)
        fecha_formateada = fecha_objeto.strftime("%d-%m-%Y")
        return fecha_formateada

    def format_datetime(self, dt_str):
        dt = datetime.strptime(
            dt_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        local_dt = dt.astimezone(pytz.timezone('America/Bogota'))
        return local_dt.strftime("%d-%m-%Y %H:%M:%S")

    def get_colombia_time(self):
        colombia_tz = pytz.timezone('America/Bogota')
        return datetime.now(colombia_tz)

    def format_money(self, value: str):
        value = value.replace(",", "")
        valor_decimal = Decimal(value)
        return valor_decimal

    def enviar_correo_notificacion(self, solicitud_id, data, correo_solicitante, correo_negociador):
        cuerpo_texto = data["cuerpo_texto"]

        filas_html = ""
        for producto in data["lista_productos"]:
            filas_html += (
                "<tr>"
                "<td>" + str(producto.get("referencia", "")) + "</td>"
                "<td>" + str(producto.get("producto", "")) + "</td>"
                "<td>" + str(producto.get("cantidad", "")) + "</td>"
                "<td>" + str(producto.get("proveedor", "")) + "</td>"
                "<td>" + str(producto.get("marca", "")) + "</td>"
                "<td>" + str(producto.get("negociador", "")) + "</td>"
                "</tr>"
            )

        tabla_html = (
            '<table border="1" cellpadding="5" cellspacing="0" style="border-collapse:collapse;font-family:Arial;">'
            '<thead style="background-color:#2778bf;color:white;">'
            "<tr><th>Referencia</th><th>Producto</th><th>Cantidad</th><th>Proveedor</th><th>Marca</th><th>Negociador</th></tr>"
            "</thead>"
            "<tbody>" + filas_html + "</tbody>"
            "</table>"
        )

        html_content = (
            "<html><body>"
            "<p>" + cuerpo_texto + "</p>"
            "<h4>Productos solicitados:</h4>"
            + tabla_html +
            "</body></html>"
        )

        subject = "Solicitud #: " + str(solicitud_id) + " - " + data["asunto"]

        if isinstance(correo_negociador, str):
            correo_negociador = [correo_negociador]
        if isinstance(correo_solicitante, str):
            correo_solicitante = [e.strip() for e in correo_solicitante.split(",") if e.strip()]
        elif not isinstance(correo_solicitante, list):
            correo_solicitante = []

        to_recipients = [e for e in correo_negociador if e]
        cc_recipients = [e for e in correo_solicitante if e]

        try:
            graph = GraphClient()
            graph.send_mail(
                subject=subject,
                html_body=html_content,
                to_recipients=to_recipients,
                cc_recipients=cc_recipients,
            )
            print("Correo de notificacion enviado correctamente via Graph.")
        except Exception as e:
            print("Error enviando correo de notificacion: " + str(e))


class CustomException(Exception):
    def __init__(self, message="", codigo=400, data={}):
        self.codigo = codigo
        self.message = message
        self.data = data
        self.resultado = {
            "body": {
                "statusCode": codigo,
                "message": message,
                "data": data,
                "Exception": "CustomException"
            }
        }