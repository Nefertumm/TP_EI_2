from __future__ import annotations
from Utils import logger
import pandas as pd

def verificar_vacios_columna(columna : str, db : pd.DataFrame) -> tuple:
    pass

if __name__ == '__main__':
    # Inicializamos el archivo de logs vacío en cada ejecución
    open('logs.log', 'w')

    db = pd.read_csv('wfp_food_prices_arg_original.csv')
    print(db)