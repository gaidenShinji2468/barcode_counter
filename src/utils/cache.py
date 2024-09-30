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
    with open(f"{os.getcwd()}/{CACHE_NAME}", "r") as file:
        data = file.readlines()
    return data


def clear():
    with open(f"{os.getcwd()}/{CACHE_NAME}", "w") as file:
        file.write("")
