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

# '.erg {background-color: rgba(0, 0, 0, 0.5); font-family: Lucida, sans-serif;font-size: 42px;font-weight: bold; color: Snow}' \
# '.erg {background-color: rgba(255, 255, 255, 0); font-family: Lucida, sans-serif;font-size: 42px;font-weight: bold; color: Snow}' \
# mit . definiert man class, die einem Element zugewiesen werden können
html_head = '<!DOCTYPE html><html>'\
            '<head > <meta charset="utf-8">'\
            '<style>' \
            'td {padding: 5px 15px 5px 15px}'\
            'caption {padding: 25px 15px 25px 15px}' \
            '.erg {font-family: Lucida, sans-serif;font-size: 42px;font-weight: bold; color: Snow}' \
            '.tab {font-family: Lucida, sans-serif;font-size: 42px;font-weight: bold; color: Snow}' \
            '</style >' \
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


def get_results(url, last_matchday):
    results = dict()
    spsoup = BeautifulSoup(fetchurl(url), 'html.parser')
    matchday_divs = spsoup.findAll('div', {"class": "sc-4y67w2-19 kGXFCX"})
    for matchday_div in matchday_divs:
        matchday_results = list()
        header = matchday_div.find('div', {"class": "sc-4y67w2-14 dnRykN"}).text.strip()
        if 'Spieltag' in header:
            matchday_date = matchday_div.find('div', {"class": "sc-4y67w2-15 hYAxxY"}).text.strip()
            mdtemp = header.split(',')[1]
            mdtemp = mdtemp.split('.')[0]
            mdtemp = mdtemp.strip()
            matchday =  int(mdtemp)
            if matchday == last_matchday:
                lines = matchday_div.findAll('div', {"class": "sc-1rxhndz-0 hfLeQi"})
                for line in lines:
                    result = get_match_result(matchday_date, line)
                    matchday_results.append(result)
                try:
                    spo = results[str(matchday)]
                    sp = spo + matchday_results
                    results[str(matchday)] = sp
                except KeyError:
                    results[str(matchday)] = matchday_results
    return results


def get_match_result(matchday_date, zeile):
    teams = zeile.findAll('div', {"class": "sc-1rxhndz-1 fTnXZf"})
    team_home = teams[0].find("span", {"class": "sc-bdfBwQ cvbBOD sc-1e04cm7-5 kUXbCS"}).text.strip()
    team_home_add = teams[0].find("span", {"class": "sc-bdfBwQ cvbBOD"})
    if team_home_add is not None:
        team_home_add = team_home_add.text.strip()
    else:
        team_home_add = ''
    team_guest = teams[1].find("span", {"class": "sc-bdfBwQ cvbBOD sc-1e04cm7-5 kUXbCS"}).text.strip()
    team_guest_add = teams[1].find("span", {"class": "sc-bdfBwQ cvbBOD"})
    if team_guest_add is not None:
        team_guest_add = team_guest_add.text.strip()
    else:
        team_guest_add = ''
    final_score = zeile.find("span", {"class": "sc-bdfBwQ fduPYt"})
    # not yet finished
    if final_score is None:
        final_score = zeile.find("span", {"class": "sc-bdfBwQ kvOzcQ"})
    # canceled
    if final_score is None:
        final_score = zeile.find("span", {"class": "sc-bdfBwQ fwsGyn sc-1rxhndz-6 iBFqGw"})
    if final_score is not None:
        final_score = final_score.text.strip()
    result = dict()
    result['datum'] = matchday_date
    result['name_heim'] = team_home + ' ' + team_home_add
    result['name_gast'] = team_guest + ' ' + team_guest_add
    try:
        result['tore_heim'] = final_score.split(':')[0]
        result['tore_gast'] = final_score.split(':')[1]
    except:
        pass
    result['endstand'] = final_score
    return result


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
    html = html_head
    html += '<body class="erg"><table><caption>Ergebnisse {}. Spieltag {}</caption>'.format(spieltag, liga)
    # print('Ergebnisse {}. Spieltag {}'.format(spieltag, liga))
    # [::-1] damit die Liste chronologisch sortiert ist
    for erg in ergebnisse[::-1]:
        datum = datetime.datetime.strptime(erg['datum'], '%d.%m.%Y')
        wt_tag = '{}., {}'.format(wochentage[datum.date().weekday()], datum.strftime('%d.%m.' ))
        # print('{} {:<20} : {:<20} {:<8}'.format(wt_tag, erg['name_heim'], erg['name_gast'], erg['endstand']))
        html += f"<tr><td>{wt_tag}</td><td>{erg['name_heim']}</td><td>-</td>" \
                f"<td>{erg['name_gast']}</td><td>{erg['endstand']}</td></tr>"
    html += '</table></div></body></html>'
    # show_html(html)
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
            erg = get_results(url + '/matchday', spieltag)
            print_ergebnisse(liga, spieltag, erg[str(spieltag)])
        print('fertig')
    else:
        print(path + ' nicht gefunden, bitte erstellen')
    exit(0)

if __name__ == "__main__":
    main()
