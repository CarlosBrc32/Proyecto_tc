import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pandas as pd

csv_path = 'PLANILLA-CARGA-MONEDAS.csv'

def get_date():
    today = datetime.today()
    yesterday = today - timedelta(days=1)
    if today.weekday() == 0: #Lunes -> Viernes
        date = today - timedelta(days=3)
    else:
        date = yesterday

    return date

def get_quotes(date):
    url = 'https://serviciosweb.afip.gob.ar/aduana/cotizacionesMaria/default.asp'

    payload = {
        'dia': date.strftime('%d'),
        'mes': date.strftime('%m'),
        'anio': date.strftime('%Y'),
        'consultarConstancia.x': 47,
        'consultarConstancia.y': 17
    }

    headers = {'User-Agent': 'Mozilla/5.0'}
    session = requests.Session()
    resp = session.post(url, data=payload, headers=headers)
    soup = BeautifulSoup(resp.text, 'html.parser')
    tablas = soup.find_all('table', class_='contenido')
    quotes = {}
    df = pd.DataFrame(tablas)

    return df


date = get_date()


print(get_quotes(date))
