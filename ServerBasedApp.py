import argparse
import socket
import threading
from bs4 import BeautifulSoup
import requests

HOST = '127.0.0.1'
PORT = 65534
ADDR = (HOST, PORT)
HEADER = 32
FORMAT = 'utf-8'



class server:

    def __init__(self):
        self.run()

    def run(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(ADDR)
        self.sock.listen(10)
        print(f'[LISTENING...] server is listening at {ADDR}')
        while True:
            conn, addr = self.sock.accept()
            thread = threading.Thread(target=self.handle, args = (conn, addr))
            thread.start()
            # print(f'[ACTIVE CONNECTIONS] { threading.active_count() - 1 }')



    def handle(self, conn, addr):
        print("="*50)
        print(f'[NEW CONNECTION] {addr} connected' )

        msg_length = conn.recv(HEADER).decode(FORMAT)
        msg_length = int(msg_length)
        message = conn.recv(msg_length).decode(FORMAT)

        print(f'[PROCCESSING] the scraping on {message}')
        responseData = self.processing(message)
        leaf, img = responseData
        sendMessage = str(leaf) + '.' + str(img)
        conn.send(sendMessage.encode(FORMAT))
        print('[COMPLETED] the result has been sent')
        print("="*50)

        
        conn.close()
        


    def processing(self, data):

        parsedURl = data.split('//')
        if len(parsedURl) == 1:
            try:
                URL = 'https://' + parsedURl[0]
                page = requests.get(URL)
            except:
                URL = 'http://' + parsedURl[0]
        else:
            URL = data
        page = requests.get(URL)


        soup = BeautifulSoup(page.content, 'html.parser')

        # Scraping the number of paragraphs
        paragraphList = soup.find_all('p')
        leafCount = 0
        for paragraph in paragraphList:
            if paragraph.find('p'):
                continue
            leafCount += 1

        # Sceaping the images number
        imgList = soup.find_all('img')
        imgCount = len(imgList)


        return (leafCount, imgCount)    



class client:


    def __init__(self, url):
        self.run(url)


    def run(self, url):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(ADDR)
        
        msg = url.encode(FORMAT)
        msgLength = len(msg)
        sendLength = str(msgLength).encode(FORMAT)
        # Modify sendLength to fill whole HEADER
        sendLength += b' ' * (HEADER - len(sendLength))

        # Sending the url to the server for further proccessing
        self.sock.send(sendLength)
        self.sock.send(msg)

        # Receiving respond from the server
        response = self.sock.recv(HEADER)

        leaf, img = response.decode(FORMAT).split('.')

        self.sock.close()

        # print('[RECEIVED] the result is:')
        # print(f'''Leaf Paragraph: {leaf}
        # Images: {img}''')
        print(img, leaf)

    


def main():
    # top-level parser
    parser = argparse.ArgumentParser(description='Send url and get the number of\
        leaf paragraphs and images')
    # subparser
    subparsers = parser.add_subparsers()

    parserServer = subparsers.add_parser('server', help='activate the server')

    parserClient = subparsers.add_parser('client', help='activate the client')
    parserClient.add_argument('-p', required=True, help='Domain which you \
        want get information from')
    
    args = parser.parse_args()

    try:
        object = client(args.p)
    except:
        object = server()
    

    

        
if __name__ == '__main__':
    main()



