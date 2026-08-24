"""
Minimal, standalone Astron connectivity probe.

No Panda3D, no game code, no Wireshark -- just Python's built-in `socket`
module. This connects directly to Astron's Message Director and asks a
trivial question ("does object 999999999 exist?") addressed to the
database control channel. Even if the object doesn't exist, Astron's
database role should reply almost instantly with a "not found" response.

If we get ANY response -> Astron's DB role is alive and answering, and the
real bug is specific to the createObject() call itself (bad payload, bad
timing, etc). Keep debugging the Python game code.

If we get NO response (timeout) -> Astron's DB role itself isn't
listening/responding at all, regardless of what the game code sends.
Stop debugging Python -- the problem is the astrond binary, the Mongo
backend, or the cluster.yml config.

Usage:
    dependencies\\panda\\python\\python.exe astron_probe.py
(run from the project root, or edit HOST/PORT/DB_CHANNEL below to match
your cluster.yml)
"""
import socket
import struct
import sys

HOST = '127.0.0.1'
PORT = 7199          # messagedirector.bind port from your cluster.yml
DB_CHANNEL = 4003     # the database role's "control" channel from cluster.yml
MY_CHANNEL = 5555555555  # arbitrary probe channel, just needs to be unused

CONTROL_MESSAGE = 1
CONTROL_ADD_CHANNEL = 9000
DBSERVER_OBJECT_GET_ALL = 3014
DBSERVER_OBJECT_GET_ALL_RESP = 3015


def build_datagram(recipients, sender, msg_type, payload=b''):
    body = struct.pack('<B', len(recipients))
    for r in recipients:
        body += struct.pack('<Q', r)
    body += struct.pack('<Q', sender)
    body += struct.pack('<H', msg_type)
    body += payload
    # Astron TCP framing: 2-byte little-endian length prefix, then body.
    return struct.pack('<H', len(body)) + body


def recv_exact(sock, n):
    buf = b''
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            return None
        buf += chunk
    return buf


def read_datagram(sock):
    length_bytes = recv_exact(sock, 2)
    if not length_bytes:
        return None
    length = struct.unpack('<H', length_bytes)[0]
    return recv_exact(sock, length)


def parse_datagram(body):
    pos = 0
    recipient_count = body[pos]
    pos += 1
    recipients = []
    for _ in range(recipient_count):
        recipients.append(struct.unpack_from('<Q', body, pos)[0])
        pos += 8
    sender = struct.unpack_from('<Q', body, pos)[0]
    pos += 8
    msg_type = struct.unpack_from('<H', body, pos)[0]
    pos += 2
    payload = body[pos:]
    return recipients, sender, msg_type, payload


def main():
    print('Connecting to Astron at %s:%d ...' % (HOST, PORT))
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)
    try:
        sock.connect((HOST, PORT))
    except OSError as e:
        print('FAILED TO CONNECT: %s' % e)
        print('-> Astron is not even accepting TCP connections on this port.')
        sys.exit(1)
    print('Connected.')

    # Step 1: subscribe our own arbitrary channel, so any response
    # addressed back to MY_CHANNEL routes back over this same socket.
    add_channel_payload = struct.pack('<Q', MY_CHANNEL)
    dg = build_datagram([CONTROL_MESSAGE], 0, CONTROL_ADD_CHANNEL, add_channel_payload)
    sock.sendall(dg)
    print('Sent CONTROL_ADD_CHANNEL for channel %d' % MY_CHANNEL)

    # Step 2: ask the database role about an object that almost certainly
    # doesn't exist. This needs no DC-file knowledge at all -- the request
    # payload is just [uint32 context][uint32 do_id].
    context = 12345
    do_id = 999999999
    payload = struct.pack('<II', context, do_id)
    dg = build_datagram([DB_CHANNEL], MY_CHANNEL, DBSERVER_OBJECT_GET_ALL, payload)
    sock.sendall(dg)
    print('Sent DBSERVER_OBJECT_GET_ALL for doId=%d to channel %d' % (do_id, DB_CHANNEL))

    print('Waiting up to 10 seconds for a response...')
    try:
        body = read_datagram(sock)
        if body is None:
            print('RESULT: Connection closed by Astron with no data. Astron dropped us.')
        else:
            recipients, sender, msg_type, resp_payload = parse_datagram(body)
            print('RESULT: Got a response!')
            print('  recipients=%r sender=%r msg_type=%r payload=%r' % (
                recipients, sender, msg_type, resp_payload))
            if msg_type == DBSERVER_OBJECT_GET_ALL_RESP:
                print('  -> This is DBSERVER_OBJECT_GET_ALL_RESP as expected.')
                print('  -> Astron\'s database role IS alive and answering requests.')
            else:
                print('  -> Unexpected message type, but Astron DID respond to something.')
    except socket.timeout:
        print('RESULT: TIMED OUT. Astron never responded at all.')
        print('-> The database role is not answering ANY request on channel %d.' % DB_CHANNEL)
        print('-> This is not a game-code bug -- look at astrond/Mongo/cluster.yml.')

    sock.close()


if __name__ == '__main__':
    main()
