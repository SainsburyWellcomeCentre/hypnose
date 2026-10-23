"""
Listen to Pinnacle/Sirenia UDP multicast and log every sample, split by stream.

Packet layout:
    bytes 0-25 : stream ID, ASCII, padded, "DeviceName_StreamName"
    bytes 26-  : ASCII "seconds,subseconds,value" (+ optional terminator)

Use it to check what Pinnacle is sending before/alongside Bonsai.
Several listeners (this script and Bonsai nodes) can run at the same time.

    python multicast_receiver_parse_stream_ID.py
    python multicast_receiver_parse_stream_ID.py --stream Mouse1_EEG1
    python multicast_receiver_parse_stream_ID.py --interface 127.0.0.1
"""

import argparse
import socket
import struct
import time

MULTICAST_GROUP = "239.255.76.67"
PORT = 8866
STREAM_ID_LEN = 26
PAD = "\x00 \r\n\t"


LOG_COLUMNS = [
    "host_time_ns", "src", "length", "stream", "device", "channel",
    "seconds", "subseconds", "value", "parsed", "payload", "raw_hex",
]


def escape(data: bytes) -> str:
    """Printable, tab/newline-free rendering of raw bytes (\\t, \\n, \\x00 ...)."""
    return data.decode("latin-1").encode("unicode_escape").decode("ascii")


def parse_packet(data: bytes):
    """Return (stream_id, device, channel, seconds, subseconds, value, fields, ok).

    Never discards a packet: seconds/subseconds/value are the original text
    fields (exactly as sent) and `ok` says whether they are valid numbers
    in the expected 3-field layout.
    """
    stream_id = data[:STREAM_ID_LEN].decode("ascii", "ignore").strip(PAD)
    device, _, channel = stream_id.partition("_")
    fields = [f.strip(PAD) for f in data[STREAM_ID_LEN:].decode("ascii", "ignore").strip(PAD).split(",")]
    ok = len(data) > STREAM_ID_LEN and len(fields) == 3
    if ok:
        try:
            int(fields[0]), float(fields[1]), float(fields[2])
        except ValueError:
            ok = False
    sec, subsec, value = fields if len(fields) == 3 else ("", "", "")
    return stream_id, device, channel or device, sec, subsec, value, ok


def open_socket(interface_ip):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # share the port with Bonsai
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 4 * 1024 * 1024)
    sock.bind(("", PORT))
    mreq = struct.pack("4s4s", socket.inet_aton(MULTICAST_GROUP), socket.inet_aton(interface_ip))
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    sock.settimeout(1.0)  # so Ctrl+C works on Windows
    return sock, mreq


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--interface", default="0.0.0.0", help="Adapter IP to join on (default: OS default)")
    ap.add_argument("--stream", default="", help="Only show this stream ID, e.g. Mouse1_EEG1")
    ap.add_argument("--log", default="output.tsv", help="Log file, every packet incl. raw bytes ('' to disable)")
    ap.add_argument("--quiet", action="store_true", help="Don't print every sample")
    args = ap.parse_args()

    sock, mreq = open_socket(args.interface)
    log = open(args.log, "w", buffering=1) if args.log else None
    if log:
        log.write("\t".join(LOG_COLUMNS) + "\n")
    print(f"Listening on {MULTICAST_GROUP}:{PORT} (interface {args.interface})...")

    counts, bad = {}, 0
    try:
        while True:
            try:
                data, addr = sock.recvfrom(65535)
            except socket.timeout:
                continue
            t_ns = time.time_ns()
            stream_id, device, channel, sec, subsec, value, ok = parse_packet(data)
            if args.stream and stream_id.lower() != args.stream.lower():
                continue
            counts[stream_id] = counts.get(stream_id, 0) + 1
            if not ok:
                bad += 1
            if log:
                row = [
                    t_ns, f"{addr[0]}:{addr[1]}", len(data), stream_id, device, channel,
                    sec, subsec, value, int(ok), escape(data[STREAM_ID_LEN:]), data.hex(),
                ]
                log.write("\t".join(map(str, row)) + "\n")
            if not args.quiet:
                print(
                    f"{t_ns} {addr[0]}:{addr[1]} len={len(data)} "
                    f"id[0:{STREAM_ID_LEN}]='{escape(data[:STREAM_ID_LEN])}' "
                    f"payload='{escape(data[STREAM_ID_LEN:])}' "
                    f"{'OK' if ok else 'UNPARSED'} hex={data.hex()}"
                )
    except KeyboardInterrupt:
        print("\nStopped. Samples per stream:")
        for s, n in sorted(counts.items()):
            print(f"  {s}: {n}")
        if bad:
            print(f"  (unparsed packets: {bad})")
    finally:
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_DROP_MEMBERSHIP, mreq)
        sock.close()
        if log:
            log.close()


if __name__ == "__main__":
    main()
