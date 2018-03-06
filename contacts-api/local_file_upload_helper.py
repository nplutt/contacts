import requests


data = open('../../Downloads/convertcsv.csv', 'rb').read()
res = requests.post(url='https://eaa2qsuq62.execute-api.us-west-2.amazonaws.com/api/upload',
                    data=data,
                    headers={'Content-Type': 'application/octet-stream'})
