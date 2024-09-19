import math
from flask import Flask, render_template, request
import json
import re
import unidecode
import requests
import main
app = Flask(__name__)
#route é o link
#função é o que exibir na pagina
with open("data.json", "r") as arquivo:
    dados = json.load(arquivo)
paginationItens = 16
providers = {
    "Netflix": "https://www.netflix.com/",
    "Disney Plus": "https://www.disneyplus.com",
    "Amazon Prime Video": "https://www.primevideo.com",       
    "Google Play Movies": "https://www.play.google.com/store/movies/",       
    "Apple iTunes": "https://www.apple.com/br/itunes/",
    "Star Plus": "https://www.starplus.com/",
    "Paramount Plus": "https://www.paramountplus.com/",
    "HBO Max": "https://www.hbomax.com/",
    "Claro video": "https://www.claro.com.br",
    "Globoplay": "https://globoplay.globo.com/",
}
@app.route("/index")
@app.route("/home")
@app.route("/")
def home():
    global paginationItens
    dados = get_dados(paginationItens)
    total_paginas = math.ceil(len(get_dados())/paginationItens)
    return render_template("index.html", titulo_pagina = "Torra Torrent - Baixar torrents grátis", dados=dados, len = len(dados), page=1, total_paginas=total_paginas)

@app.route("/filmes")
def filmes():
    global paginationItens
    dados = get_dados_por_tipo("filme", paginationItens)
    total_paginas = math.ceil(len(get_dados())/paginationItens)
    return render_template("filmes.html", titulo_pagina = "Filmes", dados=dados, len = len(dados), page=1, total_paginas=total_paginas)
@app.route("/series")
def series():
    global paginationItens
    dados = get_dados_por_tipo("serie", paginationItens)
    total_paginas = math.ceil(len(get_dados())/paginationItens)
    return render_template("series.html", titulo_pagina = "Séries", dados=dados, len = len(dados), page=1, total_paginas=total_paginas)

@app.route("/filme/", methods=['GET'])
def filme():
    nome =request.args['filme']
    dados = getFilmeByNome(nome)
    if dados == -1:
        print('erro no site.py filmes()')
    else:
        url = "https://api.themoviedb.org/3/movie/"+str(dados['id'])+"/watch/providers?api_key=60d2a1d388e526279bd05437db72ea39"
        onde_assistir = requests.request("GET", url).json()
        #url = "https://api.themoviedb.org/3/watch/providers/movie?api_key=60d2a1d388e526279bd05437db72ea39&language=pt-BR&watch_region=BR"
        #providers = requests.request("GET", url).json()
        try:
            dados['onde_assistir'] = onde_assistir['results']['BR']['flatrate']
            print(dados['onde_assistir'])
            print(dados['onde_assistir'][0])
            aux = []
            for i, plataforma in enumerate(dados['onde_assistir']):
                try:    
                    print(plataforma['provider_name'])
                    link = providers[plataforma['provider_name']]
                    dados['onde_assistir'][i]['link'] = link
                    aux.append(dados['onde_assistir'][i])
                except:
                    print("except")
                dados['onde_assistir'] = aux
            if (dados['tipo'] == "serie"):
                return render_template("filme.html", titulo_pagina = "Baixar "+str(dados['temporada'])+"º Temp. "+dados['title'],dados = dados, len = len(dados['onde_assistir']))
            else:
                return render_template("filme.html", titulo_pagina = "Baixar "+dados['title'], dados = dados, len = len(dados['onde_assistir']))
        except:
            if (dados['tipo'] == "serie"):
                return render_template("filme.html", titulo_pagina = "Baixar "+str(dados['temporada'])+"º Temp. "+dados['title'],dados = dados, len = 0)
            else:
                return render_template("filme.html", titulo_pagina = "Baixar "+dados['title'], dados = dados, len = 0)



@app.route("/page/<p>")
def home_pagenation(p):
    global paginationItens
    p = int(p)
    dados = get_dados(paginationItens, ((p-1)*paginationItens))
    total_paginas = math.ceil(len(get_dados())/paginationItens)
    return render_template("index.html", titulo_pagina = ("Torra Torrent - Página "+str(p)), dados=dados, len = len(dados), page=p, total_paginas=total_paginas)

@app.route("/series-page/<p>")
def series_pagenation(p):
    global paginationItens
    p = int(p)
    dados = get_dados_por_tipo("series", paginationItens, ((p-1)*paginationItens))
    total_paginas = math.ceil(len(get_dados_por_tipo('series'))/paginationItens)
    return render_template("index.html", titulo_pagina = ("Torra Torrent - Página "+str(p)), dados=dados, len = len(dados), page=p, total_paginas=total_paginas)

@app.route("/filmes-page/<p>")
def filmes_pagenation(p):
    global paginationItens
    p = int(p)
    dados = get_dados_por_tipo("filmes", paginationItens, ((p-1)*paginationItens))
    total_paginas = math.ceil(len(get_dados_por_tipo('filmes'))/paginationItens)
    return render_template("index.html", titulo_pagina = ("Torra Torrent - Página "+str(p)), dados=dados, len = len(dados), page=p, total_paginas=total_paginas)

@app.route("/search/", methods=['GET'])
def search():
    global paginationItens
    busca = request.args['busca']
    dados = getFilmeByParcialNome(busca)
    if len(dados) > paginationItens:
        dados = dados[:paginationItens]
    return render_template("search.html",  titulo_pagina = "Resultados "+busca, dados=dados, len = len(dados), page=1)

def getFilmeByNome(nome):
    dados = get_dados()
    for index, value in enumerate(dados):
        if str(value['title']) == nome:
            return value
    return {}

def getFilmeByParcialNome(nome):
    nome = unidecode.unidecode(nome)
    dados = get_dados()
    lista = []
    for index, value in enumerate(dados):
        if re.search(rf"{nome}", unidecode.unidecode(str(value['title'])), re.IGNORECASE):
            lista.append(value)
        elif re.search(rf"{nome}", unidecode.unidecode(str(value['original_title'])), re.IGNORECASE):
            lista.append(value)
    return lista

def get_dados(quant = -1, ini = 0):
    global dados
    if(quant < 0):
        return dados
    else:
        if (len(dados) > ini + quant):
            return dados[ini:ini+quant]
        else:
            return dados[ini:]

def get_dados_por_tipo(tipo, quant = -1, ini = 0):
    global dados
    aux = []
    for dado in dados:
        if dado['tipo'] == tipo:
            aux.append(dado)
    if(quant < 0):
        return aux
    else:
        if (len(aux) > ini + quant):
            return aux[ini:ini+quant]
        else:
            return aux[ini:]

################
###########
################

from threading import Thread

class ScanSite(Thread):
    def __init__ (self):
        Thread.__init__(self)

    def run(self):
        main.init()


if __name__ == "__main__":
    a = ScanSite()
    a.start()
    app.run()