# Amazon Fiyat Telegram Botu (Resmi API ile)

Bu bot, Amazon ürün fiyatlarını **HTML kazıma (scraping)** yerine Amazon Product Advertising API (PA-API v5) ile çeker.
Bu yaklaşım hem daha stabil hem de engellenme riskini azaltan, kurallara uyumlu yöntemdir.

## Özellikler
- `/fiyat <ürün adı>` komutu ile ürün araması
- İlk sonuçlar için başlık, fiyat ve ürün linki
- Amazon PA-API Signature V4 imzalama desteği

## Kurulum

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

`.env` dosyasına değerlerinizi girin:

- `TELEGRAM_BOT_TOKEN`
- `AMAZON_ACCESS_KEY`
- `AMAZON_SECRET_KEY`
- `AMAZON_PARTNER_TAG`
- Opsiyonel: `AMAZON_HOST`, `AMAZON_REGION`, `AMAZON_MARKETPLACE`

## Çalıştırma

```bash
python bot.py
```

## Notlar
- Amazon tarafında PA-API erişimi ve Associates hesabı gerekir.
- Trafiği artırdıkça rate limit kurallarına uyun.
- Eğer Türkiye mağazası kullanılacaksa `AMAZON_HOST` ve `AMAZON_MARKETPLACE` değerlerini TR domainine göre güncelleyin.
