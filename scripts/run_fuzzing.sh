#!/bin/bash
set -e
cd fuzzing
pytest test_fuzz.py --hypothesis-show-statistics
# AFL: not run by default, requires afl++ installation