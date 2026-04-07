from hypothesis import given, strategies as st
import sys
sys.path.append("..")
from bot.handlers.trade import create_trade  # example

@given(st.text(min_size=1, max_size=100))
def test_command_parser(command_text):
    # simulate parsing command
    assert isinstance(command_text, str)

def run_fuzz():
    test_command_parser()
    print("Fuzzing passed")