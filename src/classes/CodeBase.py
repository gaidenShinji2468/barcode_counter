import os
from math import isnan
import pandas as pd


class CodeBase:
    def __init__(self):
        self.code_base = pd.read_excel(f"{os.getcwd()}/data/code_base.xlsx").to_dict()

    def get_client(self, code):
        return self.code_base["CLIENT"][int(code)]

    def get_piece(self, code):
        for key, value in self.code_base.items():
            if [
                "SHIRTS_CODE",
                "POLO_CODE",
                "JACKET_CODE",
                "FLANNEL_CODE",
                "HOODIE_CODE",
                "VARIOUS_CODE",
                "LOWER_PARTS_CODE",
            ].count(key) == 1:
                for index, code128 in value.items():
                    if not isnan(code128) and int(code) == int(code128):
                        return self.code_base[key[:-5]][index]

    def validate(self, input):
        try:
            int(input)
            code = input[-3:]
            for key, value in self.code_base.items():
                if [
                    "SHIRTS_CODE",
                    "POLO_CODE",
                    "JACKET_CODE",
                    "FLANNEL_CODE",
                    "HOODIE_CODE",
                    "VARIOUS_CODE",
                    "LOWER_PARTS_CODE",
                ].count(key) == 1:
                    for _, code128 in value.items():
                        if not isnan(code128) and int(code) == int(code128):
                            return True
            return False
        except Exception:
            return False
