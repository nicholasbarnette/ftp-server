# File Transfer Protocol Client/Server

## Client

To start an instance of the FTP client you will want to use the follwing command. The specified port can be mapped to any valid/unused port.

```sh
python ./client/index.py 8080
```

The supported commands are defined below.

```sh
# Connects to an FTP server
CONNECT <server-host> <server-port>

# Gets a file from the connected server
GET <file-name>

# Closes the client connection to the server
QUIT
```

## Server

To start an instance of the FTP server you will want to use the follwing command. The specified port can be mapped to any valid/unused port.

```sh
python ./server/index.py 9000
```

The supported commands are defined below.

```sh
# User identifier (any user is valid right now)
USER <user>

# User password (any password is valid right now)
PASS <password>

# Informs the server of the type of data being transferred (only supports type I right now)
# A -- ASCII data
# I -- image/binary data
TYPE (A | I)

# Returns information about the server
SYST

# Sends a command that has no impact on the state of the client or server
NOOP

# Registers that the client is disconnecting from the connection
QUIT

# Create a data socket to send information to the FTP server.
# IP format is defined as xxx,xxx,xxx,xxx,xxx where the first three sections consist of the IP address.
# The last two sections consist of the port. For example, to connect to `127.0.0.1:8001` the command
# would be `PORT 127,0,0,1,31,65`.
PORT <ip>

# Upon a successfuly `PORT` command, send a request for a specific file to download locally to the
# client.
RETR <file>
```
