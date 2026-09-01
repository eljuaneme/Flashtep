from zoneinfo import ZoneInfo
import os
from datetime import datetime
import requests
import time

WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK")
TZ = ZoneInfo("UTC")

RECORDATORIOS = {
    "00:00": ("Bus Urbano (Ruta A)", "00:00 - 01:00", "🚌"),
    "01:00": ("Traslado de cliente VIP", "01:00 - 02:00", "⭐"),
    "02:00": ("Servicio de Taxi", "02:00 - 03:00", "🚕"),
    "03:00": ("Servicio de Mudanza", "03:00 - 04:00", "🚚"),
    "05:00": ("Servicio de Taxi", "05:00 - 06:00", "🚕"),
    "07:00": ("Servicio de Mudanza", "07:00 - 08:00", "🚚"),
    "08:00": ("Bus Interurbano (Ruta B)", "08:00 - 09:00", "🚌"),
    "11:00": ("Servicio de Taxi", "11:00 - 12:00", "🚕"),
    "12:00": ("Traslado de cliente VIP", "12:00 - 13:00", "⭐"),
    "14:00": ("Servicio de Taxi", "14:00 - 15:00", "🚕"),
    "16:00": ("Servicio de Mudanza", "16:00 - 17:00", "🚚"),
    "17:00": ("Traslado de cliente VIP", "17:00 - 18:00", "⭐"),
    "18:00": ("Bus Interurbano (Ruta D)", "18:00 - 19:00", "🚌"),
    "19:00": ("Servicio de Taxi", "19:00 - 20:00", "🚕"),
    "20:00": ("Servicio de Mudanza", "20:00 - 21:00", "🚚"),
    "21:00": ("Servicio de Taxi", "21:00 - 22:00", "🚕"),
    "22:00": ("Traslado de cliente VIP / Mudanza", "22:00 - 23:00", "⭐"),
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
        "allowed_mentions": {"parse": ["everyone"]},
    }

    if not WEBHOOK_URL:
        print("❌ Error: No se encontró DISCORD_WEBHOOK")
        return False

    max_intentos = 1
    
    for intento in range(max_intentos):
        try:
            respuesta = requests.post(WEBHOOK_URL, json=mensaje, timeout=10)
            
            if respuesta.status_code == 204:
                print(f"✅ Recordatorio enviado: {actividad}")
                return True
            elif respuesta.status_code == 429:
                wait_time = int(respuesta.headers.get("Retry-After", 5))
                print(f"⚠️ Rate limit. Esperando {wait_time}s (Intento {intento + 1}/{max_intentos})")
                time.sleep(wait_time)
            else:
                print(f"⚠️ Error {respuesta.status_code} (Intento {intento + 1}/{max_intentos})")
                if intento < max_intentos - 1:
                    time.sleep(2)
        except Exception as e:
            print(f"⚠️ Error: {e} (Intento {intento + 1}/{max_intentos})")
            if intento < max_intentos - 1:
                time.sleep(2)
    
    return False


def main():
    hora_actual = datetime.now(tz=TZ).strftime("%H:00")
    print(f"🕐 Verificando - Hora UTC: {hora_actual}")

    if hora_actual in RECORDATORIOS:
        actividad, horario, emoji = RECORDATORIOS[hora_actual]
        enviar_recordatorio(actividad, horario, emoji)
    else:
        print(f"ℹ️ Sin actividades para {hora_actual}")


if __name__ == "__main__":
    main()
