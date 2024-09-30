import os
from datetime import datetime
from time import time
from config import *
from classes import CodeBase as cb
from utils.connection import exec, disconnect
from utils import cache

today = datetime.now().strftime("%Y-%m-%d")
scanned_codes = dict()
code_base = cb.CodeBase()
times = 0


def q_init(connection):
    global today
    cursor = connection.cursor()
    barcodes = []
    if os.path.exists(DB_NAME):
        cursor.execute(
            """
            SELECT * FROM barcodes
            WHERE date(created_at) = ?
            """,
            (today,),
        )
        barcodes = cursor.fetchall()
        if barcodes:
            print("barcodes created today:")
            for barcode in barcodes:
                print(barcode.barcode)
        else:
            print("There are no barcodes created today")
    else:
        print(f"Creating database '{DB_NAME}' and table 'barcodes'")
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS barcodes (
                id INTEGER PRIMARY KEY,
                barcode TEXT NOT NULL,
                count INTEGER,
                created_at TEXT NOT NULL DEFAULT (DATETIME('now')),
                updated_at TEXT NOT NULL DEFAULT (DATETIME('now'))
            )
            """
        )
        connection.commit()
    return barcodes


def q_assign(connection):
    global today
    c_data = []
    inserts = []
    updates = []
    cursor = connection.cursor()
    for row in cache.read():
        id, barcode, count = row.split(",")
        c_data.append((id, barcode, int(count)))
    cursor.execute(
        """
            SELECT * FROM barcodes
            WHERE date(created_at) = ?
        """,
        (today,),
    )
    barcodes = cursor.fetchall()
    if barcodes:
        for cd in c_data:
            to_update = False
            for barcode in barcodes:
                if cd[0] == barcode[0]:
                    updates.append((cd[0], cd[2]))  # id, count
                    to_update = True
                    break
            if not to_update:
                inserts.append(cd)
            else:
                to_update = False
        if inserts:
            cursor.executemany(
                """
                INSERT INTO barcodes (id, barcode, count)
                VALUES (?, ?, ?)
                """,
                inserts,
            )
        cursor.executemany(
            """
            UPDATE barcodes
            WHERE id = ?
            SET count = ?, updated_at = DATETIME('now')
            """,
            updates,
        )
    else:
        cursor.executemany(
            """
            INSERT INTO barcodes (id, barcode, count)
            VALUES (?, ?, ?)
            """,
            c_data,
        )
    cache.clear()


def write_cache(scanned_codes):
    rows = ""
    for barcode in scanned_codes.values():
        rows += f"{barcode[0]},{barcode[1]},{barcode[2]}\n"
    cache.rewrite(rows)


def scanner():
    global scanned_codes
    global times
    global code_base
    print(
        "Escanea los códigos de barras. Presiona f o F después la tecla enter para salir."
    )
    while True:
        times += 1
        barcode = input("-> ")
        if barcode == "f" or barcode == "F":
            exec(q_assign)  # Crea o actualiza y limpia la cache
            break
        if scanned_codes.get(barcode):
            scanned_codes[barcode][2] += 1
        else:
            scanned_codes[barcode] = [int(time()), barcode, 1]
        write_cache(scanned_codes)
        if times == 50:
            exec(q_assign)  # Crea o actualiza y limpia la cache
            times = 0
    print(
        f"\nCódigos escaneados: {sum(map(lambda value: value[2], scanned_codes.values()))}"
    )
    for barcode in scanned_codes.values():
        print(
            barcode[1],
            code_base.get_brand(barcode[1][:2]),
            code_base.get_piece(barcode[1][-3:]),
            f"({barcode[2]})",
        )
    return scanned_codes


def main():
    barcodes = exec(q_init)
    if not barcodes:
        pass
    else:
        pass
    scanner()
    disconnect()


if __name__ == "__main__":
    main()
