from fastapi.testclient import TestClient

from optipy.utils.strings import to_camel


class TestToCamel:
    def test_expected_input(self, client: TestClient):
        result = to_camel("foo_bar")
        assert result == "fooBar"

    def test_single_word(self):
        result = to_camel("foo")
        assert result == "foo"

    def test_already_in_camel_case(self):
        result = to_camel("fooBar")
        assert result == "fooBar"

    def test_many_words(self):
        result = to_camel("foo_bar_fizz_buzz")
        assert result == "fooBarFizzBuzz"

    def test_multiple_underscores(self):
        result = to_camel("foo__bar")
        assert result == "fooBar"
