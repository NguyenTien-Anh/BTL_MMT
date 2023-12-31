import socket

# Hàm khởi tạo server


def CreateServer(host, port):
    Server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    Server.bind((host, port))  # tạo server
    Server.listen(5)  # Lắng nghe tối đa 5 client kết nối cùng 1 lúc
    return Server


def ReadRequest(Client):
    re = ""
    Client.settimeout(1)  # đặt giá trị thời gian request = 1s --> TCP
    try:
        # Xử lí khi HTTP request > 1024 kí tự
        re = Client.recv(1024).decode()  # binary --> string
        while (re):
            re = re + Client.recv(1024).decode()
    except socket.timeout:  # fail after 1 second of no activity
        if not re:
            print("Didn't receive data! [Timeout]")
    finally:
        return re

# 2. Client connect Server + 3. Read HTTP Request


def ReadHTTPRequest(Server):
    re = ""
    # Sử dụng while để đảm bảo server nhận được request từ phía client và client nhận được respone từ server
    while (re == ""):
        Client, address = Server.accept()
        print("Client: ", address, " da ket noi toi Server")
        re = ReadRequest(Client)
    return Client, re


def SendFileIndex(Client):
    f = open("index.html", "rb")
    L = f.read()
    header = """HTTP/1.1 200 OK
Content-Length: %d

""" % len(L)
    print("-----------------HTTP respone  Index.html: ")
    print(header)
    header += L.decode()
    Client.send(bytes(header, 'utf-8'))


def MovePageIndex(Client):
    header = """HTTP/1.1 301 Moved Permanently
Location: http://127.0.0.1:8081/index.html

"""
    print("---------------HTTP respone move Index.html: ")
    print(header)
    Client.send(bytes(header, 'utf-8'))

# 4. Send HTTP Response  + 5. Close Server


def MoveHomePage(Server, Client, Request):
    if "GET /index.html HTTP/1.1" in Request:
        SendFileIndex(Client)
        Server.close()
        return True
    if "GET / HTTP/1.1" in Request:
        # Move Index.html
        MovePageIndex(Client)
        Server.close()
        # Trả về file index.html cho client
        Server = CreateServer("localhost", 8081)
        Client, Request = ReadHTTPRequest(Server)
        print("------------------HTTP request: ")
        print(Request)
        MoveHomePage(Server, Client, Request)
        return True


def CheckPass(Request):
    if "POST / HTTP/1.1" not in Request:
        return False
    if "Username=admin&Password=admin" in Request:
        return True
    else:
        return False


def Move404(Server, Client):
    header = """HTTP/1.1 301 Moved Permanently
Location: http://127.0.0.1:8082/404.html

"""
    print("HTTP respone: ")
    print(header)
    Client.send(bytes(header, "utf-8"))
    Server.close()


def SendFile404(Client):
    f = open("404.html", "rb")
    L = f.read()
    header = """HTTP/1.1 404 Not Found
Content-Type: text/html; charset=UTF-8
Content-Encoding: UTF-8
Content-Length: %d

""" % len(L)
    print("HTTP respone file 404.html: ")
    print(header)
    header += L.decode()
    Client.send(bytes(header, 'utf-8'))


def Send404(Server, Client):
    Server = CreateServer("localhost", 8082)
    Client, Request = ReadHTTPRequest(Server)
    print("HTTP Request: ")
    print(Request)
    if "GET /404.html HTTP/1.1" in Request:
        SendFile404(Client)
    Server.close()


def MoveInfo(Server, Client):
    header = """HTTP/1.1 301 Moved Permanently
Location: http://127.0.0.1:8082/info.html

"""
    print("HTTP respone: ")
    print(header)
    Client.send(bytes(header, "utf-8"))
    Server.close()


def SendFileInfo(Client):
    f = open("info.html", "rb")
    L = f.read()
    header = """HTTP/1.1 200 OK
Content-Type: text/html; charset=UTF-8
Content-Encoding: UTF-8
Content-Length: %d

""" % len(L)
    print("-----------------HTTP respone  Info.html: ")
    print(header)
    header += L.decode()
    Client.send(bytes(header, 'utf-8'))


def SendImg(Client, NameImg):
    with open(NameImg, 'rb') as f:
        L = f.read()
        header = """HTTP/1.1 200 OK
Content-Type: text/html; charset=UTF-8
Content-Encoding: UTF-8
Content-Length: %d

""" % len(L)
        print("-----------------HTTP respone: ")
        print(header)
        header = bytes(header, 'utf-8') + L
        Client.send(header)


def SendInfo(Server, Client):
    Server = CreateServer("localhost", 8082)
    Client, Request = ReadHTTPRequest(Server)
    print("HTTP Request: ")
    print(Request)
    if "GET /info.html HTTP/1.1" in Request:
        SendFileInfo(Client)
    Server.close()
    # image 1
    Server = CreateServer("localhost", 8082)
    Client, Request = ReadHTTPRequest(Server)
    print("HTTP Request: ")
    print(Request)
    if "GET /image1.jpg HTTP/1.1" in Request:
        SendImg(Client, "pic_2.jpg")
    if "GET /image2.jpg HTTP/1.1" in Request:
        SendImg(Client, "pic_4.jpg")

    Client, Request = ReadHTTPRequest(Server)
    print("HTTP Request: ")
    print(Request)
    if "GET /image1.jpg HTTP/1.1" in Request:
        SendImg(Client, "pic_2.jpg")
    if "GET /image2.jpg HTTP/1.1" in Request:
        SendImg(Client, "pic_4.jpg")
    Server.close()
    # image 2


if __name__ == "__main__":
    while True:
        print("Phan 1: tra ve trang chu khi truy cap Server")
        # 1. Create Server Socket
        Server = CreateServer("localhost", 8080)
        # 2. Client connect Server + 3. Read HTTP Request
        Client, Request = ReadHTTPRequest(Server)
        print("----------------HTTP requset: ")
        print(Request)
        # 4. Send HTTP Response  + 5. Close Server
        MoveHomePage(Server, Client, Request)
        # Phần 2 xử lý post user name va pass lên Server
        # 1. Create Server Socket
        Server = CreateServer("localhost", 10000)
        # 2. Client connect Server + 3. Read HTTP Request
        Client, Request = ReadHTTPRequest(Server)
        print("----------------HTTP requset: ")
        print(Request)
        if CheckPass(Request) == True:
            MoveInfo(Server, Client)
            SendInfo(Server, Client)
        else:
            Move404(Server, Client)
            Send404(Server, Client)
