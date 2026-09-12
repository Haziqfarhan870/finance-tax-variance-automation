# Architecture

```text
Synthetic ERP-style extracts
        |
        v
Column normalization + subtotal removal + exact deduplication
        |
        v
Account mapping + unmapped-account detection
        |
        +---------------------------+
        |                           |
        v                           v
PNL period activity            BS closing balances
(GL quarter sums)              (TB preferred; GL fallback)
        |                           |
        +-------------+-------------+
                      v
          QoQ / % / YTD / trend / materiality
                      |
                      v
        deterministic comments + account insight
                      |
                      v
   PNL Summary + PNL Quarterly + BS Summary + BS Quarterly
                      |
                      v
       reviewer status dropdown + completion tracking
```

The public implementation uses fictional identifiers and YAML configuration. The original workflow used employer-specific mappings and file structures that are not reproduced here.
