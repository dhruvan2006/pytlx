# PyTLX

Download leveraged token data from [TLX Fi](https://tlx.fi)

[![codecov](https://codecov.io/gh/dhruvan2006/pytlx/graph/badge.svg?token=GVWV3STI3C)](https://codecov.io/gh/dhruvan2006/pytlx)
[![PyPI Version](https://img.shields.io/pypi/v/pytlx)](https://github.com/dhruvan2006/pytlx)
[![License](https://img.shields.io/github/license/dhruvan2006/pytlx)](https://github.com/dhruvan2006/pytlx)

## Installation

Install PyTLX using pip:
```bash
pip install pytlx
```

## Quick Start

### Example Usage
```python
import pytlx as tlx

# Initialize a token by its ticker
token = tlx.Token("BTC5L")

# Fetch historical data for the token
data = token.history()
print(data)
```

# API Documentation

## Token Class

### Description
The `Token` class provides a Python interface for interacting with the TLX platform, fetching token data, contract information, and historical prices.

---

### Initialization

#### `Token(ticker: str)`
- **Parameters**:
  - `ticker` (str): The token's identifier (e.g., `BTC5L`).
- **Description**:
  Initializes the `Token` object for fetching leveraged token data.

---

### Methods

#### `get_contract_addresses() -> List[Dict[str, Any]]`
- **Description**:
  Fetches all leveraged token contract addresses and related metadata from the smart contract on the Optimism blockchain.
- **Returns**:
  A list of dictionaries containing contract address data:
  - `addr` (str): Contract address.
  - `symbol` (str): Token symbol.
  - Other metadata fields as provided by the contract.

---

#### `get_contract_address() -> Optional[str]`
- **Description**:
  Retrieves the specific contract address associated with the initialized token's ticker.
- **Returns**:
  - `str`: Contract address if the ticker is found.
  - `None`: If the ticker does not exist in the metadata.

---

#### `history(granularity: str = "1d", start: str = "1900-01-01") -> pd.DataFrame`
- **Description**:
  Fetches historical price data for the token using the TLX API.
- **Parameters**:
  - `granularity` (str): Data interval (e.g., `1d`, `6h`).
  - `start` (str): Start date in `YYYY-MM-DD` format (default: `"1900-01-01"`).
- **Returns**:
  A `pandas.DataFrame` with the following columns:
  - `Date`: The timestamp of the data point (index).
  - `Price`: The historical price of the token.

- **Raises**:
  - `ValueError`: If the ticker is invalid.
  - `HTTPError`: If the API call fails.

---

#### `get_contract_addresses() -> List[Dict[str, Any]]`
- **Description**:
  Retrieves all contract addresses and metadata for leveraged tokens by interacting with the Optimism smart contract.
- **Returns**:
  A list of dictionaries with details:
  - `addr` (str): Token contract address.
  - `symbol` (str): Token ticker.
  - Additional metadata like `totalSupply`, `targetLeverage`, and `isActive`.
