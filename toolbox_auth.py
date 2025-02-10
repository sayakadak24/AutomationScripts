# 78492
# Sayak Adak
import requests
from bs4 import BeautifulSoup

def get_toolbox_cookies(username, password):
    initial_response = requests.get('https://toolbox.leisure-group.eu/crmsys/')
    initial_soup = BeautifulSoup(initial_response.content, "html.parser")
    tb_sec_token = initial_soup.find('input', {'name': 'tb_sec_token'})['value']

    PHPSESSID = ''
    for cookie in initial_response.cookies:
        if cookie.name == 'PHPSESSID':
            PHPSESSID = cookie.value

    cookies = {
        'PHPSESSID': PHPSESSID,
    }

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': 'https://toolbox.leisure-group.eu',
        'Referer': 'https://toolbox.leisure-group.eu/',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0',
        'sec-ch-ua': '"Chromium";v="124", "Microsoft Edge";v="124", "Not-A.Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }

    params = {
        'action': 'login',
    }

    data = {
        'tb_sec_token': tb_sec_token,
        'ks_username': username,
        'ks_password': password,
    }

    response = requests.post('https://toolbox.leisure-group.eu/', params=params, cookies=cookies, headers=headers, data=data, allow_redirects=False)
    set_cookie_header = response.headers.get('Set-Cookie', '')
    cookies = {}
    for cookie in set_cookie_header.split(', '):
        name, value = cookie.split('=', 1)
        cookies[name] = value.split(';')[0]

    # Accessing hs_userid and hs_ticket from cookies
    hs_userid = cookies.get('hs_userid', '')
    hs_ticket = cookies.get('hs_ticket', '')

    return {
        'hs_userid': hs_userid,
        'hs_ticket': hs_ticket,
        'PHPSESSID': PHPSESSID,
    }
