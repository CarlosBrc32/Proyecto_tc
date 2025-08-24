import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pandas as pd
import tkinter as tk
from tkinter import messagebox

csv_path = 'PLANILLA-CARGA-MONEDAS.csv'

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

    centrar_ventana(root, 300, 200)

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

    tk.Button(root, text="Aceptar", command=confirm).grid(row=4, column=4, padx=5, pady=10)
    tk.Button(root, text="Cancelar", command=cancel).grid(row=4, column=5, padx=5, pady=10)

    root.mainloop()

    return resultado.get() if resultado.get() else None

def get_quotes_arca(date):

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
                fecha = columnas[1].get_text(strip=True)
                vendedor = columnas[2].get_text(strip=True).replace('.', ',')  # VENDEDOR
                datos.append([moneda, 0, vendedor, fecha, 'A'])

        # --- Buscar en monedas_comprador ---
        for key, value in monedas_comprador.items():
            if value in nombre_moneda:
                moneda = key   # guarda la clave en vez del texto
                fecha = columnas[1].get_text(strip=True)
                comprador = columnas[3].get_text(strip=True).replace('.', ',')  # COMPRADOR
                datos.append([moneda, 0, comprador, fecha, 'A'])


    df = pd.DataFrame(datos, columns=['U.M', '0', 'TC', 'FECHA','A'])

    if df.empty:
        messagebox.showerror('ERROR',"No encontré la tabla de cotizaciones, puede que no haya datos para la fecha.")

    return df

def main_function():
    day = get_date()
    print(day)
    quotes = get_quotes_arca(day)
    print(quotes)
    messagebox.showinfo('Complete',f'Contizaciones extraidas exitosamente de la fecha {day}')

if __name__ == '__main__':
    main_function() 