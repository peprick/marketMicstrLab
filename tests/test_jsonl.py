from market_micstr_lab.data.jsonl import append_jsonl, read_jsonl, write_jsonl


def test_write_and_read_jsonl(tmp_path) -> None:
    path = tmp_path / "events.jsonl"
    records = [
        {"event_type": "snapshot", "recv_seq": 1},
        {"event_type": "update", "recv_seq": 2},
    ]

    write_jsonl(path, records)

    assert list(read_jsonl(path)) == records


def test_append_jsonl(tmp_path) -> None:
    path = tmp_path / "events.jsonl"

    append_jsonl(path, {"recv_seq": 1})
    append_jsonl(path, {"recv_seq": 2})

    assert list(read_jsonl(path)) == [{"recv_seq": 1}, {"recv_seq": 2}]


def test_read_jsonl_skips_blank_lines(tmp_path) -> None:
    path = tmp_path / "events.jsonl"
    path.write_text('{"recv_seq":1}\n\n{"recv_seq":2}\n', encoding="utf-8")

    assert list(read_jsonl(path)) == [{"recv_seq": 1}, {"recv_seq": 2}]
