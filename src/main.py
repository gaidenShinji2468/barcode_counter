import os
import pandas as pd
import keyboard

scanned_codes = dict()
# Variable temporal para capturar el código escaneado
temp_code = ""


# Función que se ejecuta cuando se presiona Enter (fin de la lectura del código)
def on_code_scanned(code):
    global scanned_codes
    # Limpiar los espacios innecesarios y agregar el código a la lista
    code = code.strip()
    if code:
        if scanned_codes.get(code):
            scanned_codes[code] += 1
        else:
            scanned_codes[code] = 1
        print(f" Código escaneado: {code}")


# Función para registrar las entradas del escáner
def scan():
    global temp_code
    while True:
        event = keyboard.read_event()
        if event.event_type == keyboard.KEY_DOWN:
            # Si es la tecla Enter, procesar el código escaneado
            if event.name == "enter":
                on_code_scanned(temp_code)
                temp_code = ""  # Reiniciar la variable para el siguiente código
            # Capturar el código escaneado
            elif (
                event.name != "enter" and len(event.name) == 1
            ):  # Ignorar teclas especiales como Shift, etc.
                temp_code += event.name

        # Salir al presionar ESC
        if event.name == "esc":
            print("Salida.")
            break


def main():
    print("Escanea los códigos de barras. Presiona ESC para salir.")
    # Ejecutar la función de escaneo
    scan()
    # Mostrar los códigos escaneados
    print(f"\nCódigos escaneados: {sum(scanned_codes.values())}")
    for code, count in scanned_codes.items():
        print(code, count, sep=" -> ")


if __name__ == "__main__":
    main()
