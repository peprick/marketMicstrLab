SCHEMA_VERSION = 1
DEFAULT_SOURCE = "kraken_ws_v2"


def raw_envelope(payload: dict, capture_ts_ns: int, recv_seq: int) -> dict:
    return {
        "schema_version": SCHEMA_VERSION,
        "source": DEFAULT_SOURCE,
        "capture_ts_ns": capture_ts_ns,
        "recv_seq": recv_seq,
        "payload": payload,
    }
