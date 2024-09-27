from classes import CodeBase as cb


def main():
    scanned_codes = dict()
    code_base = cb.CodeBase()

    print("Escanea los códigos de barras. Presiona f o F después la tecla enter para salir.")
    while True:
        code = input()
        if scanned_codes.get(code):
            scanned_codes[code] += 1
        else:
            scanned_codes[code] = 1
        if code == "f" or code == "F":
            break
    scanned_codes.popitem()
    print(f"\nCódigos escaneados: {sum(scanned_codes.values())}")
    for code, count in scanned_codes.items():
        print(
            code,
            code_base.get_brand(code[:2]),
            code_base.get_piece(code[-3:]),
            count,
        )


if __name__ == "__main__":
    main()
