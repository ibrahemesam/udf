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


###########################################
###########################################
###########################################
###########################################
if __name__ == '__main__':
    email = "iimosa7777@gmail.com"
    password = "hemo@3425"
    # print(login_fb(email, password))
    cookies = {'c_user': '100009073119269', 'datr': '2pfQY-7-Lr73qwCYtiR7udcB', 'fr': '04BieGJT1cWrn95zp.AWV7t-8qzgHSCZkmBFWpb_qEwis.Bj0Jfa.hC.AAA.0.0.Bj0Jfa.AWXuuDfIj5U', 'm_page_voice': '100009073119269', 'noscript': '1', 'sb': '2pfQYyDDXh0XyrFHJVHOKJ8s', 'xs': '10%3AbxulXEfkAvIpnA%3A2%3A1674614747%3A-1%3A7651'}
    # cookies = login_fb('01553905044', 'eylul1234')
    # cookies = {'c_user': '100057156189000', 'datr': 'QkXPY3pKyVvVCNMV7TVD_gBB', 'fr': '0G27JHbzSuBfZhDTc.AWUbi2Dnmi4UZRjyJcmz7A1G2b8.Bjz0VC.ex.AAA.0.0.Bjz0VC.AWXVbXEFH9o', 'm_page_voice': '100057156189000', 'noscript': '1', 'sb': 'QkXPY9XDeTaDrP6lLcI2KAeX', 'xs': '50%3AgMaWU3qdHLrj3A%3A2%3A1674528067%3A-1%3A9037'}
    # print(get_dummy_fb_app_user_access_token(cookies))
    # loar_cookies = {'oas_user': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJjbGllbnRUeXBlIjoiYXBwIiwiY2xpZW50SWQiOjk5OSwidXVpZCI6IjIwMDAwMDA1MDA2OTQwNiIsInBsYXllcklkIjoiMjAwMDAwMDUwMDY5NDA2Iiwibmlja25hbWUiOiJcdTA2MmVcdTA2MjdcdTA2NDRcdTA2MmYiLCJ1c2VybmFtZSI6ImtoYWxlZC5mYXJoYTQwQHlhaG9vLmNvbSIsImxvZ2luR3JhbnRUeXBlIjoiZmFjZWJvb2siLCJpYXQiOjE2NzQ1Mzg2ODMsImV4cCI6MTY3NDU0NTg4MywibGlmZXRpbWUiOjcyMDAsInJvbGVzIjpbIlJPTEVfVVNFUiJdfQ.fo0irLi_Ut_7H2N_c3ctkWWVUb6Tk191ixQmSsGfO6o', 'oauth_saved_token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1dWlkIjoiMjAwMDAwMDUwMDY5NDA2IiwiaWF0IjoxNjc0NTM4NjgzLCJleHAiOjE2NzUxNDM0ODMsImxpZmV0aW1lIjo2MDQ4MDAsInJvbGVzIjpbIlJPTEVfUkVNRU1CRVJfTUUiXX0.JS_Wok0eGS4qPZLuQCf-pwI0JYxJbITjpfeqQolDZzg'}
    # dummy_access_token = 'EAACD6tUubHgBANYTOsSIBWbGeTcPRDYlOZAmZBKBl97ztRfAi7t9r98O2Imy8TqcxypSniw00oqgGjPaAivYcCqRSGgW0flvTGbEAfxuBZAKFSqac7cVKv0BmvE787KiIBDIIZBfevzZB3tjrVZBzeQZC3jFI3PdQ8gHWehZBrShLQZDZD'
    # print(is_token_valid(dummy_access_token))
    # print(is_token_long_lived(dummy_access_token))
    # print(get_dummy_fb_app_user_access_token(cookies))

    """
    TODO:  make selenium script to:-
    [ ] login facebook
    [ ] join a facebook group
    [ ] post on facebook group
    """

    # def get_FB_restserver_token(email, password):
    #     import hashlib
    #     url = "https://api.facebook.com/restserver.php"
    #     api_key = "302666193809711"
    #     API_SECRET = '4d6897f71f6486794c6bd8a6c27dcbbe'
    #     params = {
    #         "api_key": api_key,
    #         "credentials_type": "password",
    #         "email": email,
    #         "format": "JSON",
    #         "generate_machine_id": "1",
    #         "generate_session_cookies": "1",
    #         "locale": "en_US",
    #         "method": "auth.login",
    #         "password": password,
    #         "return_ssl_resources": "0",
    #         "v": "1.0",
    #         "sig" : hashlib.md5(("api_key="+api_key+"credentials_type=passwordemail="\
    #             +email+'format=JSONgenerate_machine_id=1generate_session_cookies=1locale=en_USmethod=auth.loginpassword='\
    #                 +password+'return_ssl_resources=0v=1.0'+API_SECRET).encode('utf-8')).hexdigest()
    #         }
    #     return requests.get(url, params=params).json()['access_token']
    ## to get client_token of this FB APP
    # APP_ID = '350685531728'
    # API_KEY = '882a8490361da98702bf97a021ddc14d'
    # API_SECRET = '62f8ce9f74b12f84c123cc23437a4a32'
    ## NB: app access token is: APP_ID|API_SECRET
    # res = requests.get(f'https://graph.facebook.com/oauth/access_token?client_id={API_KEY}&client_secret={API_SECRET}&grant_type=client_credentials')
    # print(res.json()['access_token']) #302666193809711|ZsbXIwqB1D19vdOq4kPWiUq4v8c
    # exit()
    # """
    # embed facebook login page in the ui:
    #     url: https://www.facebook.com/login.php?skip_api_login=1&api_key=394718192364866&kid_directed_site=0&app_id=394718192364866&signed_next=1&next=https%3A%2F%2Fwww.facebook.com%2Fv2.11%2Fdialog%2Foauth%3Fapp_id%3D394718192364866%26cbt%3D1674316650194%26channel_url%3Dhttps%253A%252F%252Fstaticxx.facebook.com%252Fx%252Fconnect%252Fxd_arbiter%252F%253Fversion%253D46%2523cb%253Df382e846501a324%2526domain%253Dloar.creaction-network.com%2526is_canvas%253Dfalse%2526origin%253Dhttps%25253A%25252F%25252Floar.creaction-network.com%25252Ff31c49bf7ee7018%2526relation%253Dopener%26client_id%3D394718192364866%26display%3Dpopup%26domain%3Dloar.creaction-network.com%26e2e%3D%257B%257D%26fallback_redirect_uri%3Dhttps%253A%252F%252Floar.creaction-network.com%252F%253Ffbfirst%253D0%2526fbfirst%253D0%2526fbfirst%253D0%26locale%3Dar_AR%26logger_id%3Df228b06fc99a3d%26origin%3D1%26redirect_uri%3Dhttps%253A%252F%252Fstaticxx.facebook.com%252Fx%252Fconnect%252Fxd_arbiter%252F%253Fversion%253D46%2523cb%253Df10aacdf762c1ac%2526domain%253Dloar.creaction-network.com%2526is_canvas%253Dfalse%2526origin%253Dhttps%25253A%25252F%25252Floar.creaction-network.com%25252Ff31c49bf7ee7018%2526relation%253Dopener%2526frame%253Df1557672c3095ac%26response_type%3Dtoken%252Csigned_request%252Cgraph_domain%26sdk%3Djoey%26version%3Dv2.11%26ret%3Dlogin%26fbapp_pres%3D0%26tp%3Dunspecified&cancel_url=https%3A%2F%2Fstaticxx.facebook.com%2Fx%2Fconnect%2Fxd_arbiter%2F%3Fversion%3D46%23cb%3Df10aacdf762c1ac%26domain%3Dloar.creaction-network.com%26is_canvas%3Dfalse%26origin%3Dhttps%253A%252F%252Floar.creaction-network.com%252Ff31c49bf7ee7018%26relation%3Dopener%26frame%3Df1557672c3095ac%26error%3Daccess_denied%26error_code%3D200%26error_description%3DPermissions%2Berror%26error_reason%3Duser_denied&display=popup&locale=en_GB&pl_dbl=0
    # to allow opening facebook in iframe:
    #     install this chrome extension:
    #         https://chrome.google.com/webstore/detail/ignore-x-frame-headers/gleekbfjekiniecknbkamfmkohkpodhe/related
    #     to install a chrome extension in electron:
    #         https://stackoverflow.com/questions/53341132/how-can-i-add-a-custom-chrome-extension-to-my-electron-app
    # """
    ## access_token debugger: https://developers.facebook.com/tools/debug/accesstoken
    ## access_token=EAAFmZCn2kbUIBAEOFe6DPfOUPgxsUq5O0SlVJviZAfYbUA8cLrovD8hSvjNn0SRig8afCNfCtA0d2mD59wOi4XUxYxdkV28oMijQpOEKYBNZAYVbUMP2262055MNKZAJppZCPPZAia5NZBiI5Hg6WQQBSjUH7TYBAqIFSxpjmAg2bQ2Qu4IRCz8

    """



    4) generate long_lived page_access_token

    curl -i -X GET "https://graph.facebook.com/PAGE-ID?
    fields=access_token&
    access_token=USER-ACCESS-TOKEN"
    
    {
    "access_token":"PAGE-ACCESS-TOKEN",
    "id":"PAGE-ID"              
    }

    If you used a short-lived User access token, the Page access token is valid for 1 hour.
    If you used a long-lived User access token, the Page access token has no expiration date.
    """

    # publish_to_groups
    import facebook

    graph = facebook.GraphAPI(access_token="your_token", version="2.12")

    app_id = "1231241241"
    group_id = '272619198066873'
    canvas_url = "https://domain.com/that-handles-auth-response/"
    perms = ["manage_pages","publish_pages"]
    fb_login_url = graph.get_auth_url(app_id, canvas_url, perms)
    print(fb_login_url)




    # Upload an image with a caption. for a Group.
    graph.put_photo(message='', image=open("img.jpg", 'rb'),
                    album_path=group_id + "/picture")


    # https://facebook-sdk.readthedocs.io/en/latest/api.html?highlight=put_photo#put-photo
    # https://medium.com/nerd-for-tech/automate-facebook-posts-with-python-and-facebook-graph-api-858a03d2b142

    # https://stackoverflow.com/questions/17197970/facebook-permanent-page-access-token/17234650#17234650
    # https://developers.facebook.com/tools/explorer/

    dummy_token = 'EAACD6tUubHgBANYTOsSIBWbGeTcPRDYlOZAmZBKBl97ztRfAi7t9r98O2Imy8TqcxypSniw00oqgGjPaAivYcCqRSGgW0flvTGbEAfxuBZAKFSqac7cVKv0BmvE787KiIBDIIZBfevzZB3tjrVZBzeQZC3jFI3PdQ8gHWehZBrShLQZDZD'
    wa_sender_token = 'EAAOrkAOcwmABAPtIm5QfZAhKiOc9yBHHJrxZBgmswzRL7j213Q5v2buYP1vWRqo9fQDE6XHFY7YyhlwsZCUcyh429Ly9BmsJns9fEWGj5OYbQ06HBdbZAzMywFEEcWSHjy9EJESqseiUIMD9N1rRu7Bc8AC65ifXHCI5GWjlt9x5pG8x0KLIVDsqAZAG2sC4TOA57WWRDNJeDFf4BZAoE2'
    wa_sender_token_long_lived = 'EAAOrkAOcwmABAGZCC1BjZBdVSL78hOpBIbSBl9ZAWkkb3mC5flfSo5h7U4ieRZCi8ZAZAmP3HslZBCH3ZBn9iiq0AsjSbTNM3CzdDKd9VJDPFWGN1hANnEQpBKCV2Hlm3ZCzGIukzLYxAzUKZBf5H4pq3MY6mcmUpuaHKxzhABPptgtQZDZD'
    page_token = 'EAAOrkAOcwmABAKL40BDzvvqxbNovSw645tNuZCAB4ZCgTSPFCMuRi5sxOZCbCqguLFyBCZAmGQBloIM9SZCm3boqVMgMcT7TcCr3I8wkC6EkqEwjGvN1Msw24IzeWKFyyQIGDKSrhEs7A4EYwCsZBXXivZC4TDmCK0GXmWCAwX6nB2l8Gxe0cp1whVLVD7yvgWYZCagNH10KrwZDZD'
    page_token_long_lived = 'EAAOrkAOcwmABAIJA5V827eBBWhXIhd2MEsPVbNRSZCwEdlE2bDCjKsteZBgGLV8Fy143QFL6r81D9gCaGFzuBIeK1ZAWmcer9T3lbJBCrhZA7dxdCm2SfQdmPcZANbTeU7FcCUuU9xFy8ZANBCtUjhHpkdNTZB91ZAtzV5I4njqZBBPq8ZAnNSUPFk'

    import requests
    access_token = page_token     # Obtained from 
    app_id = "1033059954377312"          # Obtained from https://developers.facebook.com/        
    client_secret = "cb7cd31370064322a881d0d8f380909f"    # Obtained from https://developers.facebook.com/

    long_lived_token = requests.get("https://graph.facebook.com/oauth/access_token", params={
        'grant_type': 'fb_exchange_token',
        'client_id': app_id,
        'client_secret': client_secret,
        'fb_exchange_token': access_token,
    }).json().get('access_token')
    print(long_lived_token)
    exit()

    from requests import get
    r = get('https://graph.facebook.com/me/accounts', params= {
        # 'fields': 'access_token',
        'access_token': wa_sender_token,
    })

    print(r.status_code)
    print(r.text)





    '''
    function setCookie(name,value,days) {
        var expires = "";
        if (days) {
            var date = new Date();
            date.setTime(date.getTime() + (days*24*60*60*1000));
            expires = "; expires=" + date.toUTCString();
        }
        document.cookie = name + "=" + (value || "")  + expires + "; path=/";
    }
    function getCookie(name) {
        var nameEQ = name + "=";
        var ca = document.cookie.split(';');
        for(var i=0;i < ca.length;i++) {
            var c = ca[i];
            while (c.charAt(0)==' ') c = c.substring(1,c.length);
            if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length,c.length);
        }
        return null;
    }
    function eraseCookie(name) {   
        document.cookie = name +'=; Path=/; Expires=Thu, 01 Jan 1970 00:00:01 GMT;';
    }
    '''

    '''
    //TODO: exception if can't post on a page || group (not member)
    // post to facebook 
    set cookie i_user=100067879509057 (page_uid) to interact as this page
    # navigate to page | group | profile
    nav to: https://www.facebook.com/profile.php?id=100069444571453

    (wait4 document.querySelector('div[role=main] a[aria-label*=Timeline]'))
        .parentNode.querySelector('span').click()

    # btn_post = wait4 document.querySelector("form[method=post] > input[type=submit]")
    btn_post = wait4 document.querySelector('div[aria-label="Post"]')

    el = document.querySelector("form[method=post] div[role=textbox]")
    function send_keys(el, string){
        const dataTransfer = new DataTransfer();
        dataTransfer.setData('text', string);
        el.dispatchEvent(new ClipboardEvent('paste', {
                clipboardData: dataTransfer,
                bubbles: true
            })
        )
    }
    // add text to post
    send_keys(el, 'cool unicode string with emojis')
    // add photo to post
    document.querySelector('div[aria-label="Photo/Video"]').click()
    wait4 document.querySelector('input[accept*=image][type=file]')
        .send_keys(img_path)
    (until image is uploaded (until btn_post is clickable))
        until: el.get_attribute('aria-disabled') != 'true'

    // publish the post
    btn_post.click()
    '''

    # udf facebook
    # clean todo