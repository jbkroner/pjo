# data Value = Object !Object
#            | Array !Array
#            | String !Text
#            | Number !Scientific
#            | Bool !Bool
#            | Null
#              deriving (Eq, Read, Typeable, Data, Generic)


class Value:
    def __init__(self, value) -> None:
        self.value = value


class Object_(Value):
    def __init__(self, value: dict) -> None:
        super().__init__(value)


class Array(Value):
    def __init__(self, value) -> None:
        super().__init__(value)


class String(Value):
    def __init__(self, value: str) -> None:
        super().__init__(value)


class Number(Value):
    def __init__(self, value) -> None:
        super().__init__(value)


class Bool(Value):
    def __init__(self, value) -> None:
        super().__init__(value)


class Null(Value):
    def __init__(self) -> None:
        super().__init__(None)

    def __str__(self) -> str:
        return None
