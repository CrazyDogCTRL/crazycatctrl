import socket
from response import ResponseGenerator

HOST = ("localhost", 7777)

def run():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(HOST)
    server_socket.listen()
    print("Сервер запущен и ожидает подключений!")

    while True:
        client_socket, addr = server_socket.accept()
        request = client_socket.recv(2048)
        response = ResponseGenerator.generate_result(request.decode("UTF-8"))
        client_socket.sendall(response)
        client_socket.close()

if __name__ == "__main__":
    run()

