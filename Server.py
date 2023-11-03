import socket
import threading
import http.client
from urllib.parse import urlparse
import tkinter as tk
from tkinter import Text, Scrollbar

# Proxy server configuration
SERVER_HOST = '192.168.123.11' #this is the ip address of my laptop
SERVER_PORT = 8888             #anyone who is connected with the same network can connect to the server

class ServerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Proxy Server")

        self.text_area = Text(root, wrap=tk.WORD)
        self.text_area.pack(expand="true", fill="both")

        self.scroll = Scrollbar(root, command=self.text_area.yview)
        self.scroll.pack(side="right", fill="y")
        self.text_area.config(yscrollcommand=self.scroll.set)

        self.connected_clients = {}

        self.server_thread = threading.Thread(target=self.start_server)
        self.server_thread.start()

    def proxy_server(self, client_socket, client_id):
        try:
            request = client_socket.recv(4096).decode('utf-8')

            if not request:
                print(f"Empty request received from {self.connected_clients[client_id][1][0]}:{self.connected_clients[client_id][1][1]}")
                return

            parts = request.split(' ')
            if len(parts) < 2:
                print(f"Invalid request format from {self.connected_clients[client_id][1][0]}:{self.connected_clients[client_id][1][1]}")
                return

            url = parts[1]
            target_url = urlparse(url)

            target_conn = http.client.HTTPSConnection(target_url.netloc)

            try:
                target_conn.request("GET", target_url.path)
                response = target_conn.getresponse()
                page_content = response.read()
            except Exception as e:
                print(f"Failed to fetch the URL: {e}")
                return

            client_socket.send(b"HTTP/1.1 200 OK\r\n\r\n")
            client_socket.send(page_content)
        except Exception as e:
            print(f"An error occurred while processing the request: {e}")
        finally:
            client_socket.close()
            del self.connected_clients[client_id]
            self.display_connected_clients()

    def start_server(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((SERVER_HOST, SERVER_PORT))
        server.listen(5)
        self.text_area.insert("1.0", f"Proxy server is listening on {SERVER_HOST}:{SERVER_PORT}\n")

        while True:
            client_socket, addr = server.accept()
            self.text_area.insert("1.0", f"Accepted connection from {addr[0]}:{addr[1]}\n")

            client_id = len(self.connected_clients) + 1
            self.connected_clients[client_id] = (client_socket, addr)
            self.display_connected_clients()

            client_handler = threading.Thread(target=self.proxy_server, args=(client_socket, client_id))
            client_handler.start()

    def display_connected_clients(self):
        clients_text = "\nConnected Clients:\n"
        for client_id, (client_socket, client_addr) in self.connected_clients.items():
            clients_text += f"{client_addr[0]}:{client_addr[1]}\n"
        self.text_area.delete("2.0", "end")
        self.text_area.insert("2.0", clients_text)

def main():
    root = tk.Tk()
    app = ServerApp(root)
    root.mainloop()

if __name__ == '__main__':
    main()
