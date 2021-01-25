import enum


def check_robot_resp_ok(resp: str) -> bool:
    return resp.upper() == 'ok'.upper()


class MyEnumMeta(enum.EnumMeta):
    def __contains__(cls, item):
        return item in [v.value for v in cls.__members__.values()]
