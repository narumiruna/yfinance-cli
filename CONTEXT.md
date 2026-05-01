# yfinance CLI

這個 context 描述一個終端機工具如何讓使用者查詢 Yahoo Finance 提供的金融資料。它的目的，是先把產品語言固定下來，避免把不同型態的金融資訊混成同一件事。

## Language

**Ticker**:
公開交易標的的代號，用來唯一指定查詢目標。
_Avoid_: symbol, stock code, 股票代號

**Yahoo Finance Data**:
透過 Yahoo Finance 取得的金融資料總稱，包含價格、公司資訊、新聞、財務報表、產業排行與期權資料。
_Avoid_: information, output, response

**Market Data**:
**Yahoo Finance Data** 的一個子類，專指與公開交易標的價格行為直接相關的資料，例如報價、漲跌與歷史價格。
_Avoid_: all finance data, company details, news

**Lookup**:
一次向 Yahoo Finance 請求資料的操作總稱，可以是依 **Ticker** 查詢，也可以是搜尋或排行探索。
_Avoid_: only ticker query, endpoint call, request payload

**Single-Ticker Query**:
**Lookup** 的一個子類，一次只針對一個 **Ticker** 執行的查詢操作。
_Avoid_: all lookups, watchlist lookup, batch scan

**Capability**:
一個可被介面暴露的獨立金融查詢能力，例如查報價、查新聞或查期權鏈。
_Avoid_: endpoint, tool implementation, transport

**CLI Command**:
在終端機中觸發一個 **Capability** 的使用者操作。
_Avoid_: MCP tool, endpoint, prompt

**CLI-Native Command Name**:
為終端機使用者設計的命令名稱，保留 **Capability** 邊界，但不直接沿用 MCP tool 名稱。
_Avoid_: raw MCP tool name, protocol-shaped naming

**Human-Readable Output**:
為終端機互動閱讀設計的預設輸出，重點是快速理解，並以區塊、對齊與顏色提升可讀性，不以機器解析為優先。
_Avoid_: raw JSON, protocol payload, debug dump

**JSON Output**:
為 shell 管線或其他程式消費設計的結構化輸出，透過明確旗標啟用。
_Avoid_: default output, pretty table

**Summary View**:
為互動式終端機閱讀設計的預設輸出，只呈現最重要的重點欄位。
_Avoid_: full payload, debug dump, exhaustive field list

**Verbose View**:
透過 `--verbose` 或 `-v` 展開更多欄位的人類可讀輸出，但仍不是原始 JSON。
_Avoid_: default output, machine format, hidden fields

**Command Tree**:
單一可執行檔底下的一組子命令結構，用來組織多個 **Capability**。
_Avoid_: flat alias list, unrelated binaries

**Chart Export**:
將價格歷史視覺化結果明確寫成檔案的操作，而不是直接當作終端機標準輸出。
_Avoid_: inline chart, auto-open preview, hidden side effect

**Reference Implementation**:
用來對齊能力與行為的參考專案，但目標 CLI 在執行時不依賴它。
_Avoid_: runtime dependency, wrapper layer, shared transport

## Relationships

- 一個 **Lookup** 觸發一次 Yahoo Finance 資料取得流程
- 一個 **Single-Ticker Query** 是一種 **Lookup**
- 一個 **Single-Ticker Query** 目標是恰好一個 **Ticker**
- 一個 **Single-Ticker Query** 回傳一種或多種 **Yahoo Finance Data**
- 一個 **CLI Command** 暴露恰好一個主要 **Capability**
- 同一個 **Capability** 可以透過不同介面提供，例如 MCP 或 CLI
- **Market Data** 是 **Yahoo Finance Data** 的子集合
- 一個 **CLI Command** 應使用 **CLI-Native Command Name** 來表達其主要 **Capability**
- 一個 **CLI Command** 預設回傳 **Human-Readable Output**
- 一個 **CLI Command** 的預設 **Human-Readable Output** 應為 **Summary View**
- 使用者可透過 `--verbose` 或 `-v` 切換到 **Verbose View**
- 使用者可透過旗標要求 **JSON Output**
- CLI 介面以單一 **Command Tree** 暴露多個 **Capability**
- 需要視覺化時，**CLI Command** 應執行 **Chart Export**，而不是把圖表塞進標準輸出
- 一個 **CLI Command** 可以對齊 **Reference Implementation** 的能力，但直接以 `yfinance` 完成查詢

## Example dialogue

> **Dev:** 「這個 CLI 查的是價格資料，還是所有 Yahoo Finance 能給的資料？」
> **Domain expert:** 「CLI v1 的總稱是 **Yahoo Finance Data**；其中 **Market Data** 只是其中一類，不再代表全部。」

> **Dev:** 「`search` 和 `top` 也算查詢嗎？它們又不是查單一 ticker。」
> **Domain expert:** 「它們都算 **Lookup**；只是只有一部分 **Lookup** 會是 **Single-Ticker Query**。」

> **Dev:** 「既然參考的是 `yfinance-mcp`，CLI 是不是只是換個包裝？」
> **Domain expert:** 「不是直接照搬 transport；我們先確認每個 **Capability** 是否值得變成一個 **CLI Command**。」

> **Dev:** 「CLI 命令名稱要不要直接叫 `yfinance_get_ticker_info` 這種 MCP 名稱？」
> **Domain expert:** 「不要；同一個 **Capability** 可以一對一保留，但命名要改成 **CLI-Native Command Name**，例如 `info` 或 `history`。」

> **Dev:** 「CLI 預設要吐 JSON 嗎？」
> **Domain expert:** 「不用；預設給 **Human-Readable Output**，只有在需要管線處理時才切成 **JSON Output**。」

> **Dev:** 「所謂給人看的輸出，是簡單純文字，還是像正式 CLI 工具那樣有版面？」
> **Domain expert:** 「是有版面的 **Human-Readable Output**；它可以用區塊、對齊與顏色幫助閱讀。」

> **Dev:** 「那預設是把所有欄位都攤開嗎？」
> **Domain expert:** 「不是；預設先給 **Summary View**，需要更多再用 `--verbose` 或 `-v` 看 **Verbose View**，完整資料才交給 JSON。」

> **Dev:** 「`options` 這類能力要平鋪成 `options-chain`，還是收在同一棵命令樹？」
> **Domain expert:** 「收進單一 **Command Tree**，像 `options dates` 和 `options chain` 這樣自然分組。」

> **Dev:** 「歷史價格的圖表在 CLI 裡要怎麼回傳？」
> **Domain expert:** 「保留圖表能力，但它必須是明確的 **Chart Export**，例如寫到使用者指定的檔案。」

> **Dev:** 「既然會參考 `yfinance-mcp`，CLI 需要直接依賴它嗎？」
> **Domain expert:** 「不用；`yfinance-mcp` 只是 **Reference Implementation**，CLI 直接用 `yfinance` 實作。」

## Flagged ambiguities

- 「資訊」曾被模糊地拿來指很多東西，現已固定為 **Yahoo Finance Data** 作為 CLI v1 的總稱；**Market Data** 僅指價格相關子類。
- 「查詢」曾被拿來同時指單一 ticker 查詢與搜尋/排行探索，現已拆成總稱 **Lookup** 與子類 **Single-Ticker Query**。
- 「CLI 版本」容易被誤解成直接複製 MCP 協定，現已拆成 **Capability** 與 **CLI Command** 兩個概念。
- 「CLI 版本」不是 MCP tool 名稱的字面搬運；現已固定採用 **CLI-Native Command Name**。
- 預設輸出不是原始資料傾倒；現已固定為 **Human-Readable Output**，並以旗標切換到 **JSON Output**。
- 預設的人類可讀輸出不是全部欄位展開；現已固定為 **Summary View**，並用 `--verbose` / `-v` 切換到 **Verbose View**。
- 命令結構不是多個分散 binary；現已固定為單一 **Command Tree**。
- 圖表能力不是 stdout 內容；現已固定為明確的 **Chart Export**。
- 「參考 `yfinance-mcp`」不代表 runtime 依賴；現已固定為 **Reference Implementation**，CLI 直接使用 `yfinance`。
- 「給人看」不是極簡文字清單；現已固定為有版面的 **Human-Readable Output**。
