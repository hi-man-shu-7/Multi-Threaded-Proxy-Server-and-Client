import socket
import tkinter as tk
from tkinter import Entry, Button, Text, Scrollbar, filedialog

class ClientApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Proxy Client")

        self.ip_label = tk.Label(root, text="Server IP:")
        self.ip_label.pack()

        self.ip_entry = Entry(root, width=50)
        self.ip_entry.pack()

        self.port_label = tk.Label(root, text="Server Port:")
        self.port_label.pack()

        self.port_entry = Entry(root, width=50)
        self.port_entry.pack()

        self.connect_button = Button(root, text="Connect", command=self.connect_to_server)
        self.connect_button.pack()

        self.url_label = tk.Label(root, text="Enter URL:")
        self.url_label.pack()

        self.url_entry = Entry(root, width=50)
        self.url_entry.pack()

        self.send_url_button = Button(root, text="Send URL", command=self.send_url, state=tk.DISABLED)
        self.send_url_button.pack()

        self.disconnect_button = Button(root, text="Disconnect", command=self.disconnect, state=tk.DISABLED)
        self.disconnect_button.pack()

        self.save_button = Button(root, text="Save HTML", command=self.save_html, state=tk.DISABLED)
        self.save_button.pack()

        self.text_area = Text(root, wrap=tk.WORD)
        self.text_area.pack(expand="true", fill="both")

        self.scroll = Scrollbar(root, command=self.text_area.yview)
        self.scroll.pack(side="right", fill="y")
        self.text_area.config(yscrollcommand=self.scroll.set)

        self.client_socket = None
        self.connected = False

    def connect_to_server(self):
        server_ip = self.ip_entry.get()
        server_port = int(self.port_entry.get())

        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client.connect((server_ip, server_port))
            self.client_socket = client
            self.send_url_button["state"] = tk.NORMAL
            self.disconnect_button["state"] = tk.NORMAL
            self.text_area.insert("1.0", f"Connected to server at {server_ip}:{server_port}\n")
            self.connected = True
        except ConnectionRefusedError:
            self.text_area.insert("1.0", "Connection to the server failed. Make sure the server is running.\n")

    def send_url(self):
        if self.client_socket is None:
            return

        url = self.url_entry.get()
        self.client_socket.send(f"GET {url} HTTP/1.1\r\nHost: {url}\r\n\r\n".encode('utf-8'))

        response = b""
        while True:
            part = self.client_socket.recv(4096)
            if not part:
                break
            response += part

        content_start = response.find(b'\r\n\r\n') + 4
        page_content = response[content_start:]

        self.save_button["state"] = tk.NORMAL
        self.text_area.insert(tk.END, "Received HTML content. You can now save it.\n")
        self.html_content = page_content

    def disconnect(self):
        if self.client_socket:
            self.client_socket.close()
            self.client_socket = None
            self.text_area.insert(tk.END, "Disconnected from the server.\n")
            self.send_url_button["state"] = tk.DISABLED
            self.disconnect_button["state"] = tk.DISABLED
            self.save_button["state"] = tk.DISABLED
            self.connected = False

    def save_html(self):
        if self.html_content:
            filename = filedialog.asksaveasfilename(defaultextension=".html", filetypes=[("HTML files", "*.html")])
            if filename:
                with open(filename, 'wb') as file:
                    file.write(self.html_content)
                self.text_area.insert(tk.END, f"Saved the HTML content as {filename}\n")
                self.disconnect()

def main():
    root = tk.Tk()
    app = ClientApp(root)
    root.mainloop()

if __name__ == '__main__':
    main()
