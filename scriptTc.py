import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
from bs4 import BeautifulSoup
import pandas as pd
from datetime import date, datetime
import os

session = requests.Session()
retries = Retry(total=3, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504 ])
session.mount('https:/', HTTPAdapter(max_retries=retries))

today = date.today().strftime('%d-%m-%Y')
crispy = float(780)

def replace_to_dot(value):

    if ',' in value:
        value = float(value.replace(',','.'))
    else:
        value = float(value)
    
    return value

def replace_simbol(value):
        
        value = float(value.replace('\xa0', '').replace('$', '').replace('.', '').replace(',', '.'))

        return value

def scrap_table(url, name_table=None):
    response = session.get(url)
    soup = BeautifulSoup(response.content, 'lxml')

    if name_table:
        table = soup.find('table', class_= name_table)
    else:
        table = soup.find('table')

    return table

def my_crispy():

    buyer = float(1240)
    selling = float(1280)
    average = round((buyer + selling)/2,2)

    return {
            'Date' : date(2025,7,14).strftime('%d-%m-%Y'), 
            'Bank' : f'Crispy - USD ({crispy})',
            'Buyer': buyer,
            'Selling': selling,
            'Average' : average,
            'Crispy ARS': crispy*selling
        }

def scrap_bna():

    try:
        table =  scrap_table('https://www.bna.com.ar/Personas','table cotizacion' )

        rows = table.find_all('tr')

        for row in rows:
            cells = row.find_all('td')
            if len(cells) > 0 and "Dolar U.S.A" in cells[0].text:
                buyer = cells[1].text.strip()
                selling = cells[2].text.strip()
                buyer = replace_to_dot(buyer)
                selling = replace_to_dot(selling)
                average = round((buyer + selling)/2,2)
                break

        return {
            'Date' : today,
            'Bank' : 'BNA',
            'Buyer': buyer,
            'Selling': selling,
            'Average' : average,
            'Crispy ARS': crispy*buyer,
            'Dif ARS': round((buyer - 1280) * crispy, 2)

        }
    except AttributeError:
        return{
            'Date' : today,
            'Bank' : 'BNA',
            'Buyer': 'N/A',
            'Selling': 'N/A',
            'Average' : 'Datos no encontrados'
        }
    except requests.exceptions.RequestException as e:
        return{
            'Date' : today,
            'Bank' : 'BNA',
            'Buyer': 'N/A',
            'Selling': 'N/A',
            'Average' : f'Error {e}'
        }

def scrap_bbva():

    try:
        url = 'https://servicios.bbva.com.ar/openmarket/servicios/cotizaciones/monedaExtranjera'
        response = session.get(url)
        data = response.json()

        values = data['respuesta']

        for item in values:
            if 'USD' in item['moneda']['descripcionCorta']:
                buyer = float(item['precioCompra'])
                selling = float(item['precioVenta'])
                average = round((buyer + selling)/2,2)
                break
        
        return {
            'Date' : today,
            'Bank' : 'BBVA',
            'Buyer': buyer,
            'Selling': selling,
            'Average' : average,
            'Crispy ARS': crispy*buyer,
            'Dif ARS': round((buyer - 1280) * crispy, 2)
        }
    except AttributeError:
        return{
            'Date' : today,
            'Bank' : 'BBVA',
            'Buyer': 'N/A',
            'Selling': 'N/A',
            'Average' : 'Datos no encontrados'
        }
    except requests.exceptions.RequestException as e:
        return{
            'Date' : today,
            'Bank' : 'BBVA',
            'Buyer': 'N/A',
            'Selling': 'N/A',
            'Average' : f'Error {e}'
        }

def scrap_patagonia():

    try:
    
        table = scrap_table('https://ebankpersonas.bancopatagonia.com.ar/eBanking/usuarios/cotizacionMonedaExtranjera.htm')

        rows = table.find('tr', class_= 'odd')

        buyer = rows.find('td', class_='importe').text.strip()
        selling = rows.find('td', class_ = 'tdFinalRight').text.strip()

        buyer = replace_simbol(buyer)
        selling = replace_simbol(selling)

        average = round((buyer + selling)/2,2)

        return {
            'Date' : today,
            'Bank' : 'Patagonia',
            'Buyer': buyer,
            'Selling': selling,
            'Average' : average,
            'Crispy ARS': crispy*buyer,
            'Dif ARS': round((buyer - 1280) * crispy, 2)
        }
    
    except AttributeError:
        return{
            'Date' : today,
            'Bank' : 'Patagonia',
            'Buyer': 'N/A',
            'Selling': 'N/A',
            'Average' : 'Datos no encontrados'
        }
    except requests.exceptions.RequestException as e:
        return{
            'Date' : today,
            'Bank' : 'Patagonia',
            'Buyer': 'N/A',
            'Selling': 'N/A',
            'Average' : f'Error {e}'
        }

def scrap_infodolar():

    try:

        table = scrap_table('https://www.infodolar.com/', 'cotizaciones')

        rows = table.find_all('tr')

        for row in rows:
            dolar = row.find_all('td')
            if len(dolar) > 0 and 'Dólar MEP' in dolar[0].text:
                buyer = dolar[1].contents[0].text.strip()
                selling = dolar[2].contents[0].text.strip()

                buyer = replace_simbol(buyer)
                selling = replace_simbol(selling)

                average = round((buyer + selling)/2,2)
                break

        return {
            'Date' : today,
            'Bank' : 'Info Dólar MEP',
            'Buyer': buyer,
            'Selling': selling,
            'Average' : average,
            'Crispy ARS': crispy*buyer,
            'Dif ARS': round((buyer - 1280) * crispy, 2)
        }
    
    except AttributeError:
        return{
            'Date' : today,
            'Bank' : 'Info Dólar MEP',
            'Buyer': 'N/A',
            'Selling': 'N/A',
            'Average' : 'Datos no encontrados'
        }
    except requests.exceptions.RequestException as e:
        return{
            'Date' : today,
            'Bank' : 'Info Dólar MEP',
            'Buyer': 'N/A',
            'Selling': 'N/A',
            'Average' : f'Error {e}'
        }

def all_scrap():
    return [my_crispy(),
            scrap_bna(),
            scrap_bbva(), 
            scrap_patagonia(),
            scrap_infodolar()
            ]

def main ():

    file_path = "data/historical_quotes.xlsx"
    new_data = pd.DataFrame(all_scrap())

    new_data['Date'] = pd.to_datetime(new_data['Date'], dayfirst=True)

    if os.path.exists(file_path):
        existing_data = pd.read_excel(file_path)

        existing_data['Date'] = pd.to_datetime(existing_data['Date'], dayfirst=True)
        
        excluded_dates = [pd.to_datetime(today, dayfirst=True), pd.to_datetime('14-07-2025', dayfirst=True)]

        existing_data = existing_data[
            ~((existing_data['Date'].isin(excluded_dates)) & 
            (existing_data['Bank'].isin(new_data['Bank'])))
        ]

        df = pd.concat([existing_data, new_data], ignore_index=True)
    else:
        df = new_data

    df.to_excel(file_path, index=False)


if __name__ == '__main__':
    main()