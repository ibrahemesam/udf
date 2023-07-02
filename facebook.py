from urllib.parse import urlencode
from re import compile as re_compile
from html import unescape
from .exceptions import IncorrectEmail, IncorrectPassword
import requests

FB_URL = 'https://m.facebook.com'
IE6userAgent = 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0; WOW64; Trident/4.0; SLCC1)'
headers = { 'User-Agent': IE6userAgent, 'upgrade-insecure-requests': '1' }
LOGIN_FORM_HTML_REGX = re_compile(r'<form(.*)</form>')
LOGIN_FORM_ACTION_REGX = re_compile(r'action="([^< ]*)"')
LOGIN_FORM_INPUTS_REGX = re_compile(r'<input[^<]*name="([^<"]*)"[^<]*value="([^<"]*)"[^<]*/>')
URL_ACCESS_TOKEN_REGX = re_compile(r'access_token=([^&]*)&')

DUMMY_FB_APP_ID = '145044622175352' # this app is StackOverflow FB APP
DUMMY_WEBSITE = 'https://stackauth.com/auth/oauth2/facebook'
DUMMY_FB_APP_LOGIN_URL = FB_URL + '/v2.11/dialog/oauth?' + urlencode({
    'app_id': DUMMY_FB_APP_ID,
    'domain': DUMMY_WEBSITE,
    'is_canvas' : 'false',
    'origin': DUMMY_WEBSITE,
    'relation': 'opener',
    'client_id': DUMMY_FB_APP_ID,
    'display': 'popup',
    'locale': 'ar_AR',
    'redirect_uri': DUMMY_WEBSITE,
    'is_canvas': 'false',
    'relation': 'opener',
    'response_type': 'token',
    'sdk': 'joey',
    'version': 'v2.11',
    'scope': 'manage_pages,publish_to_groups,pages_read_engagement'
  })



def login_fb(email, password):
    s = requests.Session()
    formHtml = LOGIN_FORM_HTML_REGX.search(s.get(FB_URL, headers=headers).text).group(1)
    post_body = dict((inp[0], unescape(inp[1])) for inp in LOGIN_FORM_INPUTS_REGX.findall(formHtml))
    post_body['email'] = email
    post_body['pass'] = password
    s.post(FB_URL+unescape(LOGIN_FORM_ACTION_REGX.search(formHtml).group(1)), data=post_body, headers=headers)
    s.close()
    if not 'c_user' in s.cookies:
        if 'sfiu' in s.cookies:
            raise IncorrectPassword()
        else:
            raise IncorrectEmail()
    return dict(s.cookies)

def get_dummy_fb_app_user_access_token(fb_cookies):
    s = requests.Session()
    s.cookies.update(fb_cookies)
    while True:
        r = s.get(DUMMY_FB_APP_LOGIN_URL, allow_redirects=False)
        if 'Location' in r.headers:
            url = r.headers['Location']
            break
        formHtml = LOGIN_FORM_HTML_REGX.search(r.text).group(1)
        r = s.post(
            FB_URL+unescape(LOGIN_FORM_ACTION_REGX.search(formHtml).group(1)),
            data=dict((inp[0], unescape(inp[1])) for inp in LOGIN_FORM_INPUTS_REGX.findall(formHtml)),
            allow_redirects=False
            )
        if 'Location' in r.headers:
            url = r.headers['Location']
            break
        raise Exception('Something went wrong with this method of LOAR FB App Login')
    s.close()
    return URL_ACCESS_TOKEN_REGX.search(url).group(1)

def is_token_valid(token):
    r = requests.get('https://graph.facebook.com/oauth/access_token_info?access_token=' + token ).json()
    if 'expires_in' in r:
        if r['expires_in'] > 0:
            return True
    return False

class TokenInvalid(Exception): pass
def is_token_long_lived(token):
    r = requests.get('https://graph.facebook.com/oauth/access_token_info?access_token=' + token ).json()
    if 'expires_in' in r:
        if r['expires_in'] > 10800: # 3 Hours
            return True
        elif r['expires_in'] > 0:
            return False
    raise TokenInvalid()

