import urllib.request
import urllib.response
import webbrowser
import os
import imgkit
import datetime
try:
    from BeautifulSoup import BeautifulSoup
except ImportError:
    from bs4 import BeautifulSoup

# you need to install wkhtmltopdf
# sudo apt install wkhtmltopdf

path = 'd:\\fupa\\'  # {]\\'.format(date.today().strftime('%Y%m%d'))
path = os.path.dirname(os.path.realpath(__file__)) + '/ergebnisse/'
wochentage = ('Mo', 'Die', 'Mi', 'Do', 'Fr', 'Sa', 'So')

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
    erg_spieltage = dict()

    spsoup = BeautifulSoup(fetchurl(url), 'html.parser')
    news = spsoup.findAll('div', {"class": "sc-4y67w2-19 kGXFCX"})

    for newsbox in news:
        ergebnisse = list()
        header = newsbox.find('div', {"class": "sc-4y67w2-14 dnRykN"}).text.strip()
        if 'Spieltag' in header:

            datum = newsbox.find('div', {"class": "sc-4y67w2-15 hYAxxY"}).text.strip()

            st_temp = header.split(',')[1]
            st_temp = st_temp.split('.')[0]
            st_temp = st_temp.strip()
            spieltag =  int(st_temp)

            zeilen = newsbox.findAll('div', {"class": "sc-1rxhndz-0 hfLeQi"})
            for zeile in zeilen:
                namen = zeile.findAll('div', {"class": "sc-1rxhndz-1 fTnXZf"})
                heim = namen[0].find("span", {"class": "sc-bdfBwQ cvbBOD sc-1e04cm7-5 kUXbCS"}).text.strip()
                heimzusatz = namen[0].find("span", {"class": "sc-bdfBwQ cvbBOD"})
                if heimzusatz is not None:
                    heimzusatz = heimzusatz.text.strip()
                else:
                    heimzusatz = ''
                gast = namen[1].find("span", {"class": "sc-bdfBwQ cvbBOD sc-1e04cm7-5 kUXbCS"}).text.strip()
                gastzusatz = namen[1].find("span", {"class": "sc-bdfBwQ cvbBOD"})
                if gastzusatz is not None:
                    gastzusatz = gastzusatz.text.strip()
                else:
                    gastzusatz = ''
                endstand = zeile.find("span", {"class": "sc-bdfBwQ fduPYt"})
                # noch offen
                if endstand is None:
                    endstand = zeile.find("span", {"class": "sc-bdfBwQ kvOzcQ"})
                # abgesagt
                if endstand is None:
                    endstand = zeile.find("span", {"class": "sc-bdfBwQ fwsGyn sc-1rxhndz-6 iBFqGw"})
                if endstand is not None:
                    endstand = endstand.text.strip()

                ergebnis = dict()
                ergebnis['datum'] = datum
                ergebnis['name_heim'] = heim + ' ' + heimzusatz
                ergebnis['name_gast'] = gast + ' ' + gastzusatz
                try:
                    ergebnis['tore_heim'] = endstand.split(':')[0]
                    ergebnis['tore_gast'] = endstand.split(':')[1]
                except:
                    pass
                ergebnis['endstand'] = endstand
                ergebnisse.append(ergebnis)
            try:
                spo = erg_spieltage[str(spieltag)]
                sp = spo + ergebnisse
                erg_spieltage[str(spieltag)] = sp
            except KeyError:
                erg_spieltage[str(spieltag)] = ergebnisse

    return erg_spieltage


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
        next = row.find('div', {"class": "sc-1nnnh72-1 lfSBRq"})
        platz = next.find('span', {"class": "sc-bdfBwQ cvbBOD"})
        next = row.find('div', {"class": "sc-1nnnh72-2 efspqt"})
        mannschaft = next.find('span', {"class": "sc-bdfBwQ cvbBOD sc-1e04cm7-5 kUXbCS"})

        next = row.findAll('div', {"class": "sc-1nnnh72-1 cGvom"})
        spiele = next[0].find('span', {"class": "sc-bdfBwQ cvbBOD"})
        tordiff = next[1].find('span', {"class": "sc-bdfBwQ cvbBOD"})
        punkte = next[2].find('span', {"class": "sc-bdfBwQ cvbBOD"})

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
        # html += '<tr><td>{}</td><td>{}</td><td>{}</td><td>{}:{}</td></tr>'.format(erg['datum'],erg['name_heim'], erg['name_gast'],erg['tore_heim'],erg['tore_gast'])
        datum = datetime.datetime.strptime(erg['datum'], '%d.%m.%Y')
        wt_tag = '{}., {}'.format(wochentage[datum.date().weekday()], datum.strftime('%d.%m.' ))
        html += '<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>'.format(wt_tag, erg['name_heim'],
                                                                                  erg['name_gast'], erg['endstand'])
    html += '</table></div></body></html>'
    #show_html(html)
    options = {'width': 1200, 'transparent': '','quiet': ''}
    imgkit.from_string(html, path + liga + '_Ergebnis.png', options=options)


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
    imgkit.from_string(html, path + liga + '_Tabelle_I.png', options=options)

    html = html_head
    html += '<body class="tab"><table><caption>Tabelle {}. Spieltag {} (II)</caption></tr>'.format(spieltag, liga)
    html += hdrstr
    for pos in ligatabelle[n1:]:
        html += trstr.format(pos['platz'], pos['mannschaft'], pos['spiele'],pos['tordiff'],pos['punkte'])
    html += '</table></body></html>'
    imgkit.from_string(html, path + liga + '_Tabelle_II.png', options=options)

def main():
    if os.path.exists(path):
        ligen = list()
        liga = {'name': 'Verbandsliga Süd', 'url': 'https://www.fupa.net/league/sachsen-anhalt-verbandsliga-sued'}
        ligen.append(liga)
        liga = {'name':'Landesliga Süd', 'url':'https://www.fupa.net/league/sachsen-anhalt-landesliga-sued'}
        ligen.append(liga)
        liga = {'name':'Landesklasse 5', 'url':'https://www.fupa.net/league/sachsen-anhalt-landesklasse-5'}
        ligen.append(liga)
        liga = {'name':'Landesklasse 8', 'url':'https://www.fupa.net/league/sachsen-anhalt-landesklasse-8'}
        ligen.append(liga)
        liga = {'name':'Kreisoberliga', 'url':'https://www.fupa.net/league/mansfeld-suedharz-kreisoberliga'}
        ligen.append(liga)
        liga = {'name':'Kreisliga 1', 'url':'https://www.fupa.net/league/mansfeld-suedharz-kreisliga-1'}
        ligen.append(liga)
        liga = {'name':'Kreisliga 2', 'url':'https://www.fupa.net/league/mansfeld-suedharz-kreisliga-2'}
        ligen.append(liga)
        liga = {'name':'1. Kreisklasse 1', 'url':'https://www.fupa.net/league/mansfeld-suedharz-erste-kreisklasse-1'}
        ligen.append(liga)
        liga = {'name':'1. Kreisklasse 2', 'url':'https://www.fupa.net/league/mansfeld-suedharz-erste-kreisklasse-2'}
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
            erg = get_results(url + '/matchday')
            print_ergebnisse(liga, spieltag, erg[str(spieltag)])
        print('fertig')
    else:
        print(path + ' nicht gefunden, bitte erstellen')
    exit(0)

if __name__ == "__main__":
    main()
