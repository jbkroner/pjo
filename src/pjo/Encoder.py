"""
Encode KV pairs into JSON
"""
from ensurepip import version
import json
import re
import base64
import pkg_resources
from loguru import logger
from pjo.Value import Value, Object_, Array, String, Number, Bool, Null


class Encoder:
    VERSION = pkg_resources.get_distribution("pjo").version
    VERSION_JSON = '{version:"' + VERSION + '"}'
    DELIM = "="
    DELIMS = ["=", "@"]
    OPTIONS = {
        "-a": {"helpText": "return an array"},
        "-h": {"helpText": "display this text"},
        "-p": {"helpText": "pretty print"},
        "-l": {"helpText": "log stuff"},
        "-B": {"helpText": "disable boolean true/false/null detection"},
        "-D": {"helpText": "de-duplicate object keys"},
        "-e": {"helpText": "ignore empty input"},
        "-v": {"helpText": "show version"},
        "-V": {"helpText": "show verison as JSON"},
        "k=@<fileOrValue>": {"helpText": "read a file"},
        "k=%<fileOrValue>": {"helpText": "encode a file or value into base64"},
        "k=:something.json": {"helpText": "read in a json file"},
    }
    SEPERATORS = [",", ":"]
    INDENT_SIZE = 3

    ESCAPABLE_CHARACTERS = []

    def encode(input: list[str]) -> str:
        if "-h" in input:
            return json.dumps(Encoder.OPTIONS, indent=Encoder.INDENT_SIZE)

        elif "-v" in input:
            return Encoder.VERSION

        elif "-V" in input:
            return Encoder.VERSION_JSON

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

        if "-D" in options:
            logger.debug("de-duplicating keys")
            tmp = {}
            for key in obj.keys():
                if not tmp.get(key):
                    tmp[key] = obj[key]
            obj = tmp

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
                args.append(Encoder._to_value(e, options))

            # Maybe KV pair if DELIM in e and DELIM is not the first element (we can have key with no value usually)
            elif Encoder.DELIM in e or "@" in e or "=%" in e or "=:":
                args.append(Encoder._key_value_split(e))

            else:
                raise ValueError(
                    f"an invalid token has been passed in: {e}.  Most likely no delimiter was found."
                )

        if len(args) == 0 and "-e" not in options:
            raise ValueError("no kvpairs provided!")

        return args, options

    def _kvpairs_to_dict(
        args: list[tuple[str, str]], options: list[str]
    ) -> dict or list:
        d = {}
        a = []

        if len(args) == 0 and "-e" not in options:
            raise ValueError(
                f"empty list of args, use -e if you might have empty input"
            )

        if "-a" in options:
            for (key, value) in args:
                a.append(Encoder._to_value(value, options))
            return a

        for (key, value) in args:
            d[key] = Encoder._to_value(value, options)
        return d

    def _to_value(maybe_value: str, options: list = list()) -> Value:
        # is it empty or Null?
        if not len(maybe_value) or maybe_value in ["null"] and "-B" not in options:
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

                e2v = Encoder._to_value(e, options)

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
        elif Encoder._is_bool(maybe_value) and "-B" not in options:
            val = Encoder._str_to_boolean(maybe_value)
            logger.debug(f"found bool -> {val}")

        # bools it a valid string?
        elif Encoder._is_string(maybe_value):
            maybe_value: str
            val = maybe_value.strip("\\")
            logger.debug(f"found string -> {val}")

        else:
            # this case could get wrapped into the is_string case
            # having an additional case allows for some more contextual logging.
            logger.debug(
                f"unable to parse {maybe_value} into a type. catch all is to treat it as a string.  If the the -B flag is set then booleans and nulls will be treated like strings."
            )
            val = maybe_value

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
        if len(key_value_pair) == 0:
            raise ValueError("input str is empty")

        # special case: the value is a file.  read it and pass the contents as a value.
        if (
            Encoder.DELIM in key_value_pair
            and "@" in key_value_pair
            and "=@" in key_value_pair
        ):
            logger.debug(f"attempting to read in a file in kvpair {key_value_pair}")
            kv_list = key_value_pair.split("=@", maxsplit=1)
            key = kv_list[0]
            maybe_filename = kv_list[1]
            try:
                with open(maybe_filename) as f:
                    contents = f.read().strip("\n")
                    return key, contents
            except FileNotFoundError as e:
                logger.error(
                    f"could not file file {maybe_filename}. are you trying to encode something like a twitter handle? include an escape character please"
                )
                return key, maybe_filename

        # special case 2: the value is a file.  same as above but base64 encoded
        # if its not a file, enocde it anyways!
        elif (
            Encoder.DELIM in key_value_pair
            and "%" in key_value_pair
            and "=%" in key_value_pair
        ):
            logger.debug(
                f"attempting to read in a file in kvpair {key_value_pair} and then encode it"
            )
            kv_list = key_value_pair.split("=%", maxsplit=1)
            key = kv_list[0]
            maybe_filename = kv_list[1]
            try:
                with open(maybe_filename) as f:
                    contents = f.read().strip("\n")
                    encoded = Encoder._b64_stringify(contents)
                    return key, encoded
            except FileNotFoundError as e:
                logger.error(
                    f"could not file file {maybe_filename}, it must be a value. encoding that instead."
                )
                return key, Encoder._b64_stringify(maybe_filename)

        # special case 3: its a json file
        elif (
            Encoder.DELIM in key_value_pair
            and ":" in key_value_pair
            and "=:" in key_value_pair
        ):
            logger.debug(
                f"attempting to read in a json file in kvpair {key_value_pair}"
            )
            kv_list = key_value_pair.split("=:", maxsplit=1)
            key = kv_list[0]
            maybe_filename = kv_list[1]

            try:
                with open(maybe_filename) as f:
                    json_data: dict = json.load(f)
                    contents: str = json.dumps(json_data, separators=Encoder.SEPERATORS)
                    return key, contents
            except FileNotFoundError as e:
                logger.error(
                    f"could not file file {maybe_filename}, it must be a value. encoding that instead."
                )
                return key, maybe_filename

        elif Encoder.DELIM in key_value_pair:
            logger.debug(f"splitting {key_value_pair} along {Encoder.DELIM}")
            kv_list = key_value_pair.split(Encoder.DELIM, maxsplit=1)
            return kv_list[0], kv_list[1]

        #   pjo treats key@value specifically as boolean JSON elements:
        #   if the value begins with T, t, or the numeric value is greater than zero, the result is true, else false.
        elif "@" in key_value_pair:
            logger.debug(f"type coercion: splitting {key_value_pair} along @")
            kv_list = key_value_pair.split("@", maxsplit=1)
            key = kv_list[0]
            value = kv_list[1]

            value = Encoder._to_value(value, options)
            if type(value) == str and len(value) and value[0] in ["T", "t"]:
                value = "true"
            elif type(value) == int and value > 0:
                value = "true"
            elif type(value) == float and value > 0:
                value = "true"
            else:
                value = "false"

            return key, value

    @staticmethod
    def _b64_stringify(s: str) -> str:
        return str(base64.b64encode(s.encode("ascii")))[2:-1]

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
