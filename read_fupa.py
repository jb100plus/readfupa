import urllib.request
import urllib.response
import webbrowser
import os
import imgkit
from datetime import date
try:
    from BeautifulSoup import BeautifulSoup
except ImportError:
    from bs4 import BeautifulSoup

# you need to install wkhtmltopdf
# sudo apt install wkhtmltopdf

path = 'd:\\fupa\\'  # {]\\'.format(date.today().strftime('%Y%m%d'))
path = os.path.dirname(os.path.realpath(__file__)) + '/ergebnisse/'

html_head = '<!DOCTYPE html><html>'\
            '<head > <meta charset="utf-8">'\
            '<style>td {padding: 5px 15px 5px 15px}</style >'\
            '<style>caption {padding: 25px 15px 25px 15px}</style >' \
            '<style>.erg {background-color: rgba(255, 255, 255, 0); font-family: Lucida, sans-serif;font-size: 42px;font-weight: bold; color: Snow}</style >' \
            '<style>.tab {background-color: rgba(255, 255, 255, 0); font-family: Lucida, sans-serif;font-size: 42px;font-weight: bold; color: Snow}</style >' \
            '</head>'

def fetchurl(url):
    req = urllib.request.Request(
        url,
        data=None,
        headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
        }
    )
    f = urllib.request.urlopen(req)
    html = f.read().decode('utf-8')
    return html


def get_results(url):
    spieltage = dict()
    spsoup = BeautifulSoup(fetchurl(url), 'html.parser')
    for ct in spsoup.findAll("table", {"class": "content_table_std"}):
        spieltag = 0
        ergebnisse = list()
        for trs in ct.findAll('tr'):
            for thspieltag in trs.findAll('th'):
                spieltag = [int(s) for s in thspieltag.text.split('.') if s.isdigit()][0]
            for lsc in trs.findAll('td', {"class": "liga_spielplan_container"}):
                for href in lsc.findAll('a', href=True):
                    for div_spiel in href.findAll('div', {"class": "liga_spieltag_vorschau_spiel"}):
                        th = '-'
                        tg = '-'
                        try:
                            ergebnis = dict()
                            div_wochentag = div_spiel.find("div", {"class": "liga_spieltag_vorschau_wochentag"})
                            if None != div_wochentag:
                                wochentag = div_wochentag.text.strip()
                            div_heim_name = div_spiel.find("div", {"class": "liga_spieltag_vorschau_heim_content"})
                            mh = div_heim_name.text.strip()
                            div_gas_name = div_spiel.find("div", {"class": "liga_spieltag_vorschau_gast_content"})
                            mg = div_gas_name.text.strip()
                            div_heim_erg = div_spiel.find("div", {
                                "class": "liga_spieltag_vorschau_datum_content_ergebnis"})
                            div_heim_erg_tore = div_heim_erg.find("span", {
                                "class": "liga_spieltag_vorschau_datum_content_ergebnis_heim"})
                            th = div_heim_erg_tore.text.strip()
                            div_gast_erg = div_spiel.find("div", {
                                "class": "liga_spieltag_vorschau_datum_content_ergebnis"})
                            div_gast_erg_tore = div_gast_erg.find("span", {
                                "class": "liga_spieltag_vorschau_datum_content_ergebnis_gast"})
                            tg = div_gast_erg_tore.text.strip()
                        except:
                            pass
                        finally:
                            ergebnis['wochentag'] = wochentag
                            ergebnis['name_heim'] = mh
                            ergebnis['name_gast'] = mg
                            ergebnis['tore_heim'] = th
                            ergebnis['tore_gast'] = tg
                            ergebnisse.append(ergebnis)
            spieltage[str(spieltag)] = ergebnisse
    return spieltage

def show_html(html):
    path = os.path.abspath('temp.html')
    url = 'file://' + path
    with open(path, 'w') as f:
        f.write(html)
    webbrowser.open(url)


def get_tabelle(url):
    soup = BeautifulSoup(fetchurl(url), 'html.parser')
    ligatabelle = list()
    ltab = soup.findAll('div', {"class": "sc-1nnnh72-4 hQapSL"})
    for row in ltab:
        platz = row.find('span', {"class": "sc-bdfBwQ cvbBOD"})
        mannschaft = row.find('span', {"class": "sc-bdfBwQ cvbBOD sc-1e04cm7-5 kUXbCS"})
        spiele = row.find('span', {"class": "sc-bdfBwQ cvbBOD"})
        punkte = row.find('span', {"class": "sc-1nnnh72-1 cGvom"})
        tordiff = row.find('span', {"class": "sc-bdfBwQ cvbBOD"})
        veraenderung = None # row.find('span', {"class": ""})
        platzierung = dict()
        platzierung['platz'] = platz.text.strip()
        platzierung['mannschaft'] = mannschaft.text.replace('LIVE', '').strip()
        platzierung['spiele'] = spiele.text.strip()
        platzierung['tordiff'] = tordiff.text.strip()
        platzierung['punkte'] = punkte.text.strip()
        # platzierung['veraenderung'] = veraenderung.text.strip()
        ligatabelle.append(platzierung)
    return ligatabelle



def print_ergebnisse(liga, spieltag, ergebnisse):
    #for erg in ergebnisse:
    #    print(erg['name_heim'], erg['name_gast'],erg['tore_heim'],erg['tore_heim'])

    html = html_head
    html += '<body class="erg"><table><caption>Ergebnisse {}. Spieltag {}</caption>'.format(spieltag, liga)
    for erg in ergebnisse:
        html += '<tr><td>{}</td><td>{}</td><td>{}</td><td>{}:{}</td></tr>'.format(erg['wochentag'],erg['name_heim'], erg['name_gast'],erg['tore_heim'],erg['tore_gast'])
    html += '</table></div></body></html>'
    #show_html(html)
    options = {'width': 1200, 'transparent': '','quiet': ''}
    imgkit.from_string(html, path + liga + 'Ergebnis.png', options=options)


def print_tabelle(liga, spieltag, ligatabelle):
    #for pos in ligatabelle:
    #    print(pos['platz'], pos['mannschaft'], pos['spiele'], pos['tordiff'],pos['punkte'])
    trstrhead = '<tr><td>{}</td><td>{}</td><td align="right">{}</td><td align="right">{}</td>' \
                '<td align="right">{}</td></tr>'
    trstr = '<tr><td align="right" style="padding-right:50px">{}</td>' \
            '<td>{}</td><td align="right" style="padding-right:70px">{}</td>' \
            '<td align="right" style="padding-right:70px">{}</td>' \
            '<td align="right" style="padding-right:70px">{}</td></tr>'

    hdrstr = trstrhead.format('Platz', 'Verein', 'Spiele', 'Tordiff', 'Punkte')
    options = {'width': 1200, 'transparent': '', 'quiet': ''}
    n = len(ligatabelle)
    n1 = n // 2 + n % 2

    html = html_head
    html += '<body class="tab"><table><caption>Tabelle {}. Spieltag {} (I)</caption></tr>'.format(spieltag, liga)
    html += hdrstr
    for pos in ligatabelle[0:n1]:
        html += trstr.format(pos['platz'],pos['mannschaft'], pos['spiele'],pos['tordiff'],pos['punkte'])
    html += '</table></body></html>'
    imgkit.from_string(html, path + liga + 'Tabelle_I.png', options=options)

    html = html_head
    html += '<body class="tab"><table><caption>Tabelle {}. Spieltag {} (II)</caption></tr>'.format(spieltag, liga)
    html += hdrstr
    for pos in ligatabelle[n1:]:
        html += trstr.format(pos['platz'], pos['mannschaft'], pos['spiele'],pos['tordiff'],pos['punkte'])
    html += '</table></body></html>'
    imgkit.from_string(html, path + liga + 'Tabelle_II.png', options=options)

def main():
    if os.path.exists(path):
        ligen = list()
        liga = {'name': 'Verbandsliga', 'url': 'https://www.fupa.net/league/sachsen-anhalt-verbandsliga-sued'}
        ligen.append(liga)
        liga = {'name':'Landesliga', 'url':'https://www.fupa.net/liga/sachsen-anhalt-landesliga-sued'}
        ligen.append(liga)
        liga = {'name':'Kreisoberliga', 'url':'https://www.fupa.net/liga/mansfeld-suedharz-kreisoberliga'}
        ligen.append(liga)
        liga = {'name':'Landeskl. 4', 'url':'https://www.fupa.net/liga/sachsen-anhalt-landesklasse-4'}
        ligen.append(liga)
        liga = {'name':'Landeskl. 6', 'url':'https://www.fupa.net/liga/sachsen-anhalt-landesklasse-6'}
        ligen.append(liga)
        for li in ligen:
            spieltag = -1
            liga = li['name']
            print(liga)
            url = li['url']
            tabelle = get_tabelle(url + '/standing')
            for pos in tabelle:
                spieltag = max(spieltag, int(pos['spiele']))
            print_tabelle(liga, spieltag, tabelle)
            erg = get_results(url + '/matches')
            print_ergebnisse(liga, spieltag, erg[str(spieltag)])
        print('fertig')
    else:
        print(path + ' nicht gefunden, bitte erstellen')
    exit(0)

if __name__ == "__main__":
    main()
