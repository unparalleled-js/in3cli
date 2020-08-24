import pytest
from click.testing import CliRunner
from in3 import client


@pytest.fixture
def in3_mock(mocker):
    return mocker.MagicMock(spec=client)


@pytest.fixture
def runner():
    return CliRunner()
