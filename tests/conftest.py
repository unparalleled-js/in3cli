import pytest
from click.testing import CliRunner
from in3 import client
from in3.eth.model import Account
from in3.eth.model import Block
from in3.model import In3Node

TEST_ADDRESS = "0x12222f5555f2d32c76cba645297bb2a939577777777777abb749200000000000"
TEST_URL_1 = "www.example.com"
TEST_URL_2 = "www.test.example.com"
TEST_INDEX = 555
TEST_WEIGHT = 2000
TEST_PROPS = 100
TEST_TIMEOUT = 123456789
TEST_REGISTER_TIME = 987654321
TEST_REGISTER_TIME_STR = "2001-04-19 04:25:21"
TEST_DEPOSIT_WEI = 1000000099000000000
TEST_DEPOSIT_GWEI = 1000000099.0
TEST_ACCOUNT = Account(TEST_ADDRESS, 0, None, None)


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
        uncles=["UNCLES"],
    )


def create_test_node(url=None):
    return In3Node(
        url or TEST_URL_1,
        TEST_ACCOUNT,
        TEST_INDEX,
        TEST_DEPOSIT_WEI,
        TEST_PROPS,
        TEST_TIMEOUT,
        TEST_REGISTER_TIME,
        TEST_WEIGHT,
    )
