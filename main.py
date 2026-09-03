from zoneinfo import ZoneInfo
import os
from datetime import datetime
import requests

WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK")
TZ = ZoneInfo("UTC")

ARCHIVO_ESTADO = "ultimo_recordatorio.txt"

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


def obtener_ultimo_envio():
    if not os.path.exists(ARCHIVO_ESTADO):
        return ""

    with open(ARCHIVO_ESTADO, "r") as archivo:
        return archivo.read().strip()


def guardar_envio(clave):
    with open(ARCHIVO_ESTADO, "w") as archivo:
        archivo.write(clave)


def enviar_recordatorio(actividad, horario, emoji):
    if not WEBHOOK_URL:
        print("❌ No se encontró DISCORD_WEBHOOK")
        return False

    mensaje = {
        "content": (
            "@everyone\n"
            f"{emoji} **¡RECORDATORIO DE ACTIVIDAD!**\n\n"
            f"📌 Actividad: **{actividad}**\n"
            f"🕐 Horario: **{horario}**\n\n"
            f"⏳ ¡La actividad comienza en 10 minutos!"
        ),
        "allowed_mentions": {
            "parse": ["everyone"]
        }
    }

    try:
        respuesta = requests.post(
            WEBHOOK_URL,
            json=mensaje,
            timeout=10
        )

        if respuesta.status_code == 204:
            print(f"✅ Recordatorio enviado: {actividad}")
            return True

        print(f"❌ Discord respondió {respuesta.status_code}")
        print(respuesta.text)
        return False

    except Exception as e:
        print(f"❌ Error al enviar: {e}")
        return False


def main():
    ahora = datetime.now(TZ)

    hora_actual = ahora.strftime("%H:%M")
    clave = ahora.strftime("%Y-%m-%d %H:%M")

    print(f"🕐 Hora UTC: {hora_actual}")
    print(f"🔑 Clave: {clave}")

    if hora_actual not in RECORDATORIOS:
        print("ℹ️ No hay actividad programada.")
        return

    ultimo_envio = obtener_ultimo_envio()

    if ultimo_envio == clave:
        print("🛑 Este recordatorio YA fue enviado.")
        return

    actividad, horario, emoji = RECORDATORIOS[hora_actual]

    if enviar_recordatorio(actividad, horario, emoji):
        guardar_envio(clave)
        print("💾 Estado guardado correctamente.")


if __name__ == "__main__":
    main()
