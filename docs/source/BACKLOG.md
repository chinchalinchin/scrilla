# Scrilla Modernization Backlog

## Sprint Board

### Open 

| Status | Category | Item | Description |
| :--- | :--- | :--- | :--- |
| **TODO** | Services | Replace IEX Dividend API | The IEX API is no longer free. Transition `DividendManager` to a free alternative like `yfinance` to retrieve historical dividend data. |
| **TODO** | Services | Modernize US Treasury API | Replace the brittle XML scraping and manual `while True` pagination in `StatManager` with the modern, free JSON API provided by `fiscaldata.treasury.gov`. |
| **TODO** | Services | Verify AlphaVantage Crypto | AlphaVantage crypto endpoints frequently change their schema. Verify `DIGITAL_CURRENCY_DAILY` functionality and migrate to `yfinance` or CoinGecko if the free tier rate limits (25/day) prove too restrictive. |
| **TODO** | Bugs | Fix Singleton Initialization | `cache.py` uses `__call__` for Singletons but executes `__init__` upon every request, resetting state and triggering redundant DB table checks. Modify the metaclass to execute `__init__` only on the first instantiation. |
| **TODO** | Bugs | Remove Math Hack in Estimators | `sample_correlation` in `estimators.py` attempts to bypass division by zero using `exp(log(A/B))`. Remove this complex plane hack and use standard zero-division handling. |
| **TODO** | Bugs | Resolve PySide Redundancy | `requirements.txt` and `setup.cfg` mandate both `PySide2` and `PySide6`. Matplotlib >= 3.5 fully supports PySide6. Remove PySide2 completely to eliminate bloat and conflicts. |
| **TODO** | Bugs | DynamoDB Sorting | The DynamoDB PartiQL queries lack an `ORDER BY` clause, causing out-of-order date retrieval. Implement application-side sorting consistently across all DynamoDB retrieval methods or migrate to standard `boto3` queries. |
| **TODO** | Inefficiencies | CLI Routing | `main.py` uses massive `if/elif` blocks with redundant module imports to handle CLI commands. Replace this entirely with `Click` or `Typer` for clean, modular CLI routing. |
| **TODO** | Inefficiencies | Redundant Price Calls | `main.py` recalculates `prices` repeatedly inside command blocks instead of abstracting the retrieval logic to a shared decorator or dependency injection. |
| **TODO** | Inefficiencies | In-Memory Cache Leaks | `internal_cache` dictionaries in `cache.py` grow indefinitely without an eviction policy (e.g., LRU). Implement a maximum size limit to prevent memory leaks during long-running GUI sessions. |
| **TODO** | Inefficiencies | Iterative Symbol Parsing | `files.get_overlapping_symbols` parses static lists repeatedly. Calculate the intersection of `STATIC_TICKERS_FILE` and `STATIC_CRYPTO_FILE` once on startup and cache the result. |
| **TODO** | Refactor | Extract Raw SQL | Abstract the raw SQL strings strewn throughout `cache.py` by implementing an ORM like `SQLAlchemy` to handle SQLite safely and cleanly. |
| **TODO** | Refactor | Strategy Pattern for Services | `StatManager` and `PriceManager` rely on `if/elif` blocks to determine the active data service. Refactor to use Abstract Base Classes (ABCs) and the Strategy pattern for better extensibility. |
| **TODO** | Refactor | Date Handling | Standardize date handling using Python's `datetime` natively. Remove repetitive `dater.parse` and `dater.to_string` conversions across the analysis modules. |
| **TODO** | General | Build Modernization | Update `pyproject.toml` and `setup.cfg` to target modern Python versions (>= 3.10) and migrate entirely to standard PEP 621 `pyproject.toml` configurations. |
| **TODO** | General | Standardize Logging | Replace the custom `outputter.Logger` with Python's standard `logging` library or a modern alternative like `Loguru`. |
| **TODO** | Architecture | Relocate Application State | The application currently writes dynamic state data (`memory.json`, caches) directly into `site-packages`. Refactor to store user data and cache in a standard user directory (e.g., `~/.scrilla/` or `XDG_DATA_HOME`). |
| **TODO** | Services | Replace AlphaVantage | The AV free tier's 25 requests/day limit breaks portfolio correlation logic. Migrate `PriceManager` to `yfinance` to allow unlimited, keyless, bulk historical data retrieval. |

### Closed

| Status | Category | Item | Description |
| :--- | :--- | :--- | :--- |
| **RESOLVED** | Bugs | AlphaVantage Rate Limit | AV strictly enforces a 1 request/second limit on free tiers. Added a hard `time.sleep(2)` in `PriceManager.get_prices` to prevent immediate API rejection. |

---

## Technical Debt Notes

### 1. Service Interfaces

Relying on deprecated or shifting APIs causes the most immediate friction. `IEX` is no longer a viable free option for dividends, and parsing the US Treasury RSS feed via XML is highly fragile. Prioritize swapping these data sources to ensure the optimization algorithms have reliable data to process. 

### 2. Bugs and Issues

The `Singleton` metaclass implementation is fundamentally broken because it triggers `__init__` on every call, executing redundant logic. Fixing this will immediately speed up the application. Additionally, resolving the PySide2/PySide6 conflict will make the GUI installation much cleaner.

### 3. Inefficiencies

The lack of an LRU policy on internal memory dicts and the repetitive parsing of massive static CSVs (equities vs. crypto) causes unnecessary CPU cycles. Caching static data intersections on startup will eliminate this bottleneck.

### 4. Refactoring Opportunities

`main.py` is currently a monolithic file handling too much responsibility. Moving to a framework like `Click` will allow each command to live in its own isolated function or module. Furthermore, utilizing ORMs instead of raw SQL strings will secure the application against injection and make the database layer portable.