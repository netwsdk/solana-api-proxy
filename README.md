# solana-api-proxy
solana RPC proxy server

Python 3.10 or above.

When use it with "squads-v4-public-ui", please set the http://localhost:8080 as the solana RPC url.

All the RPC requests of "squads-v4-public-ui" and user's browser will be forwarded to "https://api.mainnet-beta.solana.com" by this proxy.

This will fix the problem of solana RPC server rejection to user's browser.
