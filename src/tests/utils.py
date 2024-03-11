from pytest_mock import MockFixture


def target_of(method) -> str:  # type: ignore
    return f"{method.__module__}.{method.__qualname__}"


def patch_of(mocker: MockFixture, method):  # type: ignore
    target = target_of(method)
    return mocker.patch(target)
