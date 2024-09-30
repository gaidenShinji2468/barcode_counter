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


def write_cache(scanned_codes):
    rows = ""
    for barcode in scanned_codes.values():
        rows += f"{barcode[0]},{barcode[1]},{barcode[2]},{today}\n"
    cache.rewrite(rows)


def get_cache():
    c_data = []
    for row in cache.read():
        id, barcode, count, date = row.split(",")
        c_data.append((int(id), barcode, int(count), date[:-1]))
    return c_data


def q_init(connection):
    global today
    cursor = connection.cursor()
    barcodes = []
    cursor.execute(
        """
        SELECT name 
        FROM sqlite_master 
        WHERE type='table' AND name='barcodes';
        """
    )
    table_exists = cursor.fetchone()
    if table_exists:
        cursor.execute(
            """
            SELECT * FROM barcodes
            WHERE DATE(created_at) = ?;
        """,
            (today,),
        )
        barcodes = cursor.fetchall()
        if barcodes:
            print("barcodes created today:")
            for barcode in barcodes:
                print(barcode)
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
            );
            """
        )
        connection.commit()
    return barcodes


def q_assign(connection):
    global today
    inserts = []
    updates = []
    c_data = get_cache()
    cursor = connection.cursor()
    cursor.execute(
        """
            SELECT * FROM barcodes
            WHERE DATE(created_at) = ?;
        """,
        (today,),
    )
    barcodes = cursor.fetchall()
    if c_data and barcodes:
        for cd in c_data:
            to_update = False
            for barcode in barcodes:
                if cd[1] == barcode[1] and cd[3] in barcode[3]:
                    updates.append((cd[2], cd[0]))  # count, id
                    to_update = True
                    break
            if not to_update:
                inserts.append((cd[0], cd[1], cd[2]))
            else:
                to_update = False
        if inserts:
            cursor.executemany(
                """
                INSERT INTO barcodes (id, barcode, count)
                VALUES (?, ?, ?);
                """,
                inserts,
            )
        cursor.executemany(
            """
            UPDATE barcodes
            SET count = ?, updated_at = DATETIME('now')
            WHERE id = ?;
            """,
            updates,
        )
        connection.commit()
    elif c_data:
        cursor.executemany(
            """
            INSERT INTO barcodes (id, barcode, count)
            VALUES (?, ?, ?);
            """,
            map(lambda record: (record[0], record[1], record[2]), c_data),
        )
        connection.commit()
    cache.clear()


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
        elif barcode:
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
    # En caso de que se haya cerrado el programa sin haber terminado la escritura
    # se verifica la cache y se almacena lo que haya quedado alli
    exec(q_assign)  # Crea o actualiza y limpia la cache
    scanner()
    cache.remove()
    disconnect()


if __name__ == "__main__":
    main()
