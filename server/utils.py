COMMANDS = ["USER", "PASS", "TYPE", "SYST", "NOOP", "QUIT", "PORT", "RETR"]


# Test if the command is valid
def validateCommand(cmd):
    """Validates a command

    Args:
        cmd (string): any command as a string

    Returns:
        string: an error message if the command is invalid
    """
    if not (len(cmd) != 0 and cmd.upper() in COMMANDS):
        # Command is 3-4 characters long
        if len(cmd) == 3 or len(cmd) == 4:
            return "502 Command not implemented.\r\n"
        return "500 Syntax error, command unrecognized.\r\n"
    return ""


def validateType(param):
    """Validates a type-code parameter

    Args:
        param (string): type-code paramerter that needs validation

    Returns:
        boolean: whether or not the type-code parameter is valid
    """
    return param.upper() in ["A", "I"]


def validateStringParameter(param):
    """Validates a string parameter to ensure it is valid. Primarily used for `USER` and `PASS` commands.

    Args:
        param (string): any string parameter

    Returns:
        boolean: whether or not the string parameter is valid
    """
    return isinstance(param, str) and len(param) != 0


def validateStringCharacters(param):
    """Validates that all characters in a string parameter are valid ASCII charaters (excluding '*').

    Args:
        param (string): any string parameter

    Returns:
        boolean: whether or not the string contains valid ASCII characters
    """
    for char in param:
        if ord(char) > 127 or ord(char) < 0 or char == "*":
            return False
    return True


def validatePort(param):
    """Validates that the port follows the proper format (xxx,xxx,xxx,xxx,xxx,xxx).

    Args:
        param (string): a port to validate

    Returns:
        boolean: whether or not the port is valid
    """

    # Splits the port sections
    portArray = param.split(",")

    # Check if there are the correct
    if not (len(portArray) == 6):
        return False

    goodPort = True
    # Check if the port number is valid
    for pNum in portArray:
        if len(pNum) == 0 or int(pNum) >= 256 or int(pNum) < 0:
            goodPort = False

    return goodPort


def convert2bytes(no):
    """Converts a number to its byte format

    Args:
        no ([type]): [description]

    Returns:
        [bytearray]: [description]
    """
    result = bytearray()
    result.append(no & 255)
    for _i in range(3):
        no = no >> 8
        result.append(no & 255)
    return result
