# Market Data Connector Agents

**Total: 27 new market data connectors**

## **Exchanges (15):**
1. alphavantage - Stock, forex, crypto data
2. binance - Already created ✅
3. binanceus - Binance US
4. bitfinex - Crypto exchange
5. bitget - Crypto derivatives
6. bithumb - Korean crypto exchange
7. bitstamp - European crypto exchange
8. bybit - Crypto derivatives
9. coinbase - Already created ✅
10. deribit - Crypto options/futures
11. ftx - Defunct (FTX collapse)
12. ftxus - Defunct (FTX US)
13. gateio - Crypto exchange
14. gemini - Crypto exchange
15. huobi - Crypto exchange
16. kraken - Already created ✅
17. kucoin - Crypto exchange
18. okx - Crypto exchange (formerly OKEx)
19. phemex - Crypto derivatives
20. upbit - Korean crypto exchange

## **Market Data Providers (7):**
21. databento - Institutional market data
22. finnhub - Stock/forex/crypto data
23. polygon - Real-time & historical market data
24. tradier - Brokerage & market data
25. twelvedata - Financial data API
26. collectors - Data aggregation
27. dex_collector - DEX data collection

## **Implementation Plan:**
- Create lightweight connector agents for each
- Focus on authentication, common queries, and rate limits
- Group by category in apolloAgents.ts
