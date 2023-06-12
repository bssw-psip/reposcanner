from typing import Optional


def replaceNoneWithEmptyString(value: Optional[str]) -> str:
    if value is None:
        return ""
    else:
        return value
