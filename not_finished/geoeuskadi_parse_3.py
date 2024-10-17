"""This code will parse throught all the geoeuskadi database"""

from bs4 import BeautifulSoup as bs #library to parse
import requests #library to read web URL

r = requests.get('https://www.geo.euskadi.eus/cartografia/DatosDescarga/')

print(r)
webpage = bs(r.content)
files = webpage.select("a") #the categories have an 'a' tag

url = "https://www.geo.euskadi.eus"

#relative_files = [f['href'] for f in files]


# for f in relative_files:
#     full_URL = url + f
#     page = requests.get(full_URL)
#     bs_page = bs(page.content)
#     break