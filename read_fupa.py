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

# path = 'd:\\fupa\\'  # {]\\'.format(date.today().strftime('%Y%m%d'))
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
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:92.0) Gecko/20100101 Firefox/92.0'
        }
    )
    f = urllib.request.urlopen(req)
    html = f.read().decode('utf-8')
    return html


def get_results_by_date(url, matchday):
    results = dict()
    spsoup = BeautifulSoup(fetchurl(url), 'html.parser')
    now =  datetime.datetime.now()

    for d in range(0, 6):
        datum = now + + datetime.timedelta(days=-d)
        datumstr = datum.strftime("%Y-%m-%d")
        spiele_datum = spsoup.find("div", {"id": datumstr})
        print(datumstr)
        if spiele_datum is not None:
            lines = spiele_datum.findAll('div', {"class": "sc-1rxhndz-2 kjfxdg"})
            matchday_results = list()
            for line in lines:
                result = get_match_result(datumstr, line)
                matchday_results.append(result)
            try:
                spo = results[str(matchday)]
                sp = spo + matchday_results
                results[str(matchday)] = sp
            except KeyError:
                results[str(matchday)] = matchday_results
    return results


def get_match_result(matchday_date, zeile):
    teams = zeile.findAll('span', {"class": "sc-lhxcmh-0 jOiTFY sc-1e04cm7-5 kUXbCS"})
    team_home = teams[0].text.strip()
    team_guest = teams[1].text.strip()
    final_score_str = 'n/a'
    final_score = zeile.find("span", {"class": "sc-lhxcmh-0 hNbCpC"})
    if final_score is not None:
        final_score_str = final_score.text.strip()
    else:
        # not yet finished or cancelled
        final_score = zeile.find("span", {"class": "sc-bdfBwQ fwsGyn sc-1rxhndz-6 iBFqGw"})
        if final_score is not None:
            final_score_str = '({})'.format(final_score.text.strip())
    result = dict()
    result['datum'] = matchday_date
    result['name_heim'] = team_home
    result['name_gast'] = team_guest
    try:
        result['tore_heim'] = final_score_str.split(':')[0]
        result['tore_gast'] = final_score_str.split(':')[1]
    except:
        pass
    result['endstand'] = final_score_str
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
        platz = row.find('span', {"sc-lhxcmh-0 jOiTFY"}).text.strip()
        mannschaft = row.find('span', {"sc-lhxcmh-0 jOiTFY sc-1e04cm7-5 kUXbCS"}).text.replace('LIVE', '').strip()
        ergebnisse = row.findAll('span', {"class": "sc-lhxcmh-0 jOiTFY"})
        spiele = ergebnisse[2].text.strip()
        tordiff = ergebnisse[5].text.strip()
        punkte = ergebnisse[6].text.strip()

        veraenderung = None # row.find('span', {"class": ""})
        platzierung = dict()
        platzierung['platz'] = platz
        platzierung['mannschaft'] = mannschaft
        platzierung['spiele'] = spiele
        platzierung['tordiff'] = tordiff
        platzierung['punkte'] = punkte
        # platzierung['veraenderung'] = veraenderung.text.strip()
        ligatabelle.append(platzierung)
    return ligatabelle


def print_ergebnisse(liga, spieltag, ergebnisse, f_erg):
    html = html_head
    html += '<body class="erg"><table><caption>Ergebnisse {}. Spieltag {}</caption>'.format(spieltag, liga)
    print('Ergebnisse {}. Spieltag {}\n'.format(spieltag, liga), file=f_erg)
    # [::-1] damit die Liste chronologisch sortiert ist
    for erg in ergebnisse[::-1]:
        datum = datetime.datetime.strptime(erg['datum'], '%Y-%m-%d')
        wt_tag = '{}., {}'.format(wochentage[datum.date().weekday()], datum.strftime('%d.%m.' ))
        print('{} {:<20} : {:<20} {:<8}'.format(wt_tag, erg['name_heim'], erg['name_gast'], erg['endstand']), file=f_erg)
        html += f"<tr><td>{wt_tag}</td><td>{erg['name_heim']}</td><td>-</td>" \
                f"<td>{erg['name_gast']}</td><td>{erg['endstand']}</td></tr>"
    html += '</table></div></body></html>'
    print('\n\n', file=f_erg)
    f_erg.flush()
    # show_html(html)
    options = {'width': 1200, 'transparent': '','quiet': ''}
    imgkit.from_string(html, path + liga + '_Ergebnis.png', options=options)


def print_tabelle(liga, spieltag, ligatabelle, f_tab):
    print('{} {}. Spieltag\n'.format(liga, spieltag), file=f_tab)
    print('{:<5} {:<20} {:<8} {:<8} {:<8}'.format('platz', 'mannschaft', 'spiele', 'tordiff','punkte'), file=f_tab)
    for pos in ligatabelle:
        print('{:<5} {:<20} {:>5} {:>8} {:>8}'.format(pos['platz'], pos['mannschaft'], pos['spiele'], pos['tordiff'],pos['punkte']), file=f_tab)
    print('\n\n', file=f_tab)
    f_tab.flush()
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

        f_erg = open(path + 'ergebnisse.txt', 'w')
        f_tab = open(path + 'tabellen.txt', 'w')

        for li in ligen:
            spieltag = -1
            liga = li['name']
            print(liga)
            url = li['url']
            tabelle = get_tabelle(url + '/standing')

            for pos in tabelle:
                spieltag = max(spieltag, int(pos['spiele']))
            print_tabelle(liga, spieltag, tabelle, f_tab)
            erg = get_results_by_date(url + '/matches?pointer=prev', spieltag)
            print_ergebnisse(liga, spieltag, erg[str(spieltag)], f_erg)
        print('fertig')
        f_erg.flush()
        f_erg.close()
        f_tab.flush()
        f_tab.close()
    else:
        print(path + ' nicht gefunden, bitte erstellen')
    exit(0)

if __name__ == "__main__":
    main()
