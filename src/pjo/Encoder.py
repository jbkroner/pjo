"""
Encode KV pairs into JSON
"""
from curses.ascii import isdigit
import json
import re
from tokenize import maybe
from click import option
from loguru import logger
from pjo.Value import Value, Object_, Array, String, Number, Bool, Null


class Encoder:
    DELIM = "="
    OPTIONS = {
        "-a": {"helpText": "return an array"},
        "-h": {"helpText": "display this text"},
        "-p": {"helpText": "pretty print"},
        "-l": {"helpText": "log stuff"},
    }
    SEPERATORS = [",", ":"]
    INDENT_SIZE = 3

    def encode(input: list[str]) -> str:
        if "-l" not in input:
            logger.disable("pjo")

        args, options = Encoder.split_args_options(input)

        logger.debug(f"args before procesing: {args}")
        logger.debug(f"options before procesing: {options}")

        if "-a" in options and "-p" in options:
            logger.debug(f"encoding as a list, pretty printing")
            return json.dumps(list(args), indent=Encoder.INDENT_SIZE)
        elif "-a" in options:
            logger.debug(f"encoding as a list")
            return json.dumps(list(args), separators=Encoder.SEPERATORS)

        obj = Encoder._kvpairs_to_dict(args, options)
        if "-p" in options:
            return json.dumps(obj, indent=Encoder.INDENT_SIZE)
        return json.dumps(obj, separators=Encoder.SEPERATORS)

    def split_args_options(input: list[str]) -> tuple[list, list]:
        options = []  # cli options
        args = []  #

        if len(input) == 0:
            raise ValueError("not args or options provided")

        # special handling if we want to generate an array
        # there are no keys / values now.  We need simply seperate list elements from options.
        # we need to check -a before we actually process the other options!
        for e in input:
            logger.debug(f"current elem -> {e}")

            # Maybe option
            if e[0] == "-":

                # validate it
                if not Encoder._validate_option(e):
                    raise ValueError(f"{e} is not a valid option")

                options.append(e)

            # in this case we are just building a list.
            elif "-a" in input:
                args.append(Encoder._to_value(e))

            # Maybe KV pair if DELIM in e and DELIM is not the first element (we can have key with no value usually)
            elif Encoder.DELIM in e:
                args.append(Encoder._key_value_split(e))

            else:
                raise ValueError(f"an invalid token has been passed in: {e}")

        if len(args) == 0:
            raise ValueError("no kvpairs provided!")

        return args, options

    def _kvpairs_to_dict(
        args: list[tuple[str, str]], options: list[str]
    ) -> dict or list:
        d = {}
        a = []

        if len(args) == 0:
            raise ValueError(f"empty list of args")

        if "-a" in options:
            for (key, value) in args:
                a.append(Encoder._to_value(value))
            return a

        for (key, value) in args:
            d[key] = Encoder._to_value(value)
        return d

    def _to_value(maybe_value: str) -> Value:
        # is it empty or Null?
        if not len(maybe_value) or maybe_value in ["null"]:
            val = Null().value

        # is it a nested object?
        elif maybe_value[0] == "{":
            logger.debug(f"nested found -> {maybe_value}")
            val = json.loads(maybe_value)
            logger.debug(f"nested after loading -> {val}, type = {type(val)}")

        # is it an array?
        elif maybe_value[0] == "[":

            # we we need to break down this string and turn it into a list of values!
            val = list()
            for e in maybe_value[1:-1].split(","):
                e.replace(" ", "")

                e2v = Encoder._to_value(e)

                if type(e2v) == str:
                    e2v = e2v[1:-1]

                val.append(e2v)

            logger.debug(f"found Array -> {val}")

        # is it a float?
        elif re.match(r"^-?\d+(?:\.\d+)$", maybe_value) is not None:
            val = float(maybe_value)
            logger.debug(f"found Float -> {val}")

        # is it an int?
        elif maybe_value.isdigit():
            val = int(maybe_value)
            logger.debug(f"found Int -> {val}")

        # negatives
        elif maybe_value[0] == "-" and maybe_value[1:].isdigit():
            val = int(maybe_value)
            logger.debug(f"found NegInt -> {val}")

        # booleans
        elif Encoder._is_bool(maybe_value):
            val = Encoder._str_to_boolean(maybe_value)
            logger.debug(f"found bool -> {val}")

        # bools it a valid string?
        elif Encoder._is_string(maybe_value):
            val = String(value=maybe_value).value
            logger.debug(f"found string -> {val}")

        else:
            val = "ERROR"

        return val

    def _validate_option(option: str) -> bool:
        if len(option) < 2:
            return False

        if option[0] != "-":
            return False

        if option not in Encoder.OPTIONS.keys():
            return False

        return True

    @staticmethod
    def _key_value_split(key_value_pair: str) -> tuple[str, str]:
        # TODO arg handling
        if len(key_value_pair) == 0:
            raise ValueError("input str is empty")

        # no empty strings
        if key_value_pair[0] == Encoder.DELIM:
            raise ValueError(
                f"delim is first elem in {key_value_pair}.  We *must* have a key, values are usually optional."
            )

        # must have delim
        if Encoder.DELIM not in key_value_pair:
            raise ValueError(f"invalid token {key_value_pair}")

        # split key and value
        kv_list = key_value_pair.split(Encoder.DELIM, maxsplit=1)
        return kv_list[0], kv_list[1]

        # k={k2=v2}

    @staticmethod
    def _is_string(input: str) -> bool:
        # str -> bool -> bool
        # return true if:
        # is not only integers (0-9)
        # is not a float
        # is not a bool ('true', 'false')

        has_digits = input.isdigit()
        has_bool = False

        # check if it's a float
        # https://stackoverflow.com/questions/736043/checking-if-a-string-can-be-converted-to-float-in-python
        if not re.match(r"^-?\d+(?:\.\d+)$", input) is None:
            has_digits = True

        if input in ["true", "false", "null"]:
            has_bool = True

        if has_digits or has_bool:
            return False
        return True

    @staticmethod
    def _is_bool(input: str) -> bool:
        return input in ["true", "false"]

    @staticmethod
    def _str_to_boolean(input: str) -> bool:
        if not Encoder._is_bool(input):
            raise ValueError(f"input {input} cannot be evaluated to a bool")

        if input in ["true"]:
            return True
        return False
