import requests, hashlib
def get_FB_token(email, password): return login_fb(email, password)['access_token']
def login_fb(email, password):
    url = "https://api.facebook.com/restserver.php"
    api_key = "882a8490361da98702bf97a021ddc14d"
    API_SECRET = '62f8ce9f74b12f84c123cc23437a4a32'
    params = {
        "api_key": api_key,
        "credentials_type": "password",
        "email": email,
        "format": "JSON",
        "generate_machine_id": "1",
        "generate_session_cookies": "1",
        "locale": "en_US",
        "method": "auth.login",
        "password": password,
        "return_ssl_resources": "0",
        "v": "1.0",
        "sig": hashlib.md5(("api_key=" + api_key + "credentials_type=passwordemail=" \
                            + email + 'format=JSONgenerate_machine_id=1generate_session_cookies=1locale=en_USmethod=auth.loginpassword=' \
                            + password + 'return_ssl_resources=0v=1.0' + API_SECRET).encode('utf-8')).hexdigest()
    }
    res = requests.get(url, params=params)
    return res.json()
