import sys
import re
import socket
import os
from utils import (
    validateStringCharacters,
    validateStringParameter,
    validateType,
    validatePort,
    validateCommand,
    convert2bytes,
)

# Global Variables
SERVER_SOCKET = None
SERVER_CONNECTION = None
DATA_SOCKET = None
DATA_CONNECTION = None
PORT_START = 9000
PORT_SERVER = 9000
USER = ""
PASSWORD = ""
FILE_NAME_NUMBER = 0
PORT = ""
IP = ""
DID_QUIT = False


def handleUSER(param):
    """Handles a `USER` command.

    Args:
        param (string): the parameter passed with the `USER` command

    Returns:
        string: response message
    """
    global USER
    global PASSWORD
    global PORT
    global IP

    # No parameter
    if len(param) == 0:
        sys.stdout.write("500 Syntax error, command unrecognized.\r\n")
        return "500 Syntax error, command unrecognized.\r\n"

    # Check if one of valid ASCII characters (not CR or LF)
    # Parameter must be a string
    if not (validateStringCharacters(param) and validateStringParameter(param)):
        sys.stdout.write("501 Syntax error in parameter.\r\n")
        return "501 Syntax error in parameter.\r\n"

    # Set/Reset Values
    USER = param
    PASSWORD = ""
    PORT = ""
    IP = ""

    sys.stdout.write("331 Guest access OK, send password.\r\n")
    return "331 Guest access OK, send password.\r\n"


def handlePASS(param):
    """Handles a `PASS` command.

    Args:
        param (string): the parameter passed with the `PASS` command

    Returns:
        string: response message
    """
    global PASSWORD

    # No parameter
    if len(param) == 0:
        sys.stdout.write("501 Syntax error in parameter.\r\n")
        return "501 Syntax error in parameter.\r\n"

    # Check if one of valid ASCII characters (not CR or LF)
    # Parameter must be a string
    if not (validateStringCharacters(param) and validateStringParameter(param)):
        sys.stdout.write("501 Syntax error in parameter.\r\n")
        return "501 Syntax error in parameter.\r\n"

    PASSWORD = param
    sys.stdout.write("230 Guest login OK.\r\n")
    return "230 Guest login OK.\r\n"


def handleTYPE(param):
    """Handles a `TYPE` command.

    Args:
        param (string): the parameter passed with the `TYPE` command

    Returns:
        string: response message
    """
    if not validateType(param):
        sys.stdout.write("501 Syntax error in parameter.\r\n")
        return "501 Syntax error in parameter.\r\n"
    else:
        sys.stdout.write("200 Type set to " + param.upper() + ".\r\n")
        return "200 Type set to " + param.upper() + ".\r\n"


def handlePORT(param):
    """Handles a `PORT` command.

    Args:
        param (string): the parameter passed with the `PORT` command

    Returns:
        string: response message
    """
    global PORT
    global IP
    global DATA_SOCKET

    # Validate port number
    if not validatePort(param):
        sys.stdout.write("501 Syntax error in parameter.\r\n")
        return "501 Syntax error in parameter.\r\n"
    else:
        portArray = param.split(",")
        pArrayLen = len(portArray) - 1

        # Gets the port
        port = (int(portArray[pArrayLen - 1]) * 256) + int(portArray[pArrayLen])

        # Gets the IP
        IP = ""
        for i in range(0, 4):
            IP += str(portArray[i]) + "."
        IP = IP[0 : len(IP) - 1]

        PORT = param

        try:
            DATA_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            DATA_SOCKET.connect((IP, port))
        except Exception:
            sys.stdout.write("425 Can not open data connection.\r\n")
            return "425 Can not open data connection.\r\n"

        sys.stdout.write(
            "200 Port command successful (" + IP + "," + str(port) + ").\r\n"
        )
        return "200 Port command successful (" + IP + "," + str(port) + ").\r\n"


def handleRETR(param):
    """Handles a `RETR` command.

    Args:
        param (string): the parameter passed with the `RETR` command

    Returns:
        string: response message
    """
    global FILE_NAME_NUMBER
    global DATA_SOCKET
    global PORT

    # Test if pathname is a string
    if not validateStringParameter(param):
        DATA_SOCKET.close()
        sys.stdout.write("550 File not found or access denied.\r\n")
        return "550 File not found or access denied.\r\n"

    # Check if string begins with '/' or '\'
    if param[0] == "\\" or param[0] == "/":
        filename = param[1:]
    else:
        filename = param

    # Process file copy
    try:
        # Send file size
        if os.path.exists(filename):
            length = os.path.getsize(filename)
            DATA_SOCKET.send(convert2bytes(length))
        else:
            DATA_SOCKET.close()
            sys.stdout.write("550 File not found or access denied.\r\n")
            return "550 File not found or access denied.\r\n"

        # Send file
        with open(filename, "rb") as fs:
            sys.stdout.write("150 File status okay.\r\n")
            SERVER_CONNECTION.send("150 File status okay.\r\n".encode())

            # Send the file encoded as bytes
            while True:
                data = fs.read(1024)
                if not data:
                    break
                DATA_SOCKET.send(data)
            fs.close()
    except Exception:
        sys.stdout.write("425 Can not open data connection.\r\n")
        return "425 Can not open data connection.\r\n"

    FILE_NAME_NUMBER += 1
    PORT = ""

    # Close connection
    DATA_SOCKET.close()

    sys.stdout.write("226 Transfer Complete.\r\n")
    return "226 Transfer Complete.\r\n"


def handleSYST(param):
    """Handles a `SYST` command.

    Args:
        param (string): the parameter passed with the `SYST` command

    Returns:
        string: response message
    """
    # Make sure there is no parameter
    if len(param) > 0:
        sys.stdout.write("501 Syntax error in parameter.\r\n")
        return "501 Syntax error in parameter.\r\n"
    else:
        sys.stdout.write("215 UNIX Type: L8.\r\n")
        return "215 UNIX Type: L8.\r\n"


def handleQUIT(param):
    """Handles a `QUIT` command.

    Args:
        param (string): the parameter passed with the `QUIT` command

    Returns:
        string: response message
    """
    global DID_QUIT

    # Make sure there is no parameter
    if len(param) > 0:
        sys.stdout.write("501 Syntax error in parameter.\r\n")
        return "501 Syntax error in parameter.\r\n"
    else:
        sys.stdout.write("221 Goodbye.\r\n")
        DID_QUIT = True
        return "221 Goodbye.\r\n"


def handleNOOP(param):
    """Handles a `NOOP` command.

    Args:
        param (string): the parameter passed with the `NOOP` command

    Returns:
        string: response message
    """
    # Make sure there is no parameter
    if len(param) > 0:
        sys.stdout.write("501 Syntax error in parameter.\r\n")
        return "501 Syntax error in parameter.\r\n"
    else:
        sys.stdout.write("200 Command OK.\r\n")
        return "200 Command OK.\r\n"


# TODO: Test this via bash commands
def checkSequence(cmd):
    """Ensure commands are passed in a valid sequence

    Args:
        cmd (string): command passed in

    Returns:
        (boolean, string): a tuple consisting of a boolean signifying the presence of
            an error and the error message
    """

    # Quit command always valid
    if cmd.upper() == "QUIT":
        return (True, "")

    # User not set and command is not user or quit
    if len(USER) == 0 and not (cmd.upper() == "USER"):
        return (False, "530 Not logged in.\r\n")
    elif cmd.upper() == "USER":
        return (True, "")

    # Password not set and command is not pass or quit
    if len(PASSWORD) == 0 and not (cmd == "pass"):
        sys.stdout.write("530 Not logged in.\r\n")
        return (False, "530 Not logged in.\r\n")
    elif len(PASSWORD) == 0 and cmd == "pass":
        return (True, "")

    # Password is set and another password command passed in
    if not (len(PASSWORD) == 0) and cmd == "pass":
        sys.stdout.write("503 Bad sequence of commands.\r\n")
        return (False, "503 Bad sequence of commands.\r\n")

    # Port not set but retr command passed in
    if len(PORT) == 0 and cmd == "retr":
        sys.stdout.write("503 Bad sequence of commands.\r\n")
        return (False, "503 Bad sequence of commands.\r\n")

    return (True, "")


# TODO: Test this via bash commands
def parseInput(cmd, param, hasCRLF):
    """Analyzes the validity of the command and handles the output

    Args:
        cmd (string): command to validate and handle
        param (string): parameter related to the command
        hasCRLF (bool): whether or not the line contains a valid CRLF

    Returns:
        string: string message regarding commands success/failure
    """

    global SERVER_CONNECTION
    global DATA_SOCKET
    global DATA_CONNECTION

    # Test for CRLF
    if not hasCRLF:
        sys.stdout.write("ERROR -- CRLF\r\n")
        return "ERROR -- CRLF\r\n"

    # Test if the command is valid
    if validateCommand(cmd) != "":

        # Command is 3-4 characters long
        if len(cmd) == 3 or len(cmd) == 4:
            sys.stdout.write("502 Command not implemented.\r\n")
            return "502 Command not implemented.\r\n"

        sys.stdout.write("500 Syntax error, command unrecognized.\r\n")
        return "500 Syntax error, command unrecognized.\r\n"

    # Check sequence of commands
    (sequenceValid, sequenceMessage) = checkSequence(cmd.lower())
    if not sequenceValid:
        return sequenceMessage

    # Handle the valid commands
    if cmd.upper() == "USER":
        return handleUSER(param)
    elif cmd.upper() == "PASS":
        return handlePASS(param)
    elif cmd.upper() == "TYPE":
        return handleTYPE(param)
    elif cmd.upper() == "PORT":
        return handlePORT(param)
    elif cmd.upper() == "RETR":
        return handleRETR(param)
    elif cmd.upper() == "SYST":
        return handleSYST(param)
    elif cmd.upper() == "QUIT":
        return handleQUIT(param)
    else:
        return handleNOOP(param)


# TODO: Test this via bash commands
def main():
    """Creates a server socket and accepts connections from a client socket"""

    global SERVER_CONNECTION
    global SERVER_SOCKET
    global PORT_SERVER
    global USER
    global PASSWORD
    global PORT
    global FILE_NAME_NUMBER
    global DID_QUIT
    global PORT_START

    PORT_START = int(sys.argv[1])
    PORT_SERVER = PORT_START + 9633

    try:
        SERVER_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        SERVER_SOCKET.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        SERVER_SOCKET.bind(("", PORT_SERVER))
        SERVER_SOCKET.listen(5)
        sys.stdout.write(
            "Server listening on "
            + SERVER_SOCKET.getsockname()[0]
            + " "
            + str(SERVER_SOCKET.getsockname()[1])
            + "\r\n"
        )

        (connectionSocket, addr) = SERVER_SOCKET.accept()
        sys.stdout.write("220 COMP 431 FTP server ready.\r\n")
        connectionSocket.send(("220 COMP 431 FTP server ready.\r\n").encode())
        SERVER_CONNECTION = connectionSocket
        FILE_NAME_NUMBER = 0

        while True:

            # Gets message from server
            inputMsg = connectionSocket.recv(1024).decode()

            if DID_QUIT:
                break

            # Reprints the line to the output
            sys.stdout.write(inputMsg)

            # Test to make sure there is not space after the parameter
            regexCRLF = re.compile("\s\r\n")
            if bool(regexCRLF.search(inputMsg)):
                connectionSocket.send(("501 Syntax error in parameter.\r\n").encode())
                continue

            # Tests input for CRLF
            regexCRLF = re.compile("\r\n")
            hasCRLF = bool(regexCRLF.search(inputMsg))

            # Splits the input on whitespace
            values = inputMsg.split()

            if len(values) == 1:
                values.append("")

            # Add CRLF to the array
            values.append(hasCRLF)

            # Send back message
            if not (len(values) == 1):
                output = parseInput(values[0], values[1], values[2])
                connectionSocket.send(output.encode())

        # Close the connection
        SERVER_SOCKET.close()

        # Reset global variable states
        SERVER_SOCKET = None
        PORT_SERVER = PORT_START + 9633
        USER = ""
        PASSWORD = ""
        PORT = ""
        DID_QUIT = False

        # Call main again
        main()

    except Exception:
        raise