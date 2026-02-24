 (cd "$(git rev-parse --show-toplevel)" && git apply --3way <<'EOF' 
diff --git a/README.md b/README.md
new file mode 100644
index 0000000000000000000000000000000000000000..522d86163a2b57baa47755560b8ee6ae2226b20f
--- /dev/null
+++ b/README.md
@@ -0,0 +1,64 @@
+# AI Destekli İndirim Analiz Sistemi
+
+Bu proje, **Amazon gruplarında paylaşılan indirimleri otomatik toplayıp** ürün fiyatını diğer pazaryerleriyle kıyaslayarak bunun gerçek indirim olup olmadığını analiz eder.
+
+## Hedefler
+
+- Amazon grup postlarından ürün bilgisi çıkarma
+- Ürünün farklı sitelerdeki güncel fiyatını toplama
+- Geçmiş fiyat ile karşılaştırma yapma
+- AI destekli "gerçek indirim" skoru üretme
+- Gerçek indirimleri anlık bildirim olarak gönderme
+
+## Mimari Akış
+
+1. **Collector**: Amazon grup mesajlarını toplar (Telegram/Discord/WhatsApp API entegrasyonu).
+2. **Extractor**: Mesaj içinden URL, ürün adı, ASIN, görülen fiyatı çıkarır.
+3. **Crawler**: Aynı ürünü diğer e-ticaret sitelerinde arar ve fiyatlarını alır.
+4. **Price Normalizer**: Fiyatları para birimi, kargo ve kupon etkisine göre normalize eder.
+5. **AI Analyzer**: LLM + kural motoru ile indirim doğruluğunu skorlar.
+6. **Alert Service**: Eşik değerin üstündeki indirimleri kullanıcıya bildirir.
+
+## Veri Şeması
+
+Veritabanı yapısı `schema.sql` dosyasında yer alır.
+
+Temel varlıklar:
+
+- `products`: Ürün ana kaydı (ASIN, marka, model)
+- `offers`: Belirli bir kaynaktan gelen anlık teklif
+- `price_snapshots`: Zaman serisi fiyat geçmişi
+- `comparisons`: Amazon fiyatı vs diğer siteler kıyası
+- `ai_evaluations`: LLM tabanlı indirim doğrulaması
+- `alerts`: Kullanıcıya gönderilen bildirimler
+
+## Hızlı Başlangıç
+
+```bash
+python3 -m venv .venv
+source .venv/bin/activate
+pip install -r requirements.txt
+python app/discount_analyzer.py --init-db --db-path data/discounts.db
+```
+
+## AI Karar Mantığı (Örnek)
+
+Sistem aşağıdaki sinyalleri birleştirir:
+
+- Son 30 gün ortalama fiyatına göre düşüş yüzdesi
+- Diğer sitelerdeki medyan fiyata göre fark
+- Stok, satıcı puanı, sahte indirim riski
+- Kampanya tipi (kupon, sepet indirimi, lightning deal)
+
+Örnek karar:
+
+- **Skor >= 0.80** → Gerçek indirim, bildirim gönder
+- **0.60 - 0.79** → İzlemeye al
+- **< 0.60** → Bildirim gönderme
+
+## Sonraki Adımlar
+
+- Gerçek kaynak konektörlerinin eklenmesi
+- Ürün eşleme (entity resolution) iyileştirme
+- LLM prompt ve değerlendirme veri seti ile model kalibrasyonu
+- Dashboard (FastAPI + React) ile canlı izleme
 
EOF
)
