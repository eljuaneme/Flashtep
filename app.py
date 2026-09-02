from zoneinfo import ZoneInfo
import os
from datetime import datetime
import requests
import time

WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK")
TZ = ZoneInfo("UTC")

RECORDATORIOS = {
    "23:50": ("Bus Urbano (Ruta A)", "00:00 - 01:00", "🚌"),
    "00:50": ("Traslado de cliente VIP", "01:00 - 02:00", "⭐"),
    "01:50": ("Servicio de Taxi", "02:00 - 03:00", "🚕"),
    "02:50": ("Servicio de Mudanza", "03:00 - 04:00", "🚚"),
    "04:50": ("Servicio de Taxi", "05:00 - 06:00", "🚕"),
    "06:50": ("Servicio de Mudanza", "07:00 - 08:00", "🚚"),
    "07:50": ("Bus Interurbano (Ruta B)", "08:00 - 09:00", "🚌"),
    "10:50": ("Servicio de Taxi", "11:00 - 12:00", "🚕"),
    "11:50": ("Traslado de cliente VIP", "12:00 - 13:00", "⭐"),
    "13:50": ("Servicio de Taxi", "14:00 - 15:00", "🚕"),
    "15:50": ("Servicio de Mudanza", "16:00 - 17:00", "🚚"),
    "16:50": ("Traslado de cliente VIP", "17:00 - 18:00", "⭐"),
    "17:50": ("Bus Interurbano (Ruta D)", "18:00 - 19:00", "🚌"),
    "18:50": ("Servicio de Taxi", "19:00 - 20:00", "🚕"),
    "19:50": ("Servicio de Mudanza", "20:00 - 21:00", "🚚"),
    "20:50": ("Servicio de Taxi", "21:00 - 22:00", "🚕"),
    "21:50": ("Traslado de cliente VIP / Mudanza", "22:00 - 23:00", "⭐"),
}


def enviar_recordatorio(actividad, horario, emoji):
    mensaje = {
        "content": (
            f"@everyone\n"
            f"{emoji} **¡RECORDATORIO DE ACTIVIDAD!**\n\n"
            f"📌 Actividad: **{actividad}**\n"
            f"🕐 Horario: **{horario}**\n\n"
            f"¡La actividad comienza ahora!"
        ),
        "allowed_mentions": {
            "parse": ["everyone"]
        },
    }

    if not WEBHOOK_URL:
        print("❌ Error: No se encontró DISCORD_WEBHOOK")
        return False

    try:
        respuesta = requests.post(
            WEBHOOK_URL,
            json=mensaje,
            timeout=10
        )

        if respuesta.status_code == 204:
            print(f"✅ Recordatorio enviado: {actividad}")
            return True

        elif respuesta.status_code == 429:
            wait_time = int(
                respuesta.headers.get("Retry-After", 5)
            )

            print(
                f"⚠️ Rate limit. "
                f"Esperando {wait_time}s..."
            )

            time.sleep(wait_time)

        else:
            print(
                f"⚠️ Error HTTP {respuesta.status_code}: "
                f"{respuesta.text}"
            )

    except requests.RequestException as e:
        print(f"❌ Error enviando el webhook: {e}")

    return False


def main():
    # Guarda el último minuto en el que se envió
    # para evitar mensajes duplicados.
    ultimo_recordatorio = None

    print("🚀 Sistema de recordatorios iniciado")
    print("🌎 Zona horaria: UTC")
    print("⏰ Esperando horarios programados...\n")

    while True:
        ahora = datetime.now(TZ)

        # Formato HH:MM, por ejemplo: 10:50
        hora_actual = ahora.strftime("%H:%M")

        # Solo entra si estamos dentro de uno de los minutos
        # programados, por ejemplo entre 10:50:00 y 10:50:59.
        if hora_actual in RECORDATORIOS:

            # Evita enviar varias veces durante el mismo minuto.
            if ultimo_recordatorio != hora_actual:

                actividad, horario, emoji = RECORDATORIOS[hora_actual]

                print(
                    f"🔔 Recordatorio encontrado: "
                    f"{hora_actual} UTC"
                )

                enviado = enviar_recordatorio(
                    actividad,
                    horario,
                    emoji
                )

                # Solo marcamos el minuto como enviado
                # si Discord confirmó correctamente el mensaje.
                if enviado:
                    ultimo_recordatorio = hora_actual

        # Comprobamos cada 5 segundos.
        time.sleep(5)


if __name__ == "__main__":
    main()
