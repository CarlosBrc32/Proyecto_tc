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

    return date.strftime('%-d/%-m/%-Y')

def get_quotes():
    url : 'https://serviciosweb.afip.gob.ar/aduana/cotizacionesMaria/default.asp'

    pass
