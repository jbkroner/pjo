"""
collect cli options and args and pass them to the parser
"""
import sys

from pjo.Encoder import Encoder


def main():
    args = sys.argv

    # (args(k:v pairs, options) <- Parser

    # printable json <- Encoder.toJson(options, args)

    print(Encoder.encode(args[1:]))


if __name__ == "__main__":
    main()
