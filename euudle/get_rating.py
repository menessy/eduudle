from httplib import *
import json, re

web = 'eduudle.c-nodes.com'

header = {
    'Host': 'js.rating-widget.com',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:17.0) Gecko/20130402 Firefox/17.0',
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.5',
    'Referer': 'http://' + web + '/search?term=I+want+to+learn...&price=0%3B100',
}

def getrating(number):
    global web
    url = '/action/load.php?next=&ratings=%5B%7B%22urid%22%3A%22' + number + '%22%2C%22type%22%3A%22star%22%7D%5D&uid=42894f8d116361f5afbac61a090349e8&huid=97153&v=1.5.3&source=Website&url=http%3A%2F%2F'+ web +'%2Fsearch%3Fterm%3DI%2Bwant%2Bto%2Blearn...%26price%3D0%253B100&sw=1366&sh=768&cguid=1365082297580'
    global header
    conn = HTTPConnection('js.rating-widget.com',80)
    conn.request('GET', url,None,header)
    response = str(conn.getresponse().read())
    response = re.sub('RW._loadCallback\(','',response)
    response = re.sub('\);','',response)
    rating =  json.loads(response)['data']['ratings']
    rating =  dict(rating[0])
    
    return ( rating['votes'] , rating['rate']/rating['votes'] )
    

    
