import re

COMMANDS = ["CONNECT", "GET", "QUIT"]


def bytes2number(b):
    """converts byte form to an integer

    Args:
        b (number): a byte array

    Returns:
        number: an integer number
    """
    res = 0
    for i in range(4):
        res += b[i] << (i * 8)
    return res


def validateString(s):
    """Validates a string to ensure that it contains valid characters

    Args:
        s (string): any string

    Returns:
        boolean: value confirming the validity of the string
    """
    # validString = re.compile('^[a-zA-Z]+$')
    # return validString.match(s)
    for char in s:
        if ord(char) > 127 or ord(char) < 0:
            return False
    return True


def validatePort(p):
    """Validates a port number

    Args:
        p (number): a port number
    Returns:
        boolean: boolean confirming validity of the port
    """
    try:
        pNum = int(p)
    except ValueError:
        return False

    # Check if it is not a valid port number (0-65535)
    if pNum < 0 or pNum > 65535:
        return False

    # Check if the lengths are the same (Making sure there is no leading 0)
    if not len(p) == len(str(pNum)):
        return False

    return True


def validateHost(host):
    """Validates that a given host is valid

    Args:
        d (string): a host name

    Returns:
        boolean: boolean confirming the validity of the host
    """
    # RE For valid alphabetic/numeric
    # Checks alphanumeric. zero or more times and that string ends in alphanumeric
    # Also an element must begin with a character
    validDomainRE = re.compile(
        "^(([a-zA-Z][a-zA-Z0-9]+).)*(?=[^.])[a-zA-Z][a-zA-Z0-9]+$"
    )
    return (not not validDomainRE.fullmatch(host)) or validateIP(host)


def validateIP(ip):
    """Validates an IP address.

    Args:
        ip (string): an IP address

    Returns:
        boolean: boolean signifying a valid IP address
    """
    ipArr = ip.split(".")
    if len(ipArr) != 4:
        return False
    validIP = True
    for i in ipArr:
        try:
            if int(i) > 255 or int(i) < 0:
                validIP = False
        except Exception:
            validIP = False
    return validIP


# Validates the command
def validateCommand(cmd):
    """Validates a command.

    Args:
        cmd (string): a command to validate

    Returns:
        boolean: boolean signifying a valid command
    """
    return len(cmd) != 0 and cmd.upper() in COMMANDS


def validateResponseCode(c):
    """Validates a respose code.

    Args:
        c (string): string representation of a response code

    Returns:
        boolean: boolean signifying the validity of a response code
    """

    try:
        cNum = int(c)
    except ValueError:
        return False

    # Check if the lengths are the same (Making sure there is no leading 0)
    if not len(c) == len(str(cNum)):
        return False

    # Check if the code is between 100 and 599
    if cNum < 100 or cNum > 599:
        return False

    return True


# Converts the port and IP to be comma separated
def convertPort(ip, port):
    """Converts an IP address and a port into format (IP,PORT)

    Args:
        ip (string): IP address
        port (string): port number

    Returns:
        string: IP and port in the format (IP,PORT)
    """
    portFinal = ""

    # Convert port to the two 16 bit values
    pUpper = int(int(port) / 256)
    pLower = int(int(port) % 256)

    # Split the IP by periods
    ipArray = ip.split(".")
    for n in ipArray:
        portFinal = portFinal + n + ","
    portFinal = portFinal + str(pUpper) + ","
    portFinal = portFinal + str(pLower)
    return portFinal