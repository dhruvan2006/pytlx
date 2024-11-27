import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from pytlx import Token
from web3 import Web3

class TestToken(unittest.TestCase):
    def setUp(self):
        self.token = Token("BTC5L")
        self.mock_addresses = [
            ("0x123", "BTC5L", 1000),
            ("0x456", "ETH3L", 500),
        ]

    @patch("pytlx.Token.get_contract_addresses")
    def test_get_contract_address(self, mock_get_contract_addresses):
        mock_get_contract_addresses.return_value = self.mock_addresses
        
        address = self.token.get_contract_address()
        self.assertEqual(address, "0x123")

    @patch("requests.get")
    def test_history_contract_address(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {"timestamp": "2024-01-01T00:00:00Z", "price": 50000},
            {"timestamp": "2024-01-02T00:00:00Z", "price": 51000},
        ]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        contract_address = "0x123"
        df = self.token._history_contract_address(contract_address)
        
        expected_df = pd.DataFrame(
            {"Date": ["2024-01-01", "2024-01-02"], "Price": [50000, 51000]}
        )
        expected_df["Date"] = pd.to_datetime(expected_df["Date"], utc=True)
        expected_df.set_index("Date", inplace=True)

        pd.testing.assert_frame_equal(df, expected_df)

    @patch("pytlx.Token.get_contract_address")
    @patch("pytlx.Token._history_contract_address")
    def test_history(self, mock_history_contract_address, mock_get_contract_address):
        mock_get_contract_address.return_value = "0x123"
        mock_history_contract_address.return_value = pd.DataFrame(
            {"Price": [50000, 51000]}, index=pd.to_datetime(["2024-01-01", "2024-01-02"])
        )

        df = self.token.history()
        self.assertIn("Price", df.columns)

    def test_invalid_ticker(self):
        with patch("pytlx.Token.get_contract_address", return_value=None):
            with self.assertRaises(ValueError):
                self.token.history()

class TestTokenLive(unittest.TestCase):
    def test_get_contract_addresses(self):
        addresses = Token("BTC5L").get_contract_addresses()
        tickers = [ticker for _, ticker, *_ in addresses]
        expected_tickers = ['DOGE5L', 'DOGE5S', 'ETH7L', 'ETH7S', 'BTC7L', 'BTC7S', 'ETHBTC2L', 'ETHBTC2S', 'ETHBTC5L', 'ETHBTC5S', 'SUI2L', 'SUI2S', 'SUI5L', 'SUI5S', 'ETHBTC10L', 'ETHBTC10S', 'SEI2L', 'SEI2S', 'SEI5L', 'SEI5S', 'RUNE2L', 'RUNE2S', 'RUNE5L', 'RUNE5S', 'OP1S', 'OP2L', 'OP2S', 'OP5L', 'OP5S', 'ETH3L', 'ETH3S', 'ETH4L', 'ETH4S', 'BTC3L', 'BTC3S', 'BTC4L', 'BTC4S', 'SOL3L', 'SOL3S', 'SOL4L', 'SOL4S', 'PEPE1L', 'PEPE1S', 'PEPE2L', 'PEPE2S', 'PEPE5L', 'PEPE5S', 'DOGE2L', 'DOGE2S', 'ETH1L', 'ETH1S', 'ETH2L', 'ETH2S', 'ETH5L', 'ETH5S', 'BTC1L', 'BTC1S', 'BTC2L', 'BTC2S', 'BTC5L', 'BTC5S', 'SOL1L', 'SOL1S', 'SOL2L', 'SOL2S', 'SOL5L', 'SOL5S', 'LINK1L', 'LINK1S', 'LINK2L', 'LINK2S', 'LINK5L', 'LINK5S', 'OP1L']
        for ticker in expected_tickers:
            assert ticker in tickers
    
    def test_get_contract_address(self):
        address = Token("BTC5L").get_contract_address()
        expected_address = "0x8efd20F6313eB0bc61908b3eB95368BE442A149d"
        assert address == expected_address
    
    def test_history_contract_address(self):
        data = Token("BTC5L")._history_contract_address("0x8efd20F6313eB0bc61908b3eB95368BE442A149d")
        start_date = "2024-05-14T00:00:00+00:00"
        assert data.index[0] == pd.to_datetime(start_date)
    
    def test_history(self):
        data = Token("BTC5L").history()
        start_date = "2024-05-14T00:00:00+00:00"
        assert data.index[0] == pd.to_datetime(start_date)

if __name__ == "__main__":
    unittest.main()
