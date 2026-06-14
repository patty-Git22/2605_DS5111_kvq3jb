import sys
import io
import pytest
from lab2.clean_ids import main, validate_id


def test_script_execution(monkeypatch, capsys):
    # 1. Simulate the standard input data
    # We use io.StringIO to make a string act like a readable stream/file
    fake_input = io.StringIO("kcFsuxaJ1es\nasd123\n")
    monkeypatch.setattr(sys, "stdin", fake_input)

    # 2. Run the script's main logic
    main()

    # 3. Capture the printed output
    captured = capsys.readouterr()

    # 4. Assert that the data was modified correctly
    assert captured.out == "kcFsuxaJ1es\n"


def test_good_bad_good(monkeypatch, capsys):
    monkeypatch.setattr(sys, "stdin", io.StringIO("kcFsuxaJ1es\nasd123\nHn4tR8wZ0aF\n"))
    main()
    assert capsys.readouterr().out == "kcFsuxaJ1es\nHn4tR8wZ0aF\n"


def test_only_bad_lines(monkeypatch, capsys):
    monkeypatch.setattr(sys, "stdin", io.StringIO("asd123\nxK9\n\n"))
    main()
    assert capsys.readouterr().out == ""

def test_keyboard_interrupt_exits_cleanly(monkeypatch):
    class InterruptingStdin:
        def __iter__(self):
            return self
        def __next__(self):
            raise KeyboardInterrupt

    monkeypatch.setattr(sys, "stdin", InterruptingStdin())
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 0


@pytest.mark.parametrize("value,expected", [
    ("7vKp2mQ9xLd", True),     # valid 11-char id
    ("bad id!", False),        # space/punctuation not allowed
    ("Z_p-3Qb8nW2", True),     # underscore and hyphen are valid
    ("xK9", False),            # too short
    ("7vKp2mQ9xLdR", False),   # one too many characters
    ("Hn4tR8wZ0aF", True),     # valid 11-char id
])
def test_validate_id(value, expected):
    assert validate_id(value) == expected
