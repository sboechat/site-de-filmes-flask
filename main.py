#TRADUZIR ALGUMAS SINOPSES

from asyncio.windows_events import NULL
from time import sleep
from unittest import result
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
import requests
import urllib
import json
import re
import unidecode
import chromedriver_autoinstaller

mediaErros = []
cache = []
with open('data.json', 'r', encoding="utf-8") as dados:
  cache = json.load(dados)
url = "https://vacatorrent.com/"
print('''
      
      O sistema tá bugado porque o site vacatorrent.com, onde era feito o webscrapper, saiu do ar. 
      Mas também foi perdido os arquivos estáticos, leia o README.md para mais informações. 
      
      ''')
print(chromedriver_autoinstaller.install())
driver = webdriver.Chrome()
driver.get(url)
sleep(2)
page = driver.page_source.encode('utf-8')
bs = BeautifulSoup(page)

def clickIn(path):
  element = driver.find_element(By.XPATH, path)
  driver.execute_script("arguments[0].click();", element)

def setPagina(page):
  url = "https://vacatorrent.com/-"+str(page)
  driver.get(url)
  #clickIn("//html//body//div[1]//div[3]//div[2]//div//ul//li[6]//a")

def clickInFilme(movieNum):
  clickIn('/html/body/div[1]/div[2]/div[2]/ul/li['+ str(movieNum+1) + ']/a/img')
  global page
  page = driver.page_source.encode('utf-8')
  global bs
  bs = BeautifulSoup(page)

def getFilmeNome():
  posRecorte = 100000
  cortes = ["Dublado", "Dublada", "Legendado", "Legendada", "Nacional", "Blu-Ray", "BluRay", "LIVE ACTION", "CD", "DVD", "1080p", "Full HD", "720p", "HD", "4K", "UHD","Torrent", "MINISSÉRIE", "Série"]
  
  for corte in cortes:
    posRecorteTemp = re.search(rf"\b(?=\w){corte}\b(?!\w)", driver.title, re.IGNORECASE)
    if posRecorteTemp:
      posRecorteTemp = posRecorteTemp.start() - 1
      if (posRecorteTemp > 0 and posRecorteTemp < posRecorte):
        posRecorte = posRecorteTemp
  posRecorteTemp = re.search(rf'temporada', driver.title, re.IGNORECASE)
 
  if posRecorteTemp:
      posRecorteTemp = posRecorteTemp.start() - 4
      if (posRecorteTemp > 0 and posRecorteTemp < posRecorte):
        posRecorte = posRecorteTemp

  if (posRecorte == 100000):
    return driver.title
  else:
    return driver.title[:posRecorte]

def getFilmeEstreia():
  estreiaElement = driver.find_element(By.XPATH, '/html/body/div[1]/div[1]/div[2]/div[3]/div[1]/a[1]')
  return estreiaElement.text 

def refinar_nome(nome):
  global bs
  tags_a = bs.find_all('a')
  for a in tags_a:
    if re.search(rf"\b(?=\w){a.text}\b(?!\w)", nome, re.IGNORECASE):
      return a.text
  return nome

def insert_db(data):
  global cache
  cache.append(data)
  with open('data.json', 'w', encoding="utf-8") as dados:
    json.dump(cache, dados, indent=2, separators=(",", ": "), sort_keys=True)

def get_overview(obj):
  overview = obj['overview']
  if ( overview == ""):
    if obj['tipo'] == "serie":
      url = "https://api.themoviedb.org/3/tv/"+str(obj['id'])+"?api_key=60d2a1d388e526279bd05437db72ea39&language=en-US"
    else:
      url = "https://api.themoviedb.org/3/movie/"+str(obj['id'])+"?api_key=60d2a1d388e526279bd05437db72ea39&language=en-US"
    
    overview = requests.request("GET", url).json()  
    overview = overview['overview']
  return overview

def get_serie_api(nome):
  url = "https://api.themoviedb.org/3/search/tv?api_key=60d2a1d388e526279bd05437db72ea39&language=pt-BR&query=+"+urllib.parse.quote(nome)+"&page=1&include_adult=true"
  response = requests.request("GET", url)
  result = response.json()
  if len(result['results']) <= 0: 
    url = "https://api.themoviedb.org/3/search/tv?api_key=60d2a1d388e526279bd05437db72ea39&language=en&query=+"+urllib.parse.quote(nome)+"&page=1&include_adult=true"
    response = requests.request("GET", url)
    result = response.json()
  return result

def get_filme_api(nome):
  url = "https://api.themoviedb.org/3/search/movie?api_key=60d2a1d388e526279bd05437db72ea39&language=pt-BR&query=+"+urllib.parse.quote(nome)+"&page=1&include_adult=true&year="+getFilmeEstreia()
  response = requests.request("GET", url)
  result = response.json()
  if len(result['results']) <= 0: 
    url = "https://api.themoviedb.org/3/search/movie?api_key=60d2a1d388e526279bd05437db72ea39&language=pt-BR&query=+"+urllib.parse.quote(nome)+"&page=1&include_adult=true"
    response = requests.request("GET", url)
    result = response.json()
    if len(result['results']) <= 0: 
      url = "https://api.themoviedb.org/3/search/movie?api_key=60d2a1d388e526279bd05437db72ea39&language=en&query=+"+urllib.parse.quote(nome)+"&page=1&include_adult=true"
      response = requests.request("GET", url)
      result = response.json()
  return result

def get_download_infos(obj, dados):
  temp = -1
  episodios = []
  res = ""
  audio = ""

  infos = obj.getText()
  infos = infos.split()
  for i in range(len(infos)):
    if (infos[i].lower() == "720p"):
      res = "720P"
    if (infos[i].lower() == "1080p"):
      res = "1080P"
    if (infos[i].lower() == "2160p"):
      res = "4K"
    if (infos[i].lower() == "4k"):
      res = "4K"
    if (infos[i].lower() == "dublado"):
      audio = "dublado"
    if (infos[i].lower() == "dublada"):
      audio = "dublado"
    if (infos[i].lower() == "legendado"):
      audio = "legendado"
    if (infos[i].lower() == "legendada"):
      audio = "legendado"
    if (infos[i].lower() == "nacional"):
      audio = "nacional"
    if (infos[i].lower() == "dual"):
      aux = unidecode.unidecode(infos[i+1]).lower()
      if (aux == "audio"):
        audio = "dual audio"
    if dados and dados['tipo'] == "serie":
      if(infos[i].find("ª") > 0):
        temp=int(infos[i][:-1])
      if((infos[i].find("º") > 0) or (infos[i].find("°") > 0)):
        ep1 = int(infos[i][:-1])
        if(infos[i+1].lower() == "ao" and ((infos[i+2].find("º") > 0) or (infos[i+2].find("°") > 0))):
          ep2 = int(infos[i+2][:-1])
          for j in range(ep1, ep2):
            episodios.append(j)
        else:
          episodios.append(ep1)
  desc = "BAIXAR "
  if dados:
    eps = ""
    if dados['tipo'] == "serie":
      if(temp > 0):
        desc = desc+str(temp)+"ª TEMPORADA - "
      if len(episodios)>0:
        eps = str(episodios[0])+"° EPISÓDIO - "
        if len(episodios)>1:
          eps = str(episodios[0])+"° E "+str(episodios[1])+"° EPISÓDIOS - "
          if len(episodios)>2:
            eps = str(episodios[0])+"° AO "+str(episodios[-1])+"° EPISÓDIOS - "
    desc = desc+eps+dados['title']+" ("+audio+" | "+res+")"
  else:
    desc = obj.getText()
  new = {
    "desc": desc.upper(), 
    "link": obj['href'],
    "temporada": temp,
    "episodios": episodios,
    "resolucao": res,
    "audio": audio,
  } 
  return new

def set_downloads(dados = None):
  downloads = []
  tags = bs.findAll("a", {"class": "list-group-item list-group-item-success newdawn"})
  for i in range(len(tags)):
    new = get_download_infos(tags[i], dados)
    downloads.append(new)
  return downloads

def organizar_dados(dados, ehSerie):
  if ehSerie:
    temp = -1
    for txt in driver.title.split():
      if(txt.find("ª") > 0):
        temp=int(txt[:-1])
    dados['temporada'] = temp
    titulo = dados['name']
    dados['title'] = titulo
    dados['original_title'] = dados['original_name']
    del dados['original_name']
    del dados['name']
    url = "https://api.themoviedb.org/3/tv/"+str(dados['id'])+"/season/"+str(temp)+"?api_key=60d2a1d388e526279bd05437db72ea39&language=pt-BR"
    response = requests.request("GET", url)
    result = response.json()
    if len(result) > 0:
      if result['poster_path'] and len(result['poster_path']) > 0:
        dados['poster_path'] = result['poster_path'] 
    else:
      url = "https://api.themoviedb.org/3/tv/"+str(dados['id'])+"/season/"+str(temp)+"?api_key=60d2a1d388e526279bd05437db72ea39&language=en"
      response = requests.request("GET", url)
      result = response.json()
      if len(result['results']) > 0:
        if len(result['poster_path']) > 0:
          dados['poster_path'] = result['poster_path']

  else:
    titulo = dados['title']     
  if ehSerie:
    dados["tipo"] = "serie"
  else:
    dados["tipo"] = "filme"
    dados['overview'] = get_overview(dados)   
  
  dados['downloads'] = set_downloads(dados)  
  try:
    ano_lancamento = dados["first_air_date"]
  except:
    ano_lancamento = dados["release_date"] 

  ano_lancamento = str(ano_lancamento)
  ano_lancamento = ano_lancamento[:4]
  dados["ano_lancamento"] = ano_lancamento
  print(dados['title']+"\n"+dados['overview']+"\n")
  return dados

############################
#
#BUG NO PAGINATION QUE NÃO MOSTRA O ULTIMO RESTINHO DE FILMES
#
############################

def init():
  for pageNum in range(1, 1366+1):
    setPagina(pageNum)
    sleep(2)
    for movieNum in range(20):
      for i in range(2):
        try:
          sleep(2)
          print("\n"+str(pageNum)+" / "+str(movieNum+1))
          clickInFilme(movieNum)
          media_name = getFilmeNome()

          ehSerie = False
          result = []
          if re.search(rf'temporada', driver.title, re.IGNORECASE):
            ehSerie = True
            result = get_serie_api(media_name)
          else:
            result = get_filme_api(media_name)

          if len(result['results']) <= 0:
            new_name = refinar_nome(media_name)
            if ehSerie:
              result = get_serie_api(new_name)
            else:
              result = get_filme_api(new_name)   
            print("NEW_NAME:" +new_name +" / Série? "+str(ehSerie))
            print(result['results'])
          if len(result['results']) > 0:
            result['results'][0] = organizar_dados(result['results'][0], ehSerie)
            insert_db(result['results'][0])
          else:
            mediaErros.append(media_name + " / " + new_name)
          driver.back()
          break
        except:
          sleep(5)
          driver.refresh()
          sleep(5)
    print("Erros: " + str(mediaErros))
  driver.quit()


if __name__ == "__main__":
  init()