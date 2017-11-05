"""
Nose tests for flask_main.py
"""
from flask_main import humanize_arrow_date
import arrow

import nose    # Testing framework
import logging


def test_for_humanize_today():
    now = arrow.utcnow()
    print("now", humanize_arrow_date(now))
    assert (humanize_arrow_date(now) == "Today")


def test_for_humanize_tomorrow():
    now = arrow.utcnow().replace(hour=0, minute=0, second=0).shift(days=1)
    assert (humanize_arrow_date(now) == "Tomorrow")


def test_for_humanize_yesterday():
    now = arrow.utcnow().replace(hour=0, minute=0, second=0).shift(days=-1)
    print("now: ", humanize_arrow_date(now))
    assert (humanize_arrow_date(now) == "Yesterday")


def test_for_humanize_long_ago():
    now = arrow.utcnow().replace(hour=0, minute=0, second=0).shift(years=-1234)
    print("now: ", humanize_arrow_date(now))
    assert (humanize_arrow_date(now) == "1234 years ago")


def test_for_humanize_far_away():
    now = arrow.utcnow().replace(hour=0, minute=0, second=0).shift(years=1234)
    print("now: ", humanize_arrow_date(now))
    assert (humanize_arrow_date(now) == "in 1234 years")
