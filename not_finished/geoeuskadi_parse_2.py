"""This code will parse throught all the geoeuskadi database and export everything in a list,
if the destination doesn't end with a "." extension, it will go deeper until it finds it"""

#Notes:
#a for loop inside a function, the return will only give the first value.
#a recursive function and a loop will do the task

from bs4 import BeautifulSoup as bs #library to parse
import requests #library to read web URL

html_text = requests.get('https://www.geo.euskadi.eus/cartografia/DatosDescarga/').text #source HTML
soup = bs(html_text, 'lxml')

categories = soup.find_all('a') #the categories have an 'a' tag


root = "https://www.geo.euskadi.eus"


def website_builder(category):
    url = root + category['href']
    return url #It works

def request_builder(url): #changes the HTML URL
    html_text = requests.get(url).text
    soup = bs(html_text, 'lxml')
    categories = soup.find_all('a')
    print(type(categories))
    return categories


for category in categories:
    if category.text == "[To Parent Directory]":
        continue
    #print(category)
    url = website_builder(category) #we build the URL
    print(url)
    categories = request_builder(url)
    break



