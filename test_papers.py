#!/usr/bin/env python3

""" Module to test papers.py  """

__author__ = 'Susan Sim'
__email__ = "ses@drsusansim.org"

__copyright__ = "2014 Susan Sim"
__license__ = "MIT License"

__status__ = "Prototype"

# imports one per line
import pytest
from papers import decide
from papers import valid_passport_format
from papers import valid_date_format
from papers import valid_visa


def test_basic():
    assert decide("test_returning_citizen.json", "watchlist.json", "countries.json") == ["Accept", "Accept"]
    assert decide("test_watchlist.json", "watchlist.json", "countries.json") == ["Secondary"]
    assert decide("test_quarantine.json", "watchlist.json", "countries.json") == ["Quarantine"]


def test_files():
    with pytest.raises(FileNotFoundError):
        decide("test_returning_citizen.json", "", "countries.json")


def test_valid_passport_format():
    assert valid_passport_format("RHDP2-TY5E4-S4BGO-VSKW7-ID3TX") is True
    assert valid_passport_format("T3SDR-T7JU8-E4TFH-BV34J-NI34") is False
    assert valid_passport_format("RE45-HY78T-3DRF4-OP113-DOJ41") is False


def test_valid_date_format():
    assert valid_date_format("2014-10-03") is True
    assert valid_date_format("09-12-1987") is False
    assert valid_date_format("111-03-21") is False


def test_valid_visa():
    assert valid_visa("LY71X-APFE8", "2013-04-03") is True
    assert valid_visa("I5K2J-HI90", "2013-09-11") is False
    assert valid_visa("T6HY7-ETG67", "2007-12-02") is False