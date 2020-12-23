import socket
from config import SERVER_PORT, CLIENT_PORT


def convertPort(ip, port):
    portFinal = ""
    pUpper = int(int(port) / 256)
    pLower = int(int(port) % 256)
    ipArray = ip.split(".")
    for n in ipArray:
        portFinal = portFinal + n + ","
    portFinal = portFinal + str(pUpper) + ","
    portFinal = portFinal + str(pLower)
    return portFinal


CLIENT_TESTS = [
    {
        "name": "test1",
        "description": "Connects client to the server (upper case)",
        "input": """CONNECT 127.0.0.1 {!SERVER_PORT}
QUIT
""".replace(
            "{!SERVER_PORT}", str(SERVER_PORT)
        ),
        "output": """CONNECT 127.0.0.1 {!SERVER_PORT}
CONNECT accepted for FTP server at host 127.0.0.1 and port {!SERVER_PORT}
FTP reply 220 accepted. Text is: COMP 431 FTP server ready.
USER anonymous
FTP reply 331 accepted. Text is: Guest access OK, send password.
PASS guest@
FTP reply 230 accepted. Text is: Guest login OK.
SYST
FTP reply 215 accepted. Text is: UNIX Type: L8.
TYPE I
FTP reply 200 accepted. Text is: Type set to I.
QUIT
QUIT accepted, terminating FTP client
QUIT
FTP reply 221 accepted. Text is: Goodbye.
""".replace(
            "{!SERVER_PORT}", str(SERVER_PORT)
        ),
    },
    {
        "name": "test2",
        "description": "Connects client to the server (lower case)",
        "input": """connect 127.0.0.1 {!SERVER_PORT}
QUIT
""".replace(
            "{!SERVER_PORT}", str(SERVER_PORT)
        ),
        "output": """connect 127.0.0.1 {!SERVER_PORT}
CONNECT accepted for FTP server at host 127.0.0.1 and port {!SERVER_PORT}
FTP reply 220 accepted. Text is: COMP 431 FTP server ready.
USER anonymous
FTP reply 331 accepted. Text is: Guest access OK, send password.
PASS guest@
FTP reply 230 accepted. Text is: Guest login OK.
SYST
FTP reply 215 accepted. Text is: UNIX Type: L8.
TYPE I
FTP reply 200 accepted. Text is: Type set to I.
QUIT
QUIT accepted, terminating FTP client
QUIT
FTP reply 221 accepted. Text is: Goodbye.
""".replace(
            "{!SERVER_PORT}", str(SERVER_PORT)
        ),
    },
    {
        "name": "test3",
        "description": "Connects client to the server (mixed case)",
        "input": """CoNnEcT 127.0.0.1 {!SERVER_PORT}
QUIT
""".replace(
            "{!SERVER_PORT}", str(SERVER_PORT)
        ),
        "output": """CoNnEcT 127.0.0.1 {!SERVER_PORT}
CONNECT accepted for FTP server at host 127.0.0.1 and port {!SERVER_PORT}
FTP reply 220 accepted. Text is: COMP 431 FTP server ready.
USER anonymous
FTP reply 331 accepted. Text is: Guest access OK, send password.
PASS guest@
FTP reply 230 accepted. Text is: Guest login OK.
SYST
FTP reply 215 accepted. Text is: UNIX Type: L8.
TYPE I
FTP reply 200 accepted. Text is: Type set to I.
QUIT
QUIT accepted, terminating FTP client
QUIT
FTP reply 221 accepted. Text is: Goodbye.
""".replace(
            "{!SERVER_PORT}", str(SERVER_PORT)
        ),
    },
    {
        "name": "test4",
        "description": "Rejects bad connect command",
        "input": """cnct 127.0.0.1 {!SERVER_PORT}
QUIT
""".replace(
            "{!SERVER_PORT}", str(SERVER_PORT)
        ),
        "output": """cnct 127.0.0.1 {!SERVER_PORT}
ERROR -- request
QUIT
ERROR -- expecting CONNECT
""".replace(
            "{!SERVER_PORT}", str(SERVER_PORT)
        ),
    },
    {
        "name": "test5",
        "description": "Handles connection to invalid host",
        "input": """CONNECT 10.9.0.2 {!SERVER_PORT}
QUIT
""".replace(
            "{!SERVER_PORT}", str(SERVER_PORT)
        ),
        "output": """CONNECT 10.9.0.2 {!SERVER_PORT}
CONNECT accepted for FTP server at host 10.9.0.2 and port {!SERVER_PORT}
CONNECT failed
QUIT
ERROR -- expecting CONNECT
""".replace(
            "{!SERVER_PORT}", str(SERVER_PORT)
        ),
    },
    {
        "name": "test6",
        "description": "Handles connection to invalid port",
        "input": """CONNECT 127.0.0.1 7000
QUIT
""".replace(
            "{!SERVER_PORT}", str(SERVER_PORT)
        ),
        "output": """CONNECT 127.0.0.1 7000
CONNECT accepted for FTP server at host 127.0.0.1 and port 7000
CONNECT failed
QUIT
ERROR -- expecting CONNECT
""".replace(
            "{!SERVER_PORT}", str(SERVER_PORT)
        ),
    },
    {
        "name": "test7",
        "description": "Sends a GET request (invalid file)",
        "input": """CONNECT 127.0.0.1 {!SERVER_PORT}
GET invalidfile.txt
QUIT
""".replace(
            "{!SERVER_PORT}", str(SERVER_PORT)
        ),
        "output": """CONNECT 127.0.0.1 {!SERVER_PORT}
CONNECT accepted for FTP server at host 127.0.0.1 and port {!SERVER_PORT}
FTP reply 220 accepted. Text is: COMP 431 FTP server ready.
USER anonymous
FTP reply 331 accepted. Text is: Guest access OK, send password.
PASS guest@
FTP reply 230 accepted. Text is: Guest login OK.
SYST
FTP reply 215 accepted. Text is: UNIX Type: L8.
TYPE I
FTP reply 200 accepted. Text is: Type set to I.
GET invalidfile.txt
GET accepted for invalidfile.txt
PORT {!CLIENT_IP}
FTP reply 200 accepted. Text is: Port command successful (192.168.99.1,8000).
RETR invalidfile.txt
FTP reply 550 accepted. Text is: File not found or access denied.
QUIT
QUIT accepted, terminating FTP client
QUIT
FTP reply 221 accepted. Text is: Goodbye.
""".replace(
            "{!SERVER_PORT}", str(SERVER_PORT)
        ).replace(
            "{!CLIENT_IP}",
            convertPort(socket.gethostbyname(socket.gethostname()), SERVER_PORT),
        ),
    },
]
