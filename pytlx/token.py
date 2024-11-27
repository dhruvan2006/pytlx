from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List, Optional
import requests
import pandas as pd
from pytlx.utils import validate_date_format
from web3 import Web3

class Token:
    """
    A class to represent a leveraged token on TLX.
    """
    BASE_URL = "https://api.tlx.fi/functions/v1/prices/"
    OPTIMISM_RPC_URL = "https://mainnet.optimism.io"
    CONTRACT_ADDRESS = "0x8E61715363435d40B0Dbb35524a03517b9d8d01D"
    CONTRACT_ABI = [{"inputs":[{"internalType":"address","name":"addressProvider_","type":"address"}],"stateMutability":"nonpayable","type":"constructor"},{"inputs":[{"internalType":"uint256","name":"offset_","type":"uint256"},{"internalType":"uint256","name":"limit_","type":"uint256"}],"name":"leveragedTokenData","outputs":[{"components":[{"internalType":"address","name":"addr","type":"address"},{"internalType":"string","name":"symbol","type":"string"},{"internalType":"uint256","name":"totalSupply","type":"uint256"},{"internalType":"string","name":"targetAsset","type":"string"},{"internalType":"uint256","name":"targetLeverage","type":"uint256"},{"internalType":"bool","name":"isLong","type":"bool"},{"internalType":"bool","name":"isActive","type":"bool"},{"internalType":"uint256","name":"rebalanceThreshold","type":"uint256"},{"internalType":"uint256","name":"exchangeRate","type":"uint256"},{"internalType":"bool","name":"canRebalance","type":"bool"},{"internalType":"bool","name":"hasPendingLeverageUpdate","type":"bool"},{"internalType":"uint256","name":"remainingMargin","type":"uint256"},{"internalType":"uint256","name":"leverage","type":"uint256"},{"internalType":"uint256","name":"assetPrice","type":"uint256"},{"internalType":"uint256","name":"userBalance","type":"uint256"}],"internalType":"struct LeveragedTokenHelper.LeveragedTokenData[]","name":"","type":"tuple[]"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"user_","type":"address"},{"internalType":"uint256","name":"offset_","type":"uint256"},{"internalType":"uint256","name":"limit_","type":"uint256"}],"name":"leveragedTokenData","outputs":[{"components":[{"internalType":"address","name":"addr","type":"address"},{"internalType":"string","name":"symbol","type":"string"},{"internalType":"uint256","name":"totalSupply","type":"uint256"},{"internalType":"string","name":"targetAsset","type":"string"},{"internalType":"uint256","name":"targetLeverage","type":"uint256"},{"internalType":"bool","name":"isLong","type":"bool"},{"internalType":"bool","name":"isActive","type":"bool"},{"internalType":"uint256","name":"rebalanceThreshold","type":"uint256"},{"internalType":"uint256","name":"exchangeRate","type":"uint256"},{"internalType":"bool","name":"canRebalance","type":"bool"},{"internalType":"bool","name":"hasPendingLeverageUpdate","type":"bool"},{"internalType":"uint256","name":"remainingMargin","type":"uint256"},{"internalType":"uint256","name":"leverage","type":"uint256"},{"internalType":"uint256","name":"assetPrice","type":"uint256"},{"internalType":"uint256","name":"userBalance","type":"uint256"}],"internalType":"struct LeveragedTokenHelper.LeveragedTokenData[]","name":"","type":"tuple[]"}],"stateMutability":"view","type":"function"}]

    def __init__(self, ticker: str) -> None:
        """
        Initialize the Token with a ticker string.

        :param ticker: str: The token's ticker (e.g., "BTC5L").
        """
        self.ticker: str = ticker
    
    def _fetch_leveraged_token_data(self, contract, offset: int, limit: int) -> List[Dict[str, Any]]:
        """
        Fetch leveraged token data from the smart contract.

        :param contract: Web3 contract instance.
        :param offset: int: Offset for pagination.
        :param limit: int: Number of items to fetch per batch.
        :return: List[Dict]: Leveraged token data.
        """
        return contract.functions.leveragedTokenData(offset, limit).call()
    
    def get_contract_addresses(self) -> List[Dict[str, Any]]:
        """
        Fetch all contract addresses and related metadata from the smart contract.

        :return: List[Dict]: List of contract address data.
        """
        web3 = Web3(Web3.HTTPProvider(self.OPTIMISM_RPC_URL))
        if not web3.is_connected():
            raise Exception("Failed to connect to Optimism network.")    

        contract = web3.eth.contract(
            address=web3.to_checksum_address(self.CONTRACT_ADDRESS),
            abi=self.CONTRACT_ABI
        )

        batch_size = 25
        start_offset = 0
        end_offset = 100
        all_results = []

        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_offset = {
                executor.submit(self._fetch_leveraged_token_data, contract, offset, batch_size): offset
                for offset in range(start_offset, end_offset, batch_size)
            }

            for future in as_completed(future_to_offset):
                try:
                    result = future.result()
                    all_results.extend(result)
                except Exception as e:
                    raise RuntimeError(f"Error fetching batch: {e}")
        
        return all_results
    
    def get_contract_address(self) -> Optional[str]:
        """
        Get the contract address for the given ticker.

        :return: str or None: Contract address if found, else None.
        """
        addresses = self.get_contract_addresses()
        for address, ticker, *_ in addresses:
            if ticker == self.ticker:
                return address
        return None
    
    def _history_contract_address(self, contract_address: str, granularity: str = "1d", start: str = "1900-01-01") -> pd.DataFrame:
        """
        Fetch historical price data from the TLX API for a given contract address.

        :param contract_address: str: The smart contract address.
        :param granularity: str: Data granularity (e.g., "1d").
        :param start: str: Start date in "YYYY-MM-DD" format.
        :return: pd.DataFrame: Historical prices with Date as the index.
        """
        query = f"?granularity={granularity}&from=${start}"
        url = self.BASE_URL + contract_address + query
        
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        df = pd.DataFrame(data).rename(columns={
            "timestamp": "Date",
            "price": "Price"
        })
        
        df["Date"] = pd.to_datetime(df["Date"])
        df.set_index("Date", inplace=True)
        
        return df
    
    def history(self, granularity: str = "1d", start: str = "1900-01-01") -> pd.DataFrame:
        """
        Fetch historical price data for the token.

        :param granularity: str: Data granularity (e.g., "6h").
        :param start: str: Start date in "YYYY-MM-DD" format.
        :return: pd.DataFrame: Historical price data.
        """
        validate_date_format(start)

        address = self.get_contract_address()
        if address is None:
            raise ValueError(f"Invalid ticker '{self.ticker}'")

        return self._history_contract_address(address, granularity=granularity, start=start)
