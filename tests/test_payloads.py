import pytest
from axon.adapter.payloads import *


def test_dataclass_check():
    with pytest.raises(TypeError, match="not a dataclass"):

        @payloadclass("person")
        class NotADataclass:
            ...

    # payload = payload_from_object(NotADataclass())
    # assert payload.get("name") == "garfield"
