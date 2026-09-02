from flask import Flask
from zoneinfo import ZoneInfo
from datetime import datetime
import requests
import os
import time

app = Flask(__name__)

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
        "allowed_mentions": {"parse": ["everyone"]},
    }

    if not WEBHOOK_URL:
        print("❌ Error: No se encontró DISCORD_WEBHOOK")
        return False

    max_intentos = 3
    
    for intento in range(max_intentos):
        try:
            respuesta = requests.post(WEBHOOK_URL, json=mensaje, timeout=10)
            
            if respuesta.status_code == 204:
                print(f"✅ Recordatorio enviado: {actividad}")
                return True
            else:
                print(f"⚠️ Error {respuesta.status_code}")
                if intento < max_intentos - 1:
                    time.sleep(2)
        except Exception as e:
            print(f"⚠️ Error: {e}")
            if intento < max_intentos - 1:
                time.sleep(2)
    
    return False


@app.route('/recordatorio', methods=['GET', 'POST'])
def recordatorio():
    hora_actual = datetime.now(tz=TZ).strftime("%H:00")
    print(f"🕐 Verificando - Hora UTC: {hora_actual}")

    if hora_actual in RECORDATORIOS:
        actividad, horario, emoji = RECORDATORIOS[hora_actual]
        enviar_recordatorio(actividad, horario, emoji)
        return "✅ Recordatorio enviado", 200
    else:
        print(f"ℹ️ Sin actividades para {hora_actual}")
        return "ℹ️ Sin actividades", 200


@app.route('/ping', methods=['GET', 'POST'])
def ping():
    return "✅ Servidor activo", 200


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
