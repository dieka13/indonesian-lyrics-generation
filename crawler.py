import os
import re
import requests
from bs4 import BeautifulSoup

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


def requests_retry_session(
    retries=3,
    backoff_factor=0.3,
    status_forcelist=(500, 502, 504),
    session=None,
):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session


artist_pattern = re.compile(r'([\w -.]+) \((\d+)\)')

if not os.path.exists('lyrics'):
    os.mkdir('lyrics')


artists = []
not_processed = []
total = 0
with open('lyrics/summary.txt', 'wb') as summ:
    for i_page in range(1, 38 + 1):

        req = requests_retry_session(retries=10, backoff_factor=1).get('http://liriklagu.co.id/daftar-penyanyi/{}/'.format(i_page))
        soup = BeautifulSoup(req.text, 'html.parser')

        for artist in soup.find_all('a', itemprop='item'):
            link = artist['href']
            name, count = artist_pattern.match(artist.span.string).groups()
            total += int(count)
            artists.append(artist['href'])
            summ.write('{}: {} ({}) \n'.format(name, count, link))
            print link, name, count

    print len(artists), total
    summ.write('\nTotal artist: {} \nTotal lyrics: {}'.format(len(artists), total))


#
for a in artists:

    artist_name = a.split('/')[-1].replace('.', '')
    print artist_name
    if not os.path.exists('lyrics/{}'.format(artist_name)):
        os.mkdir('lyrics/{}'.format(artist_name))

    req = requests_retry_session(retries=10, backoff_factor=1).get(a, timeout=60)
    soup = BeautifulSoup(req.text, 'html.parser')
    songs = [t.a['href'] for t in soup.find_all('li', itemprop='itemListElement')]

    artist_pages = soup.find('ul', class_='pagination')
    if artist_pages:
        for c in artist_pages.children:
            if c.a['href'].startswith('http'):
                req = requests_retry_session(retries=10, backoff_factor=1).get(c.a['href'], timeout=60)
                soup = BeautifulSoup(req.text, 'html.parser')
                songs.extend([t.a['href'] for t in soup.find_all('li', itemprop='itemListElement') if t.a['href']])


    #
    for s in songs:

        title = s.split('/')[-1].replace('.', '')
        # print title

        if os.path.exists('lyrics/{}/{}.txt'.format(artist_name, title)):
            print 'skipping ({})'.format(s)
            continue

        try:
            req = requests_retry_session(retries=10, backoff_factor=1).get(s, timeout=60)
            soup = BeautifulSoup(req.text, 'html.parser')
            lyric = soup.find('p', itemprop='text')
            if lyric is not None:

                lyric_str = '\n'.join([t for t in lyric.stripped_strings])
                lyric_str = re.sub(r'[^\x00-\x7F]', '', lyric_str)

                with open('lyrics/{}/{}.txt'.format(artist_name, title), 'wb') as lyric_txt:
                    lyric_txt.write(lyric_str)

                print 'lyrics/{}/{}.txt ({})'.format(artist_name, title, s)

            else:
                raise Exception('no lyric found!')

        except Exception as e:

            print 'error when processing {} : {}'.format(s, e)
            not_processed.append((s, str(e)))


with open('lyrics/error.txt', 'wb') as err_txt:

    for url, err in not_processed:
        err_txt.write('{}: {}\n'.format(url, str(err)))
