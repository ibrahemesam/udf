# Graph API explorer: https://developers.facebook.com/tools/explorer
from urllib.parse import urlencode
from re import compile as re_compile
from html import unescape
from .exceptions import IncorrectEmail, IncorrectPassword, UsernameDoesNotExist
from requests import get as GET
import requests

FB_URL = 'https://m.facebook.com'
# FB_MBASIC_URL = 'https://mbasic.facebook.com'
IE6userAgent = 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0; WOW64; Trident/4.0; SLCC1)'
# ChromeUserAgent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
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
    s.post(
            FB_URL+unescape(LOGIN_FORM_ACTION_REGX.search(formHtml).group(1)),
            data = {
                'email': email,
                'pass': password,
                **dict((inp[0], unescape(inp[1])) for inp in LOGIN_FORM_INPUTS_REGX.findall(formHtml)),
            },
        )
    s.close()
    if not 'c_user' in s.cookies:
        if 'sfiu' in s.cookies:
            raise IncorrectPassword('if you sure it is correct, then Facebook has rejected your login from this IP')
        else:
            raise IncorrectEmail('if you sure it is correct, then Facebook has rejected your login from this IP')
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

DEVELOPER_ACCESS_TOKEN_REGX = re_compile(r'&long_lived_token=(.*)"')
DEFAULT_PERMISSIONS = ('pages_read_engagement', 'pages_show_list')
PAGES_POSTS_PERMISSIONS = ('pages_manage_posts', 'pages_read_engagement')
def get_fb_app_developer_user_access_token(app_id, dev_fb_cookies, extra_permissions=()):
    # NB: retuns long_lived token
    permissions = tuple(set((*DEFAULT_PERMISSIONS, *extra_permissions)))
    s = requests.Session()
    s.cookies.update(dev_fb_cookies)
    headers = {
        'referer': f'https://www.facebook.com/v15.0/dialog/oauth?response_type=token&display=popup&client_id={app_id}&redirect_uri=https%3A%2F%2Fdevelopers.facebook.com%2Ftools%2Fexplorer%2Fcallback%3Fmethod%3DGET%26path%3Dme%252Faccounts%26version%3Dv15.0&auth_type=rerequest&scope=' + '%2C'.join(permissions),
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
    }
    r = s.get(
        f'https://www.facebook.com/forced_account_switch?next=https%3A%2F%2Fm.facebook.com%2Fv2.11%2Fdialog%2Foauth%3F?response_type=token&display=popup&client_id={app_id}&redirect_uri=https%3A%2F%2Fdevelopers.facebook.com%2Ftools%2Fexplorer%2Fcallback%3Fmethod%3DGET%26path%3Dme%252Faccounts%26version%3Dv15.0&auth_type=rerequest&scope=' + '%2C'.join(permissions),
        allow_redirects = False,
        headers = headers,
        )
    user_scopes = '&'.join((f'user_scopes[{idx}]={i}' for idx, i in enumerate(permissions)))
    r = s.post(
        f'https://www.facebook.com/dialog/oauth/business/cancel/?app_id={app_id}&version=v15.0&{user_scopes}&redirect_uri=https%3A%2F%2Fdevelopers.facebook.com%2Ftools%2Fexplorer%2Fcallback%3Fmethod%3DGET%26path%3Dme%252Faccounts%26version%3Dv15.0&response_types[0]=token&display=popup&action=finish&return_scopes=false&return_format[0]=access_token&tp=unspecified&sdk=&selected_business_id=&set_token_expires_in_60_days=false',
        headers = headers,
        data = dict(
            ( inp[0], unescape(inp[1]) ) for inp\
                in LOGIN_FORM_INPUTS_REGX.findall(
                        LOGIN_FORM_HTML_REGX.search(r.text).group(1)
                    )
        ),
        allow_redirects = False
    )
    s.close()
    return DEVELOPER_ACCESS_TOKEN_REGX.findall(r.text)[0]

def is_token_valid(token):
    # r = requests.get('https://graph.facebook.com/oauth/access_token_info?access_token=' + token ).json()
    # if 'expires_in' in r:
    #     if r['expires_in'] > 0:
    #         return True
    # return False
    j = requests.get('https://graph.facebook.com/me?access_token=' + token ).json().keys()
    if ('name' in j) and ('id' in j):
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

INVALID_COOKIES_PATTERNS = (
    'data-testid="royal_login_button"',
    '<a href="https://www.facebook.com/recover/',
    '<form id="login_form"',
    'action="https://www.facebook.com/login/',
)
def is_cookies_valid(cookies):
    t = GET('https://facebook.com/profile.php', cookies = cookies).text
    for i in INVALID_COOKIES_PATTERNS:
        if i in t:
            return False
    return True

def get_uid_by_username(username, access_token):
    j = GET(f'https://graph.facebook.com/{username}?access_token={access_token}').json()
    if 'id' in j:
        return j['id']
    else:
        raise UsernameDoesNotExist(str(j))

def get_page_access_token(page_uid : str, user_access_token):
    j = GET(f'https://graph.facebook.com/me/accounts?access_token={user_access_token}').json()
    for p in j['data']:
        if p['id'] == page_uid:
            return p['access_token']
