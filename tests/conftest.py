import pytest
from click.testing import CliRunner
from in3 import client
from in3.eth.model import Block


@pytest.fixture
def in3_mock(mocker):
    return mocker.MagicMock(spec=client)


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def mock_block():
    return Block(
        author="AUTHOR",
        number=9,
        hash="HASH",
        parentHash="PARENT",
        nonce=1,
        sha3Uncles=["UNCLES"],
        logsBloom="LOGS",
        transactionsRoot="TRANS_ROOT",
        stateRoot="state",
        miner="miner",
        difficulty=10,
        totalDifficulty=100,
        extraData="2020",
        size=1000,
        gasLimit=1000000000,
        gasUsed=1000000000000,
        timestamp=1234567889,
        transactions=["TRANS"],
        uncles=["UNCLES"]
    )
