PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    asin TEXT UNIQUE,
    title TEXT NOT NULL,
    brand TEXT,
    model TEXT,
    category TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_type TEXT NOT NULL,          -- amazon_group, amazon, trendyol, hepsiburada vb.
    source_name TEXT NOT NULL,
    source_url TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS offers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    source_id INTEGER NOT NULL,
    merchant_name TEXT,
    listing_url TEXT,
    observed_price REAL NOT NULL,
    shipping_fee REAL DEFAULT 0,
    currency TEXT DEFAULT 'TRY',
    coupon_amount REAL DEFAULT 0,
    stock_status TEXT,
    observed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(product_id) REFERENCES products(id),
    FOREIGN KEY(source_id) REFERENCES sources(id)
);

CREATE TABLE IF NOT EXISTS price_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    source_id INTEGER NOT NULL,
    effective_price REAL NOT NULL,
    list_price REAL,
    discount_rate REAL,
    captured_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(product_id) REFERENCES products(id),
    FOREIGN KEY(source_id) REFERENCES sources(id)
);

CREATE TABLE IF NOT EXISTS comparisons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    amazon_offer_id INTEGER NOT NULL,
    competitor_median_price REAL,
    competitor_min_price REAL,
    delta_vs_median REAL,
    delta_vs_min REAL,
    pct_vs_30d_avg REAL,
    is_likely_real_discount INTEGER DEFAULT 0,
    computed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(product_id) REFERENCES products(id),
    FOREIGN KEY(amazon_offer_id) REFERENCES offers(id)
);

CREATE TABLE IF NOT EXISTS ai_evaluations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    comparison_id INTEGER NOT NULL,
    model_name TEXT NOT NULL,
    confidence_score REAL NOT NULL,
    decision TEXT NOT NULL,             -- real_discount | watch | ignore
    reason_summary TEXT,
    raw_features_json TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(comparison_id) REFERENCES comparisons(id)
);

CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ai_evaluation_id INTEGER NOT NULL,
    channel TEXT NOT NULL,              -- telegram, e-mail, slack vb.
    recipient TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    sent_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(ai_evaluation_id) REFERENCES ai_evaluations(id)
);

CREATE INDEX IF NOT EXISTS idx_offers_product_observed_at
ON offers(product_id, observed_at DESC);

CREATE INDEX IF NOT EXISTS idx_snapshots_product_captured_at
ON price_snapshots(product_id, captured_at DESC);

CREATE INDEX IF NOT EXISTS idx_eval_decision
ON ai_evaluations(decision, confidence_score DESC);
