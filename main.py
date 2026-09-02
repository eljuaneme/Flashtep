from zoneinfo import ZoneInfo
import os
from datetime import datetime
import requests
import time


# ============================================================
# CONFIGURACIÓN
# ============================================================

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


# ============================================================
# ENVIAR MENSAJE A DISCORD
# ============================================================

def enviar_recordatorio(actividad, horario, emoji):

    if not WEBHOOK_URL:
        print("❌ Error: No se encontró DISCORD_WEBHOOK")
        return False

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

        elif respuesta.status_code == 429:

            print("⚠️ Discord indicó Rate Limit.")

            retry_after = respuesta.headers.get(
                "Retry-After",
                "5"
            )

            print(
                f"⏳ Discord pide esperar "
                f"{retry_after} segundos."
            )

            return False

        else:

            print(
                f"❌ Error de Discord: "
                f"{respuesta.status_code}"
            )

            print(respuesta.text)

            return False

    except requests.RequestException as e:

        print(f"❌ Error de conexión: {e}")

        return False


# ============================================================
# PROGRAMA PRINCIPAL
# ============================================================

def main():

    print("🚀 Sistema de recordatorios iniciado")
    print("🌎 Zona horaria: UTC")
    print("⏰ Los anuncios se envían durante el minuto :50")
    print()

    # Guarda exactamente el momento programado que ya fue enviado.
    # Ejemplo:
    # 2026-09-02 10:50
    ultimo_envio = None

    while True:

        ahora = datetime.now(TZ)

        fecha_hora_minuto = ahora.strftime(
            "%Y-%m-%d %H:%M"
        )

        hora_minuto = ahora.strftime(
            "%H:%M"
        )

        # ====================================================
        # ¿Estamos en uno de los minutos programados?
        # ====================================================

        if hora_minuto in RECORDATORIOS:

            # =================================================
            # ¿Ya enviamos este mismo minuto?
            # =================================================

            if ultimo_envio != fecha_hora_minuto:

                actividad, horario, emoji = RECORDATORIOS[
                    hora_minuto
                ]

                print(
                    f"🔔 Actividad detectada: "
                    f"{fecha_hora_minuto} UTC"
                )

                enviado = enviar_recordatorio(
                    actividad,
                    horario,
                    emoji
                )

                # =================================================
                # SOLO marcamos como enviado si Discord respondió
                # correctamente.
                # =================================================

                if enviado:

                    ultimo_envio = fecha_hora_minuto

                    print(
                        f"🔒 Bloqueado hasta el próximo "
                        f"horario: {hora_minuto}"
                    )

                    # Esperamos hasta que termine el minuto :50.
                    #
                    # Esto evita que el bucle vuelva a procesar
                    # inmediatamente el mismo anuncio.
                    segundos_restantes = 60 - ahora.second

                    if segundos_restantes > 0:
                        time.sleep(segundos_restantes)

        # Comprobamos cada segundo.
        time.sleep(1)


# ============================================================
# INICIO
# ============================================================

if __name__ == "__main__":
    main()
