#! /usr/bin/python3

import http.server, ssl, sys, random, string, argparse, socket

hostname = "[domain]"
redirect_enabled = False
redirect_target = ""
redirect_token = ""
manual_redirect_token = False
redirect_code = 303
verbose = False

parser = argparse.ArgumentParser()
parser.add_argument("--redirect", type=str)
parser.add_argument("--redirect_code", type=int)
parser.add_argument("--redirect_token", type=str)
parser.add_argument("--verbose", action="store_true")
args = parser.parse_args()

url = "https://" + hostname + "/"

if args.redirect is not None:
    print("[redirect] Redirecting enabled. Target: '" + args.redirect + "'")
    redirect_enabled = True
    redirect_target = args.redirect

if args.redirect_code is not None:
    if not redirect_enabled:
        print("[!] Redirecting is disabled. Can't set 'redirect_code'.")
        exit()
    print("[redirect] Setting custom redirect response code to '" + str(args.redirect_code) + "'.")
    redirect_code = args.redirect_code

if args.redirect_token is not None:
    if not redirect_enabled:
        print("[!] Redirecting is disabled. Can't set 'redirect_token'.")
        exit()
    print("[redirect] Manually setting redirect token to '" + str(args.redirect_token) + "'. Redirect URL: " + url + args.redirect_token)
    redirect_token = args.redirect_token
    manual_redirect_token = True

if args.verbose is not False:
    print("[verbose] Verbose mode enabled.")
    verbose = True

if redirect_enabled and not manual_redirect_token:
    redirect_token = "".join(random.SystemRandom().choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(30))
    print("[redirect] Random redirect URL: " + url + redirect_token)

class CustomServer(http.server.SimpleHTTPRequestHandler):
    def do_request(self, method):
        if verbose:
            print("\n\n[verbose]")
            print(self.client_address)
            try:
                print(socket.gethostbyaddr(self.client_address[0])[0])
            except:
                print("[!] Reverse DNS failed.")
            print()
            print(self.headers)
        if redirect_enabled and self.path == "/" + redirect_token:
            print("[redirect] Redirect path hit! Returning " + str(redirect_code) + " to '" + redirect_target + "'.")
            self.send_response(redirect_code)
            self.send_header("Location", redirect_target)
            self.end_headers()
        else:
            if method == "GET":
                super().do_GET()
            else:
                print("[!] Cant handle request method '" + method + "'...")
                self.send_response(501)
                self.end_headers()

    def do_GET(self):
        self.do_request("GET")
    
    def do_POST(self):
        self.do_request("POST")

server_address = ("0.0.0.0", 443)
httpd = http.server.HTTPServer(server_address, CustomServer)

httpd.socket = ssl.wrap_socket(httpd.socket,
                               server_side=True,
                               keyfile="/etc/letsencrypt/live/" + hostname + "/privkey.pem",
                               certfile="/etc/letsencrypt/live/" + hostname + "/fullchain.pem",
                               ssl_version=ssl.PROTOCOL_TLSv1_2)

print("[+] Starting server. URL: " + url)
httpd.serve_forever()