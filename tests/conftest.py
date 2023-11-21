import pytest


@pytest.fixture
def vcr_config():
    return {
        "filter_headers": ["authorization"],
        # "ignore_localhost": True,
        "record_mode": "once",
    }
