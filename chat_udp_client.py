import argparse
import socket
import threading

BUFFER_SIZE = 4096


def receive_loop(sock, goodbye):
    """Receive messages from the server."""

    print("[CLIENT] Receiver thread started!", flush=True)

    while True:
        try:
            data, addr = sock.recvfrom(BUFFER_SIZE)

        except ConnectionResetError as e:
            print(f"[CLIENT] UDP reset: {e}", flush=True)
            continue

        except OSError as e:
            print(f"[CLIENT] Socket error: {e}", flush=True)
            return

        text = data.decode('utf-8', errors='replace')

        print(f"\n[SERVER MESSAGE] {text}", flush=True)

        if text == "Goodbye!":
            goodbye.set()
            return


def run_client(host, port, nickname):

    server = (host, port)

    # Create UDP socket
    sock = socket.socket(
        socket.AF_INET,
        socket.SOCK_DGRAM
    )

    goodbye = threading.Event()

    # Start receiving thread
    thread = threading.Thread(
        target=receive_loop,
        args=(sock, goodbye),
        daemon=True
    )

    thread.start()

    # Register client
    print(f"[CLIENT] Sending join request for {nickname}...")

    sock.sendto(
        f"/join {nickname}".encode('utf-8'),
        server
    )

    try:
        while True:

            try:
                text = input("> ")

            except EOFError:
                text = '/quit'

            # Send message to server
            print(f"[DEBUG CLIENT] Sending: {text}")

            sock.sendto(
                text.encode('utf-8'),
                server
            )

            if text.strip() == '/quit':
                goodbye.wait(timeout=2)
                break

    except KeyboardInterrupt:

        print("\n[CLIENT] Leaving chat...")

        sock.sendto(b'/quit', server)

        goodbye.wait(timeout=2)

    finally:

        sock.close()

        print("[CLIENT] Socket closed.")


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='UDP chat client'
    )

    parser.add_argument('nickname')

    parser.add_argument(
        'host',
        nargs='?',
        default='127.0.0.1'
    )

    parser.add_argument(
        'port',
        nargs='?',
        type=int,
        default=5000
    )

    args = parser.parse_args()

    run_client(
        args.host,
        args.port,
        args.nickname
    )
