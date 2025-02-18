import socket
import threading

team_name = ""
my_port = 0
connected_peers = {}
connections = []

def start_server(my_port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(("", my_port))
    server_socket.listen(5)
    print(f"Server listening on port {my_port}")
    while True:
        client_socket, client_address = server_socket.accept()
        peer_ip, peer_port = client_address
        peer_id = f"{peer_ip}:{peer_port}"
        print(client_address)
        if peer_id not in connected_peers:
            threading.Thread(target=handle_client, args=(client_socket, client_address), daemon=True).start()
            connected_peers[peer_id] = client_socket
        else:
            client_socket.close()

def handle_client(client_socket, client_address):
    while True:
        try:
            message = client_socket.recv(1024).decode()
            if not message:
                break
            parts = message.split(" ", 2)
            if len(parts) < 3:
                continue
            sender_id = parts[0]
            sender_team = parts[1]
            content = parts[2]
            connected_peers[sender_id] = client_socket
            if sender_id not in connections:
                connections.append(sender_id)
            if content.lower() == "exit":
                print(f"Peer {sender_id} disconnected.")
                del connected_peers[sender_id]
                connections.remove(sender_id)
                break
            print(f"\nMessage from {sender_id} ({sender_team}) - {content}")
        except:
            break
    client_socket.close()

def connect_peers(my_port):
    local_id = f"{socket.gethostbyname(socket.gethostname())}:{my_port}"
    for peer in connections:
        if peer == local_id:
            continue
        if peer not in connected_peers:
            try:
                ip, port = peer.split(":")
                port = int(port)
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind(("", my_port))
                s.connect((ip, port))
                threading.Thread(target=handle_client, args=(s, (ip, port)), daemon=True).start()
                connected_peers[peer] = s
                msg = f"{socket.gethostbyname(socket.gethostname())}:{my_port} {team_name} CONNECT"
                s.send(msg.encode())
                print(f"Sent connection message to {peer}")
            except:
                print(f"Failed to connect to {peer}")
        else:
            try:
                s = connected_peers[peer]
                msg = f"{socket.gethostbyname(socket.gethostname())}:{my_port} {team_name} CONNECT"
                s.send(msg.encode())
                print(f"Sent connection message to {peer}")
            except:
                print(f"Failed to send connection message to {peer}")

def send_message(my_port):
    while True:
        print("\n***** Menu *****")
        print("1. Send message")
        print("2. Query active peers")
        print("3. Connect to active peers")
        print("0. Quit")
        choice = input("Enter choice: ")
        if choice == "1":
            recipient_ip = input("Enter recipient's IP address: ")
            recipient_port = int(input("Enter recipient's port number: "))
            message = input("Enter your message: ")
            recipient_id = f"{recipient_ip}:{recipient_port}"
            full_message = f"{socket.gethostbyname(socket.gethostname())}:{my_port} {team_name} {message}"
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            if recipient_id not in connected_peers:
                client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                client_socket.bind(("", my_port))
                client_socket.connect((recipient_ip, recipient_port))
                threading.Thread(target=handle_client, args=(client_socket, (recipient_ip, recipient_port))).start()
                connected_peers[recipient_id] = client_socket
            else:
                client_socket = connected_peers[recipient_id]
            client_socket.send(full_message.encode())
            print(f"Message sent to {recipient_ip}:{recipient_port}")
        elif choice == "2":
            print("\nActive Peers:")
            if connections:
                for i in connections:
                    print(i)
            else:
                print("No active peers.")
        elif choice == "3":
            connect_peers(my_port)
        elif choice == "0":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Try again.")

def main():
    global team_name, my_port
    team_name = input("Enter your name: ")
    my_port = int(input("Enter your port number: "))
    print(f"Server listening on port {my_port}")
    threading.Thread(target=start_server, args=(my_port,), daemon=True).start()
    send_message(my_port=my_port)

if __name__ == "__main__":
    main()
