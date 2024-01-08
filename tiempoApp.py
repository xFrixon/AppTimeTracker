import psutil
import time
import keyboard
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Lista de nombres de aplicaciones a rastrear
aplicaciones_a_rastrear = ["chrome.exe", "code.exe", "firefox.exe"]  # Puedes agregar más nombres según tus necesidades

# Diccionario para almacenar los tiempos de inicio y pausa de las aplicaciones
tiempos_inicio_pausa = {}

def obtener_tiempo_actividad(proceso_nombre):
    if proceso_nombre in tiempos_inicio_pausa:
        tiempo_actividad = tiempos_inicio_pausa[proceso_nombre]['tiempo_acumulado']
        if not tiempos_inicio_pausa[proceso_nombre]['pausado']:
            tiempo_actividad += time.time() - tiempos_inicio_pausa[proceso_nombre]['tiempo_inicial']
        return tiempo_actividad
    else:
        return 0  # Si no hay tiempo de inicio registrado, devuelve 0

def formatear_tiempo(tiempo_segundos):
    horas, segundos_restantes = divmod(tiempo_segundos, 3600)
    minutos, segundos = divmod(segundos_restantes, 60)
    return int(horas), int(minutos), int(segundos)

def imprimir_tiempo_actividad(proceso_nombre):
    tiempo_actividad = obtener_tiempo_actividad(proceso_nombre)
    tiempo_formateado = formatear_tiempo(tiempo_actividad)
    print(f"Tiempo de actividad de {proceso_nombre}: {tiempo_formateado[0]} horas, {tiempo_formateado[1]} minutos, {tiempo_formateado[2]} segundos")

def enviar_correo(destinatario, asunto, cuerpo):
    # Configura los detalles del servidor SMTP (en este caso, para Gmail)
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp_username = "rendimientopc22@gmail.com"
    smtp_password = "vieh rqvm ryty bfdn"

    # Configura el mensaje
    mensaje = MIMEMultipart()
    mensaje['From'] = smtp_username
    mensaje['To'] = destinatario
    mensaje['Subject'] = asunto

    # Agrega el cuerpo del mensaje
    mensaje.attach(MIMEText(cuerpo, 'plain'))

    # Establece la conexión con el servidor SMTP y envía el mensaje
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.sendmail(smtp_username, destinatario, mensaje.as_string())

if __name__ == "__main__":
    print("Presiona Enter para obtener el tiempo de actividad de las aplicaciones. Presiona Ctrl+C para salir.")

    try:
        while True:
            keyboard.wait("enter")
            aplicaciones_imprimidas = set()  # Para realizar un seguimiento de las aplicaciones que ya se han impreso
            for proceso in psutil.process_iter(['pid', 'name', 'create_time']):
                proceso_nombre = proceso.info['name']
                if proceso_nombre.lower() in aplicaciones_a_rastrear and proceso_nombre not in aplicaciones_imprimidas:
                    aplicaciones_imprimidas.add(proceso_nombre)
                    if proceso_nombre not in tiempos_inicio_pausa:
                        # Registra el tiempo de inicio de la aplicación
                        tiempos_inicio_pausa[proceso_nombre] = {'tiempo_acumulado': 0, 'pausado': False, 'tiempo_inicial': time.time()}
                        print(f"La aplicación {proceso_nombre} se ha iniciado.")
                    else:
                        # Imprime el tiempo de actividad de la aplicación hasta el momento
                        imprimir_tiempo_actividad(proceso_nombre)

            # Comprueba si alguna aplicación ha sido cerrada
            for proceso_nombre in list(tiempos_inicio_pausa.keys()):
                procesos_activos = [p.info['name'] for p in psutil.process_iter(['name'])]
                if proceso_nombre not in procesos_activos and not tiempos_inicio_pausa[proceso_nombre]['pausado']:
                    # La aplicación se ha cerrado, pausa el tiempo de actividad
                    tiempos_inicio_pausa[proceso_nombre]['tiempo_acumulado'] += time.time() - tiempos_inicio_pausa[proceso_nombre]['tiempo_inicial']
                    tiempos_inicio_pausa[proceso_nombre]['pausado'] = True
                    print(f"La aplicación {proceso_nombre} se ha cerrado.")

                # Comprueba si la aplicación cerrada ha sido reiniciada
                elif proceso_nombre in procesos_activos and tiempos_inicio_pausa[proceso_nombre]['pausado']:
                    # La aplicación se ha reiniciado, actualiza el tiempo inicial
                    tiempos_inicio_pausa[proceso_nombre]['tiempo_inicial'] = time.time()
                    tiempos_inicio_pausa[proceso_nombre]['pausado'] = False
                    print(f"La aplicación {proceso_nombre} se ha reiniciado.")

    except KeyboardInterrupt:
        # Al presionar Ctrl+C, mostrar el tiempo final de todas las aplicaciones rastreadas
        print("\nPrograma finalizado. Mostrando tiempos finales:")
        for proceso_nombre in tiempos_inicio_pausa:
            imprimir_tiempo_actividad(proceso_nombre)

        # Agregar la fecha y hora de finalización
        fecha_hora_fin = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\nFecha y hora de finalización: {fecha_hora_fin}")

        # Enviar correo electrónico con los tiempos finales y la fecha de finalización
        destinatario_correo = "xavier22tobar@gmail.com"  # Coloca el correo del destinatario
        asunto_correo = "Informe de Tiempos Finales"
        cuerpo_correo = f"Programa finalizado. Tiempos finales:\n"
        for proceso_nombre in tiempos_inicio_pausa:
            tiempo_actividad = obtener_tiempo_actividad(proceso_nombre)
            tiempo_formateado = formatear_tiempo(tiempo_actividad)
            cuerpo_correo += f"Tiempo de actividad de {proceso_nombre}: {tiempo_formateado[0]} horas, {tiempo_formateado[1]} minutos, {tiempo_formateado[2]} segundos\n"

        cuerpo_correo += f"\nFecha y hora de finalización: {fecha_hora_fin}"

        enviar_correo(destinatario_correo, asunto_correo, cuerpo_correo)
        # Confirma el envio del correo
        print("\nSe ha enviado el correo electrónico correctamente")
