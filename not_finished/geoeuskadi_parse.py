"""This code will parse throught all the geoeuskadi database and export everything in a list,
if the destination doesn't end with a "." extension, it will go deeper until it finds it"""

#Notes:
#a for loop inside a function, the return will only give the first value.

from bs4 import BeautifulSoup as bs #library to parse
import requests #library to read web URL

html_text = requests.get('https://www.geo.euskadi.eus/cartografia/DatosDescarga/Agricultura/').text #source HTML
soup = bs(html_text, 'lxml')

categories = soup.find_all('a') #the categories have an 'a' tag


root = "https://www.geo.euskadi.eus"


def website_builder(category):
    url = root + category['href']
    return url #It works

def request_builder(url, list):
    html_text = requests.get(url).text #request the url source
    soup = bs(html_text, 'lxml') #create the soup
    for link in soup.find_all('a', href=True): #check if href is true and tag 'a'
        ref = link.get('href') #we get the href
        if(url.find(ref) == -1): #-1 means that is not in string
            if ref.lower().find(".zip") != -1 : #lower is for lowercase and "!= -1" if exists, the index is more or equal to 0
                list.append(root  + ref)
            else:
                if ref[-1] == '/': #if last character is '/' enter
                    list = (request_builder(root  + ref, list))
    return list


cats = request_builder('https://www.geo.euskadi.eus/cartografia/DatosDescarga/Agricultura/', [])
with open('somefile.txt', 'w') as f:
    for cat in cats:
        f.write("%s\n" % cat)




