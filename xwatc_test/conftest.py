from pytest import fixture

from xwatc.system import Mänx
from xwatc_test.mock_system import MockSystem


@fixture
def system() -> MockSystem:
    return MockSystem()


@fixture
def mänx(system: MockSystem) -> Mänx:
    return system.install()
