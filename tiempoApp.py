import psutil
import time
import keyboard

# Lista de nombres de aplicaciones a rastrear
aplicaciones_a_rastrear = ["chrome.exe", "code.exe", "firefox.exe"]  # Puedes agregar más nombres según tus necesidades

# Diccionario para almacenar los tiempos de inicio de las aplicaciones
tiempos_inicio = {}

def obtener_tiempo_actividad(proceso_nombre):
    if proceso_nombre in tiempos_inicio:
        tiempo_actividad = time.time() - tiempos_inicio[proceso_nombre]
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
                    if proceso_nombre not in tiempos_inicio:
                        # Registra el tiempo de inicio de la aplicación
                        tiempos_inicio[proceso_nombre] = time.time()
                        print(f"La aplicación {proceso_nombre} se ha iniciado.")
                    else:
                        # Imprime el tiempo de actividad de la aplicación
                        imprimir_tiempo_actividad(proceso_nombre)
    except KeyboardInterrupt:
        print("\nPrograma finalizado.")