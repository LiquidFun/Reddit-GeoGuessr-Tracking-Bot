import urllib.parse
import urllib.request
import sys, os

def pasteToPastebin(name, text):

    pastebin_API_file = open(os.path.join(os.path.dirname(__file__), "PastebinAPIAccess.txt"))
    lines = []
    for line in pastebin_API_file:
        lines.append(line)

    #print(lines[0])

    url = "http://pastebin.com/api/api_post.php"
    values = {'api_option' : 'paste',
               'api_dev_key' : lines[0].strip(),
               'api_paste_code' : text,
               'api_paste_private' : '1',
               'api_paste_name' : name,
               'api_paste_expire_date' : 'N'}
               #'api_paste_format' : 'None'}
               #'api_user_key' : 'User Key Here',
     
    data = urllib.parse.urlencode(values)
    data = data.encode('utf-8') # data should be bytes
    req = urllib.request.Request(url, data)
    with urllib.request.urlopen(req) as response:
        the_page = response.read()
    #print(the_page[2:len(the_page) - 1])

    return the_page

if __name__ == '__main__':
    pasteToPastebin("Some name", "Test1\n\nTExt2\tTe33")