from pjo.Encoder import Encoder
import pytest


class TestSplitArgOptions:
    def test_invalid_not_args_or_options(self):
        input = []
        with pytest.raises(ValueError):
            args, options = Encoder.split_args_options(input)

    def test_invalid_bad_option(self):
        input = ["--invalid"]
        with pytest.raises(ValueError):
            args, options = Encoder.split_args_options(input)

    def test_invalid_no_kv_pairs(self):
        input = ["-a"]
        with pytest.raises(ValueError):
            args, options = Encoder.split_args_options(input)

    def test_valid_000(self):
        input = ["k=v"]
        args, options = Encoder.split_args_options(input)
        assert args == [("k", "v")]
        assert options == []

    def test_valid_001(self):
        input = ["k=v", "k2=v2"]
        args, options = Encoder.split_args_options(input)
        assert args == [("k", "v"), ("k2", "v2")]
        assert options == []

    def test_valid_002(self):
        input = ["-a", "k=v"]
        args, options = Encoder.split_args_options(input)
        assert args == [("k", "v")]
        assert options == ["-a"]


class TestBuildDict:
    def test_invalid_empty_args(self):
        args = []
        options = []

        with pytest.raises(ValueError):
            d = Encoder._kvpairs_to_dict(args, options)

    def test_valid_000(self):
        args = [("k", "v")]
        options = []

        d = Encoder._kvpairs_to_dict(args, options)

        assert d == {"k": "v"}

    def test_valid_001(self):
        args = [("k", "v"), ("k2", "v2")]
        options = []

        d = Encoder._kvpairs_to_dict(args, options)

        assert d == {"k": "v", "k2": "v2"}


class TestValidateOption:
    def test_invalid_too_short_000(self):
        option = ""
        assert Encoder._validate_option(option) == False

    def test_invalid_too_short_001(self):
        option = "-"
        assert Encoder._validate_option(option) == False

    def test_invalid_not_in_list(self):
        option = "--invalid"
        assert Encoder._validate_option(option) == False

    def test_valid_000(self):
        option = "-a"
        assert Encoder._validate_option(option)


class TestKeyValueSplit:
    def test_invalid_empty(self):
        input = ""
        with pytest.raises(ValueError):
            Encoder._key_value_split(input)

    def test_invalid_no_delim(self):
        input = ""
        with pytest.raises(ValueError):
            Encoder._key_value_split(input)

    def test_valid_string_string(self):
        input = "k=v"
        result_key, result_value = Encoder._key_value_split(input)
        expected_key = "k"
        expected_value = "v"

        assert result_key == expected_key
        assert result_value == expected_value

    def test_valid_string_number(self):
        input = "k=1"
        result_key, result_value = Encoder._key_value_split(input)
        expected_key = "k"
        expected_value = "1"

        assert result_key == expected_key
        assert result_value == expected_value

    def test_valid_string_bool(self):
        input = "k=true"
        result_key, result_value = Encoder._key_value_split(input)
        expected_key = "k"
        expected_value = "true"

        assert result_key == expected_key
        assert result_value == expected_value

    def test_valid_string_null(self):
        input = "k=Null"
        result_key, result_value = Encoder._key_value_split(input)
        expected_key = "k"
        expected_value = "Null"

        assert result_key == expected_key
        assert result_value == expected_value

    def test_valid_string_null_2(self):
        input = "k=null"
        result_key, result_value = Encoder._key_value_split(input)
        expected_key = "k"
        expected_value = "null"

        assert result_key == expected_key
        assert result_value == expected_value

    def test_valid_no_value(self):
        input = "k="
        result_key, result_value = Encoder._key_value_split(input)
        expected_key = "k"
        expected_value = ""

        assert result_key == expected_key
        assert result_value == expected_value

    def test_valid_more_than_one_delim(self):
        input = "k={k2=v2}"
        result_key, result_value = Encoder._key_value_split(input)
        expected_key = "k"
        expected_value = "{k2=v2}"

        assert result_key == expected_key
        assert result_value == expected_value


class Test_is_string:
    def test_is_string_true(self):
        assert Encoder._is_string("x")

    def test_is_string_int(self):
        assert Encoder._is_string("1") == False

    def test_is_string_float(self):
        assert Encoder._is_string("1.1") == False

    def test_is_string_None(self):
        assert Encoder._is_string("None") == False

    def test_is_string_None(self):
        assert Encoder._is_string("null") == False

    def test_is_string_bool_000(self):
        assert Encoder._is_string("true") == False

    def test_is_string_bool_001(self):
        assert Encoder._is_string("false") == False


class Test_Is_Bool:
    def test_valid_true(self):
        assert Encoder._is_bool("true")

    def test_valid_false(self):
        assert Encoder._is_bool("false")

    def test_invalid_000(self):
        assert Encoder._is_bool("something") == False


class Test_str_to_boolean:
    def test_invalid(self):
        with pytest.raises(ValueError):
            Encoder._str_to_boolean("not a bool")

    def test_valid_true(self):
        assert Encoder._str_to_boolean("true") == True

    def test_valid_False(self):
        assert Encoder._str_to_boolean("false") == False


class Test_dummy:
    def test(self):
        assert True
