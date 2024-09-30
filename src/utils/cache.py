import os
from config import *


def rewrite(rows):
    with open(f"{os.getcwd()}/{CACHE_NAME}", "w") as file:
        file.write(rows)


def add(row):
    with open(f"{os.getcwd()}/{CACHE_NAME}", "a") as file:
        file.write(row)


def read():
    data = []
    try:
        with open(f"{os.getcwd()}/{CACHE_NAME}", "r") as file:
            data = file.readlines()
    except FileNotFoundError:
        with open(f"{os.getcwd()}/{CACHE_NAME}", "w") as file:
            file.write("")
    except Exception as e:
        print(f"Error reading file: {e}")
    return data


def clear():
    with open(f"{os.getcwd()}/{CACHE_NAME}", "w") as file:
        file.write("")


def remove():
    if os.path.exists(f"{os.getcwd()}/{CACHE_NAME}"):
        os.remove(f"{os.getcwd()}/{CACHE_NAME}")
