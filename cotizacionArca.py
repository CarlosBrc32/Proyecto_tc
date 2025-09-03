import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pandas as pd
import tkinter as tk
from tkinter import messagebox
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

session = requests.Session()
retries = Retry(total=3, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504 ])
session.mount('https:/', HTTPAdapter(max_retries=retries))

csv_path = 'PLANILLA-CARGA-MONEDAS.csv'

today = datetime.today()
today_format = today.strftime('%d/%m/%Y')

def scrap_table(url, name_table=None):
    response = session.get(url)
    soup = BeautifulSoup(response.content, 'lxml')

    if name_table:
        table = soup.find('table', class_= name_table)
    else:
        table = soup.find('table')

    return table

def centrar_ventana(ventana, ancho=400, alto=250):
    pantalla_ancho = ventana.winfo_screenwidth()
    pantalla_alto = ventana.winfo_screenheight()
    x = (pantalla_ancho // 2) - (ancho // 2)
    y = (pantalla_alto // 2) - (alto // 2)
    ventana.geometry(f"{ancho}x{alto}+{x}+{y}")

def get_date():

    def confirm():
        try:
            d = int(entry_dia.get())
            m = int(entry_mes.get())
            y = int(entry_anio.get())

            datetime(y, m, d)

            if not (1 <= d <= 31):
                raise ValueError("Día inválido")
            if not (1 <= m <= 12):
                raise ValueError("Mes inválido")
            if not (1900 <= y <= 2100):
                raise ValueError("Año inválido")

            fecha_str = f"{d:02d}/{m:02d}/{y}"
            resultado.set(fecha_str)
            root.destroy()
        except ValueError as e:
            messagebox.showerror("Error",'Fecha invalida:'+ str(e))

    def cancel():
        resultado.set("")  # No devuelve nada
        root.destroy()

    root = tk.Tk()
    root.title("Ingresar Fecha")
    root.resizable(False, False)

    #Checkbox
    weekend = tk.BooleanVar()

    check = tk.Checkbutton(root, text='Fin de semana/Feriado', variable=weekend)
    check.grid(row=1, column=3,padx=10, pady=10)

    centrar_ventana(root, 400, 200)

    resultado = tk.StringVar()

    tk.Label(root, text="Día:", font=("Arial", 12)).grid(row=0, column=0, padx=10, pady=10)
    entry_dia = tk.Entry(root, width=8, font=("Arial", 12))
    entry_dia.grid(row=0, column=1, padx=10, pady=10)
    entry_dia.focus_set()

    tk.Label(root, text="Mes:", font=("Arial", 12)).grid(row=1, column=0, padx=10, pady=10)
    entry_mes = tk.Entry(root, width=8, font=("Arial", 12))
    entry_mes.grid(row=1, column=1, padx=10, pady=10)

    tk.Label(root, text="Año:", font=("Arial", 12)).grid(row=2, column=0, padx=10, pady=10)
    entry_anio = tk.Entry(root, width=8, font=("Arial", 12))
    entry_anio.grid(row=2, column=1, padx=10, pady=10)

    root.bind("<Return>", lambda e: confirm())
    root.bind("<Escape>", lambda e: cancel())

    tk.Button(root, text="Aceptar", command=confirm).grid(row=4, column=1, padx=5, pady=10)
    tk.Button(root, text="Cancelar", command=cancel).grid(row=4, column=2, padx=5, pady=10)

    root.mainloop()

    return weekend.get(), resultado.get() if resultado.get() else None

def get_quotes_arca(date,today_format):

    url = 'https://serviciosweb.afip.gob.ar/aduana/cotizacionesMaria/formulario.asp'

    day, month, year = date.split('/')

    payload = {
        'dia': day,
        'mes': month,
        'anio': year,
        'consultarConstancia.x': 0,
        'consultarConstancia.y': 0
    }

    headers = {'User-Agent': 'Mozilla/5.0'}
    session = requests.Session()
    resp = session.post(url, data=payload, headers=headers)
    soup = BeautifulSoup(resp.text, 'html.parser')

    tablas = soup.find_all('table', class_='contenido')

    if not tablas:
        messagebox.showerror('ERROR',"No encontré la tabla de cotizaciones, puede que no haya datos para la fecha.")
        return pd.DataFrame()

    tabla = tablas[0]

    monedas_filtrar = { '1':'DOLAR ESTADOUNIDENSE',
                        '9': 'ESTERLINA',
                        '3':'EURO',
                        '4':'SUIZO',
                        '14': 'BOLIVIANO',
                        '8': 'AUSTRALIANO'
    }
    
    monedas_comprador = {'2':'DOLAR ESTADOUNIDENSE',
                        '10':'EURO'
    }   
    datos = []
    
    for fila in tabla.find_all('tr')[1:]:  # salto cabecera
        columnas = fila.find_all('td')
        nombre_moneda = columnas[0].get_text(strip=True).upper()

        # --- Buscar en monedas_filtrar ---
        for key, value in monedas_filtrar.items():
            if value in nombre_moneda:
                moneda = key   # guarda la clave en vez del texto
                fecha = today_format
                vendedor = columnas[2].get_text(strip=True).replace('.', ',')  # VENDEDOR
                datos.append([moneda, 0, vendedor, fecha, 'A'])

        # --- Buscar en monedas_comprador ---
        for key, value in monedas_comprador.items():
            if value in nombre_moneda:
                moneda = key   # guarda la clave en vez del texto
                fecha = today_format
                comprador = columnas[3].get_text(strip=True).replace('.', ',')  # COMPRADOR
                datos.append([moneda, 0, comprador, fecha, 'A'])


    df = pd.DataFrame(datos, columns=['U.M', '0', 'TC', 'FECHA','A'])

    if df.empty:
        messagebox.showerror('ERROR',"No encontré la tabla de cotizaciones, puede que no haya datos para la fecha.")
        
    return datos

def get_quotes_bna(today_format):

        try:   
            table =  scrap_table('https://www.bna.com.ar/Personas','table cotizacion' )

            rows = table.find_all('tr')

            for row in rows:
                cells = row.find_all('td')
                if len(cells) > 0 and "Real" in cells[0].text:
                    comprador = cells[1].text.strip()[:3]
                    vendedor  = cells[2].text.strip()[:3]
            
            datos = [['11',0,vendedor,today_format,'A'],['12',0,comprador,today_format,'A']]        
    
            return datos
        
        except AttributeError:
            messagebox.showerror('ERROR',"No encontré la tabla de cotizaciones del BNA.")
        except requests.exceptions.RequestException as e:
            messagebox.showerror('Error', f'{e}')

def get_quotes_oanda(date,today_format):

    url = "https://fxds-hcc.oanda.com/api/data/update/"

    base_currencies = ['DZD', 'EGP', 'INR']
    quote_currency = 'ARS'

    day, month, year = date.split('/')
    end_day, end_month, end_year = today_format.split('/')

    end_date = f'{end_year}-{end_month}-{end_day}'#HOY
    start_date = f'{year}-{month}-{day}'#FECHA PEDIDA

    params = {
    "source": "OANDA",
    "adjustment": "0",
    "period": "daily",
    "price": "bid",
    "view": "graph",
    "quote_currency_0": quote_currency
}
    
    data = []
    for base in base_currencies:
        try:
            params['base_currency'] = base
            params['start_date'] = start_date
            params['end_date'] = end_date

            r = requests.get(url, params=params, timeout=10)
            r.raise_for_status()

            quotes = r.json()
            
        except Exception as e:
            messagebox.showerror('Error', f'{e}')

    return data


def main_function():
    weekend, day = get_date()
    print(day, weekend)

    arca = get_quotes_arca(day,today_format)
    bna = get_quotes_bna(today_format)

    print(get_quotes_oanda(day, today_format))

    all_tc = arca + bna

    df = pd.DataFrame(all_tc,columns=['U.M', '0', 'TC', 'FECHA','A'])
    df.to_csv(csv_path, sep=';', index=False, header=False)

    messagebox.showinfo('Complete',f'Contizaciones extraidas exitosamente de la fecha {day}')

if __name__ == '__main__':
    main_function() 