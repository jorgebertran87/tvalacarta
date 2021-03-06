# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta - XBMC Plugin
# Canal para telemadrid
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------
import urlparse,re
import urllib
import os

from core import logger
from core import scrapertools
from core.item import Item

DEBUG = False
CHANNELNAME = "telemadrid"

def isGeneric():
    return True

def mainlist(item):
    logger.info("tvalacarta.channels.telemadrid mainlist")

    itemlist = []
    itemlist.append( Item(channel=CHANNELNAME, title="Telemadrid" , url="http://www.telemadrid.es/programas/directorio_programas" , action="programas", folder=True) )
    itemlist.append( Item(channel=CHANNELNAME, title="laOtra" , url="http://www.telemadrid.es/laotra/directorio_programas" , action="programas", folder=True) )

    return itemlist

def programas(item):
    logger.info("tvalacarta.channels.telemadrid programas")

    itemlist = []
    
    # Descarga la página
    data = scrapertools.cache_page(item.url)
    
    # Extrae las zonas de los programas
    patron = '<li class="views-row(.*?</li>)'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for bloque in matches:
        title = scrapertools.find_single_match(bloque,'<a href="[^"]+" class="titulo">([^<]+)</a>')

        # El titulo puede venir de dos formas (en telemadrid y en laotra)
        if title=="":
            title = scrapertools.find_single_match(bloque,'<a class="titulo" href="[^"]+" >([^<]+)</a>')
            url = scrapertools.find_single_match(bloque,'<a class="titulo" href="([^"]+)"')
            thumbnail = scrapertools.find_single_match(bloque,'<img.*?src="([^"]+)"')
            plot = scrapertools.find_single_match(bloque,'<a class="titulo" href="[^"]+" >[^<]+</a>(.*?)</li>')
        else:
            url = scrapertools.find_single_match(bloque,'<a href="([^"]+)" class="titulo">')
            thumbnail = scrapertools.find_single_match(bloque,'<img src="([^"]+)"')
            plot = scrapertools.find_single_match(bloque,'<a href="[^"]+" class="titulo">[^<]+</a>(.*?)</li>')

        # URL absoluta
        url = urlparse.urljoin(item.url,url)

        # Limpia el argumento
        plot = scrapertools.htmlclean(plot)
        plot = plot.replace("693 056 799","")
        plot = plot.replace("680 116 002","")
        plot = plot.replace("+34687591531","")
        plot = plot.replace("+34682500200","")
        plot = plot.replace("+34616080863","")
        plot = plot.replace("Whatsapp del programa:","")
        plot = plot.replace("WhatsApp:","")
        plot = scrapertools.htmlclean(plot)
        plot = plot.strip()

        if title!="":
            itemlist.append( Item(channel=CHANNELNAME, title=title , url=url, thumbnail=thumbnail, plot=plot, action="episodios", show=title, folder=True) )

    return itemlist

def episodios(item):
    logger.info("tvalacarta.channels.telemadrid episodios")

    itemlist = []
    
    # Descarga la página
    data = scrapertools.cache_page(item.url)
    link = scrapertools.find_single_match(data,'<h3 class="titulo">Programas Completos</h3[^<]+<a href="([^"]+)">')
    if link!="":
        item.url = urlparse.urljoin(item.url,link)
        data = scrapertools.cache_page(item.url)

    # video de portada
    bloque = scrapertools.find_single_match(data,'<div id="portSubcatNotDestTema">(.*?)\s+</div>')
    logger.info("bloque="+bloque)
    title,url,thumbnail,plot,url = parse_video(item,bloque)

    if title!="":
        itemlist.append( Item(channel=CHANNELNAME, title=title , url=url, thumbnail=thumbnail, plot=plot, action="play", server="telemadrid", show=item.show, folder=False) )

    # Extrae las zonas de los videos
    patron = '<li class="views-row(.*?</li>)'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for bloque in matches:
        title,url,thumbnail,plot,url = parse_video(item,bloque)

        if title!="":
            itemlist.append( Item(channel=CHANNELNAME, title=title , url=url, thumbnail=thumbnail, plot=plot, action="play", server="telemadrid", show=item.show, folder=False) )

    next_page_url = scrapertools.find_single_match(data,'<li class="pager-next"><a href="([^"]+)" title="Ir a la p')
    if next_page_url!="":
        itemlist.append( Item(channel=CHANNELNAME, title=">> Página siguiente" , url=urlparse.urljoin(item.url,next_page_url), action="episodios", show=item.show, folder=True) )

    return itemlist

def parse_video(item,bloque):
    title = scrapertools.find_single_match(bloque,'<a href="[^"]+" class="titulo">([^<]+)</a>')
    url = scrapertools.find_single_match(bloque,'<a href="([^"]+)" class="titulo">')
    thumbnail = scrapertools.find_single_match(bloque,'<img src="([^"]+)"')
    plot = scrapertools.find_single_match(bloque,'<a href="[^"]+" class="titulo">[^<]+</a>(.*?)</li>')

    # URL absoluta
    url = urlparse.urljoin(item.url,url)

    # Limpia el argumento
    plot = scrapertools.htmlclean(plot)
    plot = plot.replace("693 056 799","")
    plot = plot.replace("680 116 002","")

    return title,url,thumbnail,plot,url

# Verificación automática de canales: Esta función debe devolver "True" si todo está ok en el canal.
def test():

    # Comprueba que la primera opción tenga algo
    categorias_items = mainlist(Item())
    programas_items = programas(categorias_items[0])
    episodios_items = episodios(programas_items[0])

    if len(episodios_items)>0:
        return True

    return False