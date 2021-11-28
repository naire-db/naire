import requests

with open('test.txt', 'rb') as f:
    url = 'http://localhost:8000/attachment/upload/'
    resp = requests.post(url, files ={'file' : f})
    if resp.ok:
        print('success')
    else:
        print('fail')
