from zoneinfo import ZoneInfo
import os
from datetime import datetime
import requests

WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK")
TZ = ZoneInfo("UTC")

RECORDATORIOS = {
    "23:50": ("Bus Urbano (Ruta A)", "00:00 - 01:00", "🚌"),
    "00:50": ("Traslado de cliente VIP", "01:00 - 02:00", "⭐"),
    "01:50": ("Servicio de Taxi", "02:00 - 03:00", "🚕"),
    "02:20": ("Servicio de Mudanza", "03:00 - 04:00", "🚚"),
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

ARCHIVO_ULTIMO_ENVIO = "ultimo_recordatorio.txt"


def enviar_recordatorio(actividad, horario, emoji):
    mensaje = {
        "content": (
            f"@everyone\n"
            f"{emoji} **¡RECORDATORIO DE ACTIVIDAD!**\n\n"
            f"📌 Actividad: **{actividad}**\n"
            f"🕐 Horario: **{horario}**\n\n"
            f"⏳ ¡La actividad comienza en 10 minutos!"
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

        print(f"⚠️ Error {respuesta.status_code}")
        print(respuesta.text)
        return False

    except Exception as e:
        print(f"⚠️ Error: {e}")
        return False


def ya_fue_enviado(clave):
    if not os.path.exists(ARCHIVO_ULTIMO_ENVIO):
        return False

    with open(ARCHIVO_ULTIMO_ENVIO, "r") as archivo:
        ultimo_envio = archivo.read().strip()

    return ultimo_envio == clave


def guardar_envio(clave):
    with open(ARCHIVO_ULTIMO_ENVIO, "w") as archivo:
        archivo.write(clave)


def main():
    ahora = datetime.now(tz=TZ)

    hora_actual = ahora.strftime("%H:%M")

    # Incluye fecha + hora para evitar bloquear
    # el mismo horario del día siguiente.
    clave = ahora.strftime("%Y-%m-%d %H:%M")

    print(f"🕐 Verificando - Hora UTC: {hora_actual}")
    print(f"🔑 Clave: {clave}")

    if hora_actual in RECORDATORIOS:

        if ya_fue_enviado(clave):
            print("ℹ️ Este recordatorio ya fue enviado.")
            return

        actividad, horario, emoji = RECORDATORIOS[hora_actual]

        if enviar_recordatorio(actividad, horario, emoji):
            guardar_envio(clave)
            print("💾 Estado guardado correctamente.")

    else:
        print(f"ℹ️ Sin actividades para {hora_actual}")


if __name__ == "__main__":
    main()
    
