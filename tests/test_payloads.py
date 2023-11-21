from dataclasses import dataclass
import pytest
from axon.adapter.payloads import payloadclass, dumps


@pytest.fixture
def cls_person():
    @payloadclass("person")
    @dataclass
    class Person:
        id: int
        name: str

    return Person


def test_dataclass_check():
    with pytest.raises(TypeError, match="not a dataclass"):

        @payloadclass("person")
        class NotADataclass:
            ...


def test_payload_type_for_class():
    @payloadclass("person")
    @dataclass
    class Person:
        ...

    # assert payload_type_for_class(Person) == "person"
    assert payloadclass.type_name(Person) == "person"


def test_object_from_payload():
    @payloadclass("person")
    @dataclass
    class Person:
        id: int
        name: str

    # person = object_from_payload("person", {"id": 1234, "name": "Ayaz"})
    person = payloadclass.to_instance("person", {"id": 1234, "name": "Ayaz"})
    assert person.id == 1234
    assert person.name == "Ayaz"


def test_payload_from_object():
    @payloadclass("person")
    @dataclass
    class Person:
        id: int
        name: str

    # person = payload_from_object(Person(1234, "Ayaz"))
    person = payloadclass.to_payload(Person(1234, "Ayaz"))
    assert person.get("id") == 1234
    assert person.get("name") == "Ayaz"


def test_dumps():
    @payloadclass("person")
    @dataclass
    class Person:
        id: int
        name: str

    json_res = dumps({"person": Person(1234, "Ayaz")})
    assert json_res == '{"person": {"id": 1234, "name": "Ayaz"}}'
