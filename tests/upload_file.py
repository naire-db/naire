import requests

with open('test.txt', 'rb') as f:
<<<<<<< HEAD
    url = 'http://localhost:8000/attachment/upload_file/'
    # url = 'https://httpbin.org/post'
    files = {'file': f}
    values = {'name': 'test.txt'}
    resp = requests.post(url, files=files, data=values)
    print(resp.text)
    print(resp.status_code)
=======
    url = 'http://localhost:8000/attachment/upload/'
    resp = requests.post(url, files ={'file' : f})
>>>>>>> 375d08a (attachment: upload: impl (progressing))
    if resp.ok:
        print('success')
    else:
        print('fail')
