import sys
import re
import socket
import os
import shutil
from utils import (
    COMMANDS,
    validateCommand,
    validateHost,
    validatePort,
    validateString,
    convertPort,
    bytes2number,
    validateResponseCode,
)


# Global Variables
CLIENT_SOCKET = None
IS_CONNECTED = False
HOST = ""
PORT = 8000
FILE_NUMBER = 0


# Parses the command
def parseCommand(values):
    """Parses the values for the command and any parameters

    Args:
        values (string): string input from the command line

    Returns:
        boolean: boolean signifying the success of the command
    """
    global IS_CONNECTED
    global CLIENT_SOCKET
    global HOST
    global PORT
    global FILE_NUMBER

    cmd = values[0]
    params = []
    for p in values[1:]:
        params.append(p)

    # Test if the command is valid
    if not validateCommand(cmd):
        print("ERROR -- request")
        return False

    # Test for valid parameters
    if cmd.upper() == "CONNECT":

        # Check that the server host is valid
        if not validateHost(params[0]) or params[0] == "localhost":
            print("ERROR -- server-host")
            return False

        # Check that the port is valid
        if not validatePort(params[1]):
            print("ERROR -- server-port")
            return False

    elif cmd.upper() == "GET":

        # Check that there is valid pathname
        if not validateString(params[0]):
            print("ERROR -- pathname")
            return False

    # QUIT Command
    else:

        # Make sure there are no parameters
        if len(params) > 0:
            print("ERROR -- request")
            return False

    # Test if the user is connected before other commands
    if not IS_CONNECTED and not cmd.upper() == "CONNECT":
        print("ERROR -- expecting CONNECT")
        return False

    # Handle the requests
    if cmd.upper() == "CONNECT":

        # Attempt to open FTP connection
        HOST = params[0]
        PORT = int(params[1])

        try:
            if CLIENT_SOCKET != None:
                CLIENT_SOCKET.send("QUIT\r\n".encode())
                CLIENT_SOCKET.close()
            print("CONNECT accepted for FTP server at host", HOST, "and port", PORT)
            openFTPConnection(HOST, PORT + 9633)
        except Exception as e:
            return False

    elif cmd.upper() == "GET":

        hostip = socket.gethostbyname(socket.gethostname())
        convertedPortNum = convertPort(hostip, PORT)
        print("GET accepted for " + params[0])

        try:
            dataSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            dataSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            dataSocket.bind((hostip, PORT))
            dataSocket.listen(1)

            sys.stdout.write("PORT " + convertedPortNum + "\r\n")
            CLIENT_SOCKET.send(("PORT " + convertedPortNum + "\r\n").encode())
            parseFTPResponse(CLIENT_SOCKET.recv(1024).decode())

            (dataConnection, _addr) = dataSocket.accept()

            sys.stdout.write("RETR " + params[0] + "\r\n")
            CLIENT_SOCKET.send(("RETR " + params[0] + "\r\n").encode())
            info = ""
            info = parseFTPResponse(CLIENT_SOCKET.recv(1024).decode())

            # If file does not exist
            if (
                info
                == "FTP reply 550 accepted. Text is: File not found or access denied."
            ):
                return False

            # Testing data connection on server side
            fileSize = dataConnection.recv(4)
            fileSize = bytes2number(fileSize)

            # Write File
            fileDirectory = os.path.join(os.path.dirname(__file__), "retr_file")
            if not os.path.exists(fileDirectory):
                os.makedirs(fileDirectory)

            fp = open(os.path.join(fileDirectory, "file" + str(FILE_NUMBER)), "wb")
            currentSize = 0
            while currentSize < int(fileSize):
                data = dataConnection.recv(1024)
                if not data:
                    break

                if len(data) + currentSize > fileSize:
                    data = data[: fileSize - currentSize]  # trim additional data

                fp.write(data)
                currentSize += len(data)
            fp.close()

            dataSocket.close()

        except:
            sys.stdout.write("GET failed, FTP-data port not allocated.\r\n")
            pass

        parseFTPResponse(CLIENT_SOCKET.recv(1024).decode())
        PORT = int(PORT) + 1
        FILE_NUMBER += 1

    # QUIT Command
    else:
        IS_CONNECTED = False
        HOST = None
        PORT = 8000

        try:
            print("QUIT accepted, terminating FTP client")
            sys.stdout.write("QUIT\r\n")
            CLIENT_SOCKET.send("QUIT\r\n".encode())
            parseFTPResponse(CLIENT_SOCKET.recv(1024).decode())
            CLIENT_SOCKET.close()
            CLIENT_SOCKET = None
            return True
        except Exception as e:
            return False


# Response parsing
def parseResponse(values, hasCRLF):
    """Parse a response from the server.

    Args:
        values (string): a string command from the server
        hasCRLF (bool): whether or not the command has a valid CRLF

    Returns:
        string: response from server formatted
    """
    code = values[0]
    text = " ".join(values[1:])

    # Check if the code is correct
    if not validateResponseCode(code):
        print("ERROR -- reply-code")
        return ""

    # Check if the text is a string
    if not validateString(text):
        print("ERROR -- reply-text")
        return ""

    # Checks for CRLF
    if not hasCRLF:
        print("ERROR -- <CRLF>")
        return ""

    # Create response string
    responseStringFinal = ""
    responseStringFinal = "FTP reply " + values[0] + " accepted. "
    responseStringFinal = responseStringFinal + "Text is: " + text
    return responseStringFinal


def openFTPConnection(serverName, serverPort):
    """Opens a socket connection with the server.

    Args:
        serverName (string): domain or IP of the server
        serverPort (number): port number of the server
    """
    global CLIENT_SOCKET
    global IS_CONNECTED
    global HOST
    global PORT

    try:
        CLIENT_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        CLIENT_SOCKET.settimeout(10)
        CLIENT_SOCKET.connect((serverName, serverPort))
        IS_CONNECTED = True

        # Receives Initial Connection Message
        parseFTPResponse(CLIENT_SOCKET.recv(1024).decode())

        # Send sequence
        sys.stdout.write("USER anonymous\r\n")
        CLIENT_SOCKET.send("USER anonymous\r\n".encode())
        parseFTPResponse(CLIENT_SOCKET.recv(1024).decode())

        sys.stdout.write("PASS guest@\r\n")
        CLIENT_SOCKET.send("PASS guest@\r\n".encode())
        parseFTPResponse(CLIENT_SOCKET.recv(1024).decode())

        sys.stdout.write("SYST\r\n")
        CLIENT_SOCKET.send("SYST\r\n".encode())
        parseFTPResponse(CLIENT_SOCKET.recv(1024).decode())

        sys.stdout.write("TYPE I\r\n")
        CLIENT_SOCKET.send("TYPE I\r\n".encode())
        parseFTPResponse(CLIENT_SOCKET.recv(1024).decode())

    except Exception as e:
        IS_CONNECTED = False
        HOST = None
        PORT = 8000
        CLIENT_SOCKET = None
        print("CONNECT failed")

    return


# Sends data over FTP connection
def parseFTPResponse(dataRcv):
    """Parse a response from the server.

    Args:
        dataRcv (string): response from the server

    Returns:
        string: formatted message from the server
    """
    # Splits input and tests for CRLF
    values = dataRcv.split()
    regexCRLF = re.compile("\r\n")
    hasCRLF = bool(regexCRLF.search(dataRcv))
    rcvMsg = parseResponse(values, hasCRLF)
    print(rcvMsg)
    return rcvMsg


def main():
    """Creates a client that listens for user input"""

    global PORT
    PORT = int(sys.argv[1])

    # Clean out the retr_files directory
    try:
        retrFiles = os.path.join(os.path.dirname(__file__), "retr_file")
        if os.path.exists(retrFiles):
            shutil.rmtree(retrFiles)
    except Exception as e:
        pass

    for i in sys.stdin:

        # Reprints the line to the output
        sys.stdout.write(i)

        # Splits the input on whitespace
        values = i.split()

        # If parse command returns true that means a valid quit command was parsed
        # Program should terminate
        if parseCommand(values):
            break
    return
