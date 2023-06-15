from typing import Optional, TypeVar, Type, cast


def replaceNoneWithEmptyString(value: Optional[str]) -> str:
    if value is None:
        return ""
    else:
        return value


T = TypeVar("T")


def expect_type(typ: Type[T], obj: object) -> T:
    if isinstance(obj, typ):
        return cast(T, typ)
    else:
        raise TypeError("{} is not an instance of {}".format(obj, typ))
