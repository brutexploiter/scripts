import socket

hostname = "example.com"
port = 80

request = (
    "GET /pentesterlab HTTP/1.1\r\n"
    f"Host: {hostname}\r\n"
    "Content-Type: application/x-www-form-urlencoded\r\n"
    "Connection: close\r\n"
    "X-Forwarded-For: 1.2.3.4\r\n"
    "Content-Length: 10\r\n"
    "User-Agent: curl/8.10.1\r\n"
    "Accept: */*\r\n"
    "\r\n"
    ""
)

print("Request:\n")
print(request)

# Send the request to the server
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((hostname, port))
    
    # Send the request
    s.sendall(request.encode("utf-8"))

    response = b""
    while True:
        data = s.recv(4096)  # Read in chunks of 4096 bytes
        if not data:
            break
        response += data

print("\nResponse:\n")
print(response.decode("utf-8", errors="replace"))
