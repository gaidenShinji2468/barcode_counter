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
selected = None


def write_cache(isAdd):
    # id
    # order_num
    # size
    # barcode
    # count
    global scanned_codes

    rows = ""
    type = "add" if isAdd else "takeout"

    for fields in scanned_codes.values():
        rows += f"{fields[0]},{fields[1]},{fields[2]},{fields[3]},{fields[4]},{type}\n"
    cache.rewrite(rows)


def get_cache():
    c_data = []

    for row in cache.read():
        id, order_num, size, barcode, count, type = row.split(",")
        c_data.append((int(id), int(order_num), size, barcode, int(count), type[:-1]))

    return c_data


def q_init(connection):
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
            WHERE active = ?
            ORDER BY created_at DESC;
            """,
            (1,),
        )
        barcodes = cursor.fetchall()
    else:
        print(f"Creating database '{DB_NAME}' and table 'barcodes'...")
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS barcodes (
                id INTEGER PRIMARY KEY,
                order_num INTEGER NOT NULL,
                size TEXT NOT NULL,
                barcode TEXT,
                count INTEGER NOT NULL,
                active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL DEFAULT (DATETIME('now')),
                updated_at TEXT NOT NULL DEFAULT (DATETIME('now'))
            );
            """
        )
        print("Done")
        connection.commit()

    return barcodes


def q_add(connection):
    inserts = []
    updates = []
    c_data = get_cache()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT * FROM barcodes
        WHERE active = ?;
        """,
        (1,),
    )

    barcodes = cursor.fetchall()

    if c_data and barcodes:
        for cd in c_data:

            to_update = False

            for barcode in barcodes:
                if (
                    cd[3]
                    and barcode[3]
                    and cd[1] == barcode[1]
                    and cd[2].upper() == barcode[2]
                    and cd[3] == barcode[3]
                ) or (cd[1] == barcode[1] and cd[2].upper() == barcode[2]):
                    updates.append((cd[4] + barcode[4], barcode[0]))  # count, id
                    to_update = True
                    break
            if not to_update:
                # id
                # order_num
                # size
                # barcode
                # count
                inserts.append((cd[0], cd[1], cd[2].upper(), cd[3], cd[4]))
            else:
                to_update = False
        if inserts:
            cursor.executemany(
                """
                INSERT INTO barcodes (id, order_num, size, barcode, count)
                VALUES (?, ?, ?, ?, ?);
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
            INSERT INTO barcodes (id, order_num, size, barcode, count)
            VALUES (?, ?, ?, ?, ?);
            """,
            map(
                lambda record: (
                    record[0],
                    record[1],
                    record[2].upper(),
                    record[3],
                    record[4],
                ),
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
        WHERE active = ?;
        """,
        (1,),
    )

    barcodes = cursor.fetchall()

    if c_data and barcodes:
        for cd in c_data:
            for barcode in barcodes:
                if (
                    cd[3]
                    and barcode[3]
                    and cd[1] == barcode[1]
                    and cd[2].upper() == barcode[2]
                    and cd[3] == barcode[3]
                ) or (cd[1] == barcode[1] and cd[2].upper() == barcode[2]):
                    updates.append(
                        (
                            barcode[4] - cd[4] if barcode[4] - cd[4] >= 0 else 0,
                            barcode[0],
                        )
                    )  # count, id
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


def q_get_by_query(query):
    key, value = query

    def query(connection):
        cursor = connection.cursor()

        cursor.execute(
            f"""
            SELECT * FROM barcodes
            WHERE {key} = ?
            ORDER BY created_at DESC;
            """,
            (value,),
        )

        return cursor.fetchall()

    return query


def q_delete_one(id):
    def query(connection):
        cursor = connection.cursor()

        cursor.execute("DELETE FROM barcodes WHERE id = ?", (id,))
        connection.commit()

    return query


def q_update_one(id, queries):
    values = []

    def unpacking(query):
        key, value = query
        values.append(value)

        return f"{key} = ?"

    def query(connection):
        cursor = connection.cursor()

        cursor.execute(
            f"""
            UPDATE barcodes
            SET {",".join(map(unpacking, queries))}, updated_at = DATETIME('now')
            WHERE id = ?;
            """,
            (*values, id),
        )
        connection.commit()

    return query


def show_history(ui, barcodes):
    global code_base

    def prepare(barcode):
        if not barcode[3]:
            return f"Orden: {barcode[1]} Talla: {barcode[2].upper()} Cantidad: {barcode[4]} ID: {barcode[0]}"
        return f"Orden: {barcode[1]} Talla: {barcode[2].upper()} Código: {barcode[3]} Cliente: {code_base.get_client(barcode[3][:2])} Cantidad: {barcode[4]} ID: {barcode[0]}"

    ui.list.clear()
    ui.list.addItems(
        map(
            prepare,
            barcodes,
        )
    )


def set_selected(ui):
    global selected

    d_item = dict()
    l_item = ui.list.currentItem().text().split(" ")

    for i in range(len(l_item)):
        if l_item[i] == "Orden:":
            d_item["order_num"] = l_item[i + 1]
        elif l_item[i] == "Talla:":
            d_item["size"] = l_item[i + 1]
        elif l_item[i] == "Cantidad:":
            d_item["count"] = l_item[i + 1]
        elif l_item[i] == "ID:":
            d_item["id"] = l_item[i + 1]
        elif l_item[i] == "Código:":
            d_item["barcode"] = l_item[i + 1]
    selected = int(d_item["id"])
    if d_item.get("barcode"):
        ui.client.setText(code_base.get_client(d_item["barcode"][:2]))
        ui.piece.setText(code_base.get_piece(d_item["barcode"][-3:]))
        ui.code.setText(d_item["barcode"])
    ui.size.setText(d_item["size"])
    ui.size.setReadOnly(True)
    ui.order_num.setText(d_item["order_num"])
    ui.order_num.setReadOnly(True)
    ui.count.setText(d_item["count"])
    ui.code.setReadOnly(True)
    ui.update_record.setEnabled(True)
    ui.end_record.setEnabled(True)
    ui.delete_record.setEnabled(True)
    ui.save_count.setEnabled(False)
    ui.add.setEnabled(False)
    ui.takeout.setEnabled(False)
    ui.clean_count.setText("Limpiar")


def clean_selected(ui):
    global selected

    selected = None
    ui.client.setText("Cliente")
    ui.piece.setText("Pieza")
    ui.size.setText("")
    ui.size.setReadOnly(False)
    ui.order_num.setText("")
    ui.order_num.setReadOnly(False)
    ui.count.setText("")
    ui.code.setText("")
    ui.code.setReadOnly(False)
    ui.update_record.setEnabled(False)
    ui.end_record.setEnabled(False)
    ui.delete_record.setEnabled(False)
    ui.save_count.setEnabled(True)
    ui.add.setEnabled(True)
    ui.takeout.setEnabled(True)
    ui.clean_count.setText("Limpiar Conteo")


def clean_count(ui):
    global scanned_codes
    global scanned_barcode

    reply = QtWidgets.QMessageBox.question(
        ui.counter_container,
        "Limpiar",
        "Se borrara la información. ¿Estás segur@?",
        QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
        QtWidgets.QMessageBox.No,
    )

    if reply == QtWidgets.QMessageBox.Yes:
        scanned_codes = dict()
        scanned_barcode = ""
        ui.size.setText("")
        ui.code.setText("")
        ui.order_num.setText("")
        ui.client.setText("Cliente")
        ui.piece.setText("Pieza")
        ui.count.setText("")
        clean_selected(ui)


def save_count(ui):
    global scanned_codes
    global scanned_barcode

    if ui.add.isChecked():
        exec(q_add)  # Añade y limpia la cache
    elif ui.takeout.isChecked():
        exec(q_takeout)  # Saca y limpia la cache

    show_history(ui, exec(q_get_by_query(("active", 1))))
    scanned_codes = dict()
    scanned_barcode = ""
    ui.size.setText("")
    ui.order_num.setText("")
    ui.code.setText("")
    ui.client.setText("Cliente")
    ui.piece.setText("Pieza")
    ui.count.setText("")


def _input(ui):
    global scanned_codes
    global scanned_barcode
    global selected

    try:
        size = ui.size.text()
        count = ui.count.text()
        order_num = ui.order_num.text()

        if not selected and not scanned_barcode and order_num and size and count:
            scanned_codes[size] = [int(time()), int(order_num), size, "", int(count)]
            write_cache(ui.add.isChecked())
        elif not selected and scanned_barcode and order_num and size and count:
            scanned_codes[scanned_barcode][4] = int(count)
            write_cache(ui.add.isChecked())
    except Exception as e:
        print(e)


def scanner(ui):
    global scanned_codes
    global scanned_barcode
    global code_base
    global selected

    scanned_barcode = ui.code.text()
    size = ui.size.text()
    order_num = ui.order_num.text()

    if (
        not selected
        and scanned_barcode
        and order_num
        and size
        and code_base.validate(scanned_barcode)
    ):
        if scanned_codes.get(scanned_barcode):
            scanned_codes[scanned_barcode][4] += 1
        else:
            scanned_codes[scanned_barcode] = [
                int(time()),
                int(order_num),
                size,
                scanned_barcode,
                1,
            ]
        write_cache(ui.add.isChecked())
        ui.client.setText(code_base.get_client(scanned_barcode[:2]))
        ui.piece.setText(code_base.get_piece(scanned_barcode[-3:]))
        ui.count.setText(str(scanned_codes.get(scanned_barcode)[4]))
        ui.code.setText("")


def confirm_delete(ui):
    global selected

    reply = QtWidgets.QMessageBox.question(
        ui.counter_container,
        "Eliminar registro",
        "Se eliminara este registro. ¿Estás segur@?",
        QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
        QtWidgets.QMessageBox.No,
    )

    if reply == QtWidgets.QMessageBox.Yes and selected:
        # Ejecutar la eliminacion
        exec(q_delete_one(selected))
        show_history(ui, exec(q_get_by_query(("active", 1))))
        clean_selected(ui)


def confirm_end(ui):
    global selected

    reply = QtWidgets.QMessageBox.question(
        ui.counter_container,
        "Finalizar registro",
        "Se finalizara este registro. ¿Estás segur@?",
        QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
        QtWidgets.QMessageBox.No,
    )

    if reply == QtWidgets.QMessageBox.Yes and selected:
        # Ejecutar la finalizacion
        exec(q_update_one(selected, [("active", 0)]))
        show_history(ui, exec(q_get_by_query(("active", 1))))
        clean_selected(ui)


def update_record(ui):
    global selected

    exec(q_update_one(selected, [("count", int(ui.count.text()))]))
    show_history(ui, exec(q_get_by_query(("active", 1))))
    clean_selected(ui)


def pre_close_event():
    cache.remove()
    disconnect()


def main():
    c_data = get_cache()
    barcodes = exec(q_init)

    # En caso de que se haya cerrado el programa sin haber terminado la escritura
    # se verifica la cache y se almacena lo que haya quedado alli
    if c_data and c_data[0][-1] == "add":
        exec(q_add)  # Añade y limpia la cache
    elif c_data and c_data[0][-1] == "takeout":
        exec(q_takeout)  # Saca y limpia la cache

    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow(pre_close_event)
    ui = UiMainWindow()
    ui.setupUi(main_window)
    ui.code.returnPressed.connect(lambda: scanner(ui))
    ui.size.textChanged.connect(lambda: scanner(ui))
    ui.count.textChanged.connect(lambda: _input(ui))
    ui.save_count.clicked.connect(lambda: save_count(ui))
    ui.clean_count.clicked.connect(lambda: clean_count(ui))
    ui.update_record.clicked.connect(lambda: update_record(ui))
    ui.end_record.clicked.connect(lambda: confirm_end(ui))
    ui.delete_record.clicked.connect(lambda: confirm_delete(ui))
    ui.list.itemDoubleClicked.connect(lambda: set_selected(ui))
    ui.active.clicked.connect(
        lambda: show_history(ui, exec(q_get_by_query(("active", 1))))
    )
    ui.completed.clicked.connect(
        lambda: show_history(ui, exec(q_get_by_query(("active", 0))))
    )
    if barcodes:
        # Adiciona a la tabla de registros las entradas del dia
        show_history(ui, barcodes)

    main_window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
