from datetime import datetime
from time import time
import sys
from PyQt5 import QtWidgets
from config import *
from classes.CodeBase import CodeBase
from classes.UiMainWindow import UiMainWindow, MainWindow
from utils.connection import exec, disconnect
from utils import cache

code_base = CodeBase()
scanned_codes = dict()
today = datetime.now().strftime("%Y-%m-%d")
times = 0


def write_cache(scanned_codes):
    rows = ""

    for props in scanned_codes.values():
        rows += f"{props[0]},{props[1]},{props[2]},{props[3]},{today}\n"
    cache.rewrite(rows)


def get_cache():
    c_data = []

    for row in cache.read():
        id, size, barcode, count, date = row.split(",")
        c_data.append((int(id), size, barcode, int(count), date[:-1]))

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
    else:
        print(f"Creating database '{DB_NAME}' and table 'barcodes'")
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS barcodes (
                id INTEGER PRIMARY KEY,
                size TEXT NOT NULL,
                barcode TEXT,
                count INTEGER NOT NULL,
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
                if (
                    cd[2]
                    and barcode[2]
                    and cd[1].upper() == barcode[1]
                    and cd[2] == barcode[2]
                    and cd[4] in barcode[4]
                ) or (cd[1].upper() == barcode[1] and cd[4] in barcode[4]):
                    updates.append((cd[3] + barcode[3], barcode[0]))  # count, id
                    to_update = True
                    break
            if not to_update:
                inserts.append((cd[0], cd[1].upper(), cd[2], cd[3]))
            else:
                to_update = False
        if inserts:
            cursor.executemany(
                """
                INSERT INTO barcodes (id, size, barcode, count)
                VALUES (?, ?, ?, ?);
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
            INSERT INTO barcodes (id, size, barcode, count)
            VALUES (?, ?, ?, ?);
            """,
            map(
                lambda record: (record[0], record[1].upper(), record[2], record[3]),
                c_data,
            ),
        )
        connection.commit()
    cache.clear()


def q_get_all(connection):
    global today

    cursor = connection.cursor()

    cursor.execute(
        """
            SELECT * FROM barcodes
            ORDER BY created_at DESC
            WHERE DATE(created_at) = ?;
            """,
        (today,),
    )
    return cursor.fetchall()


def q_delete_one(id):
    def query(connection):
        cursor = connection.cursor()

        cursor.execute("DELETE FROM barcodes WHERE id = ?", (id,))
        connection.commit()

    return query


def q_update_many():
    pass  # TODO:


def show_history(ui, barcodes):
    global code_base

    def prepare(barcode):
        if not barcode[2]:
            return (
                f"Talla: {barcode[1].upper()} Cantidad: {barcode[3]} ID: {barcode[0]}"
            )
        return f"Talla: {barcode[1].upper()} Código: {barcode[2]} Cliente: {code_base.get_client(barcode[2][:2])} Cantidad: {barcode[3]} ID: {barcode[0]}"

    ui.list.clear()
    ui.list.addItems(
        map(
            prepare,
            barcodes,
        )
    )


def clean_count(ui):
    global scanned_codes
    global times

    reply = QtWidgets.QMessageBox.question(
        ui.counter_container,
        "Limpiar Conteo",
        "Se limpiara el conteo. ¿Estás segur@?",
        QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
        QtWidgets.QMessageBox.No,
    )

    if reply == QtWidgets.QMessageBox.Yes:
        scanned_codes = dict()
        times = 0
        ui.size.setText("")
        ui.code.setText("")
        ui.client.setText("Cliente")
        ui.piece.setText("Pieza")
        ui.count.setText("")


def end_count(ui):
    global scanned_codes
    global times

    exec(q_assign)  # Crea o actualiza y limpia la cache
    show_history(ui, exec(q_get_all))
    scanned_codes = dict()
    times = 0
    ui.size.setText("")
    ui.code.setText("")
    ui.client.setText("Cliente")
    ui.piece.setText("Pieza")
    ui.count.setText("")


def scanner(ui):
    global scanned_codes
    global times
    global code_base

    barcode = ui.code.text()
    size = ui.size.text()
    count = ui.size.text()

    if barcode and size and code_base.validate(barcode):
        times += 1
        if scanned_codes.get(barcode):
            scanned_codes[barcode][3] += 1
        else:
            scanned_codes[barcode] = [int(time()), size, barcode, 1]
        write_cache(scanned_codes)
        if times == 40:
            exec(q_assign)  # Crea o actualiza y limpia la cache
            show_history(ui, exec(q_get_all))
            times = 0
        ui.client.setText(code_base.get_client(barcode[:2]))
        ui.piece.setText(code_base.get_piece(barcode[-3:]))
        ui.count.setText(str(scanned_codes.get(barcode)[3]))
        ui.code.setText("")
    elif not barcode and size and count:
        times += 1
        scanned_codes[size] = [int(time()), size, None, int(count)]
        write_cache(scanned_codes)
        if times == 40:
            exec(q_assign)  # Crea o actualiza y limpia la cache
            show_history(ui, exec(q_get_all))
            times = 0


def pre_close_event():
    cache.remove()
    disconnect()


def confirm_delete(ui):
    reply = QtWidgets.QMessageBox.question(
        ui.list_container,
        "Eliminar registro",
        "Se eliminara este registro. ¿Estás segur@?",
        QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
        QtWidgets.QMessageBox.No,
    )

    if reply == QtWidgets.QMessageBox.Yes:
        # Ejecutar la eliminacion
        id = ui.list.currentItem().text().split(" ")[-1]
        exec(q_delete_one(id))
        show_history(ui, exec(q_get_all))


def main():
    barcodes = exec(q_init)

    # En caso de que se haya cerrado el programa sin haber terminado la escritura
    # se verifica la cache y se almacena lo que haya quedado alli
    exec(q_assign)  # Crea o actualiza y limpia la cache

    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow(pre_close_event)
    ui = UiMainWindow()
    ui.setupUi(main_window)
    ui.code.returnPressed.connect(lambda: scanner(ui))
    ui.size.textChanged.connect(lambda: scanner(ui))
    ui.count.textChanged.connect(lambda: scanner(ui))
    ui.end_count.clicked.connect(lambda: end_count(ui))
    ui.clean_count.clicked.connect(lambda: clean_count(ui))
    ui.list.itemDoubleClicked.connect(lambda: confirm_delete(ui))
    if barcodes:
        # Adiciona a la tabla de registros las entradas del dia
        show_history(ui, barcodes)

    main_window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
