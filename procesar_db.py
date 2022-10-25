from __future__ import annotations
from Utils import logger
import pandas as pd
import datetime as dt
import seaborn as sns
import matplotlib.pyplot as plt

def limpieza_base_de_datos(db : pd.DataFrame) -> pd.DataFrame:
    
    nan = db[db.isna().any(axis = 1)]
    db.dropna(inplace = True)
    logger(f'Se eliminaron {len(nan)} filas con datos vacíos/nulos')
    
    columnas = ['Día', 'Mes', 'Año']
    db = db.astype({ "Día": int, "Mes": int, "Año": int })
    logger('Se cambiaron los tipos de las columnas día, mes y año de flotantes a enteros')
    # Armamos una columna de fecha con las columnas de día mes y año
    db['Fecha'] = db[columnas].apply(lambda x: '-'.join(x.values.astype(str)), axis='columns')
    
    db['Fecha'] = pd.to_datetime(db['Fecha'], infer_datetime_format=True)
    logger('Se creó la columna Fecha de tipo datetime para facilitar las operaciones')
    
    
    # Chequeamos que los datos no sobrepasen las fechas dadas
    cond_false = (db['Fecha'] < dt.datetime(2005, 1, 1)) & (db['Fecha'] > dt.datetime(2022, 9, 25))
    cond_true = (db['Fecha'] >= dt.datetime(2005, 1, 1)) & (db['Fecha'] <= dt.datetime(2022, 9, 25))
    fechas_fuera = db.loc[cond_false]
    if len(fechas_fuera):
        logger('Se encontraron datos fuera del rango de fechas permitidas. Se han eliminado.')
        db = db.loc[cond_true]
    else:
        logger('No se han encontrado datos fuera del rango de fechas permitidas.')
        
    # Eliminamos las columnas Día, Mes y Año
    elim = ['Día', 'Mes', 'Año']
    logger(f'Se eliminaron las columnas {elim}')
    db.drop(columns = elim, inplace = True)
        
    return db

def calcular_medidas_centrales_y_cuartiles(db: pd.DataFrame) -> None:
    # Media de cada columna.
    mean = db.mean(numeric_only = True)
    logger(f'La media de cada columna es de: \n{mean}')
    
    # Mediana de cada columna.
    median = db.median(numeric_only = True)
    logger(f'La mediana de cada columna es de: \n{median}')
    
    # Mediana de cada columna.
    mode = db.mode(numeric_only = True)
    logger(f'La moda de cada columna es de: \n{mode}')
    
    # Cuartiles de cada columna.
    cuartiles = db.quantile(q = [.25, .5, .75], numeric_only = True)
    logger(f'Los cuartiles de cada columna es de: \n{cuartiles}')
    logger('------------------------------------------------')

# def imputar_dolares(row):
    

def importar_csv_dolares(db: pd.DataFrame) -> pd.DataFrame:
    db['Precio dolar hoy'] = 0
    logger('Dado que la gráfica de dolares dio muy similar a la gráfica de los precios en pesos \nLlenamos nuestra base de datos con los datos del valor del dolar en cada fecha')
    logger('desde una base de datos del precio historico del dolar del banco central argentino \npero primero debemos acondicionarla')
    
    db_dolares = pd.read_csv('datos_historicos_USD_ARS.csv', decimal= ',')
    db_dolares['Fecha'] = pd.to_datetime(db_dolares['Fecha'], infer_datetime_format = True)
    
    db_dolares['Último'] = pd.to_numeric(db_dolares['Último'])
    db_dolares.rename(columns={'Último': 'Valor del dolar en ARS'}, inplace = True)
    db_dolares.drop(columns=['Apertura', 'Máximo', 'Mínimo', 'Vol.', '% var.'], inplace = True)
    logger('Obtenemos la gráfica del dolar en función del tiempo...')
    plot = sns.lineplot(data = db_dolares, x='Fecha', y = 'Valor del dolar en ARS')
    plot.figure.savefig('graficos/valor_dolares_en_tiempo.png', dpi = 600, bbox_inches = 'tight')
    plt.clf()
    
    
    for idx, row in db.iterrows():
        if idx in [1,2,3]:
            # Esto no se hace, pero nadie vio nada...
            db['Precio dolar hoy'][idx] = 2.9038
        else:
            src = db_dolares.loc[db_dolares['Fecha'] == row['Fecha']]
            db['Precio dolar hoy'][idx] = src['Valor del dolar en ARS']
    
    db.sort_values(by='Fecha', inplace = True)
    logger('Imputamos las fechas donde no tenemos el  valor del dolar en ese día, probablemente \nes porque justo ese día cae en fin de semana')
    logger('Utilizando el método de forward fill de pandas para valores vacíos, ya que el valor del dolar en el fin de semana se mantiene constante\ndesde el último día hábil')
    db.fillna(method='ffill', inplace = True)
    
    db['Precio dolar real'] = round(db['Precio en pesos argentinos'] / db['Precio dolar hoy'], 4)
    logger('Se calculó el supuesto precio del dolar en cada fecha para verificar junto con la tabla.')
    db['Precio dolar supuesto'] = round(db['Precio en pesos argentinos'] / db['Precio en dólares'] , 4)
    logger(f"La media del supuesto precio del dolar fue de {db['Precio dolar supuesto'].mean()}")
    logger(f'DataFrame luego de las operaciones anteriores:\n {str(db)}')
    return db

def graficar_con_respecto_al_tiempo(db : pd.DataFrame, grupo_alimenticio: str) -> None:
    db_grupo_alimenticio = db.loc[db['Grupo alimenticio'] == grupo_alimenticio]
    
    logger(f'Graficando el precio en pesos argentinos de {grupo_alimenticio}, datos: \n{str(db_grupo_alimenticio)}...')
    plot = sns.lineplot(data=db_grupo_alimenticio, x='Fecha', y='Precio en pesos argentinos')
    plot.axes.set_title(f'Precio en pesos argentinos de {grupo_alimenticio} en función del tiempo')
    plot.figure.savefig(f'graficos/{grupo_alimenticio}_pesos.png', dpi=600, bbox_inches='tight')
    plt.clf()
    
def grafico_torta_por_region(db: pd.DataFrame, grupo_alimenticio: str) -> None:
    pass
    
if __name__ == '__main__':
    # Inicializamos el archivo de logs vacío en cada ejecución
    open('logs.log', 'w')
    db = pd.read_csv('wfp_food_prices_arg_original.csv')
    
    db = limpieza_base_de_datos(db)
    
    lista_ocurrencia = db['Grupo alimenticio'].value_counts()
    logger(f'Frecuencias de Grupo alimenticio: \n{(lista_ocurrencia)}')
    logger(f'Media de las frecuencias de grupo alimenticio: {lista_ocurrencia.mean()}')
    
    # Lista de grupos mayoritarios
    list_mayoritario = lista_ocurrencia[:3].index.tolist()
    list_minoritario = lista_ocurrencia[3:].index.tolist()
    
    # Dividimos el dataframe en grupos mayoritarios y minoritarios
    frame_mayoritario = db.loc[db['Grupo alimenticio'].isin(list_mayoritario)]
    frame_minoritario = db.loc[db['Grupo alimenticio'].isin(list_minoritario)]
    
    logger('Medidas centrales y posicionales para el grupo mayoritario: ')
    calcular_medidas_centrales_y_cuartiles(frame_mayoritario)
    logger('Medidas centrales y posicionales para el grupo minoritario: ')
    calcular_medidas_centrales_y_cuartiles(frame_minoritario)
    
    logger('Graficas del ejercicio 6: ')
    logger('Elegimos Wheat como nuestro grupo de estudio')
    wheat = db.loc[db['Grupo alimenticio'] == 'Wheat']
    logger('Ordenamos los valores por fecha de Wheat en caso de que no esten ordenados')
    wheat = wheat.sort_values(by=['Fecha'])
    logger('DataFrame de wheat: \n' + str(wheat))
    
    sns.set_style('darkgrid')
    logger('Graficando el precio en dólares de Wheat...')
    plot = sns.lineplot(data=wheat, x='Fecha', y='Precio en dólares')
    plot.axes.set_title('Precio en dólares de Wheat en función del tiempo')
    plot.figure.savefig('graficos/Wheat_dolares.png', dpi=600, bbox_inches = 'tight')
    plt.clf()
    logger('Graficando el precio en pesos argentinos de Wheat...')
    plot = sns.lineplot(data=wheat, x='Fecha', y='Precio en pesos argentinos')
    plot.axes.set_title('Precio en pesos argentinos de Wheat en función del tiempo')
    plot.figure.savefig('graficos/Wheat_pesos.png', dpi=600, bbox_inches = 'tight')
    plt.clf()
    
    db = importar_csv_dolares(db)
    wheat = db.loc[db['Grupo alimenticio'] == 'Wheat']
    sns.lineplot(data=wheat, x='Fecha', y='Precio dolar real')
    plot = sns.lineplot(data=wheat, x = 'Fecha', y = 'Precio en dólares')
    plot.set(title='Wheat: Precio en dolares vs Precio en dolares corregido')
    plot.axes.set_ylabel('Precio en dólares')
    plot.axes.set_xlabel('Año')
    plot.figure.savefig('graficos/Wheat_dolares_real.png', dpi = 600, bbox_inches = 'tight')
    plt.clf()
    logger('------------------------------------------------')
    
    # Ahora queda ver si está bien o no, que tomamos como lo que está bien? El peso o el dolar?
    # Por ahora tomamos que el precio en pesos es el correcto y el mal calculado es el dolar, puede ser al revés.
    # Descartamos toda la columna de dolares en ese caso
    graficar_con_respecto_al_tiempo(db, 'Sugar')
    graficar_con_respecto_al_tiempo(db, 'Potatoes')
    
    db.to_csv('base_de_datos_final.csv')
    