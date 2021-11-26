from requests import session

login_url = 'http://localhost:8000/auth/login/'
login_data = {'username_or_email': 'alvin', 'password':'123456'}

with session() as s:
    r = s.post(login_url, json=login_data)
    print(r.status_code)
    url = 'http://localhost:8000/auth/change_password/'
    data = {'password': '123456', 'new_password':'12345678'}
    r = s.post(url, json=data)
    print(r.status_code)
