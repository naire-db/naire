import requests

with open('test.txt', 'rb') as f:
    url = 'http://localhost:8000/attachment/upload/'
    # url = 'https://httpbin.org/post'
    files = {'file': f}
    values = {'name': 'test.txt'}
    resp = requests.post(url, files=files, data=values)
    print(resp.text)
    print(resp.status_code)
    if resp.ok:
        print('success')
    else:
        print('fail')