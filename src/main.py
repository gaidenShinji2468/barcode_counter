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
scanned_barcode = ""
today = datetime.now().strftime("%Y-%m-%d")


def write_cache():
    global scanned_codes

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
            WHERE DATE(created_at) = ?
            ORDER BY created_at DESC;
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


def q_add(connection):
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


def q_takeout(connection):
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
            for barcode in barcodes:
                if (
                    cd[2]
                    and barcode[2]
                    and cd[1].upper() == barcode[1]
                    and cd[2] == barcode[2]
                    and cd[4] in barcode[4]
                ) or (cd[1].upper() == barcode[1] and cd[4] in barcode[4]):
                    updates.append((barcode[3] - cd[3], barcode[0]))  # count, id
                    break
        cursor.executemany(
            """
            UPDATE barcodes
            SET count = ?, updated_at = DATETIME('now')
            WHERE id = ?;
            """,
            updates,
        )
        connection.commit()
    cache.clear()


def q_get_all(connection):
    global today

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT * FROM barcodes
        WHERE DATE(created_at) = ?
        ORDER BY created_at DESC;
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
    global scanned_barcode

    reply = QtWidgets.QMessageBox.question(
        ui.counter_container,
        "Limpiar Conteo",
        "Se limpiara el conteo. ¿Estás segur@?",
        QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
        QtWidgets.QMessageBox.No,
    )

    if reply == QtWidgets.QMessageBox.Yes:
        scanned_codes = dict()
        scanned_barcode = ""
        ui.size.setText("")
        ui.code.setText("")
        ui.client.setText("Cliente")
        ui.piece.setText("Pieza")
        ui.count.setText("")


def end_count(ui):
    global scanned_codes
    global scanned_barcode

    if ui.add.isChecked():
        exec(q_add)  # Crea o actualiza y limpia la cache
    elif ui.takeout.isChecked():
        exec(q_takeout)  # Actualiza y limpia la cache

    show_history(ui, exec(q_get_all))
    scanned_codes = dict()
    scanned_barcode = ""
    ui.size.setText("")
    ui.code.setText("")
    ui.client.setText("Cliente")
    ui.piece.setText("Pieza")
    ui.count.setText("")


def _input(ui):
    global scanned_codes
    global scanned_barcode

    try:
        size = ui.size.text()
        count = ui.count.text()

        if not scanned_barcode and size and count:
            scanned_codes[size] = [int(time()), size, "", int(count)]
            write_cache()
        elif scanned_barcode and size and count:
            scanned_codes[scanned_barcode][3] = int(count)
            write_cache()
    except Exception as e:
        print(e)


def scanner(ui):
    global scanned_codes
    global scanned_barcode
    global code_base

    scanned_barcode = ui.code.text()
    size = ui.size.text()

    if scanned_barcode and size and code_base.validate(scanned_barcode):
        if scanned_codes.get(scanned_barcode):
            scanned_codes[scanned_barcode][3] += 1
        else:
            scanned_codes[scanned_barcode] = [int(time()), size, scanned_barcode, 1]
        write_cache()
        ui.client.setText(code_base.get_client(scanned_barcode[:2]))
        ui.piece.setText(code_base.get_piece(scanned_barcode[-3:]))
        ui.count.setText(str(scanned_codes.get(scanned_barcode)[3]))
        ui.code.setText("")


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
    exec(q_add)  # Crea o actualiza y limpia la cache

    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow(pre_close_event)
    ui = UiMainWindow()
    ui.setupUi(main_window)
    ui.code.returnPressed.connect(lambda: scanner(ui))
    ui.size.textChanged.connect(lambda: scanner(ui))
    ui.count.textChanged.connect(lambda: _input(ui))
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
