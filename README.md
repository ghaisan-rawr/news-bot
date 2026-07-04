# Crypto & Macro News Bot (100% Free)

Bot yang polling RSS + CryptoPanic tiap 30 menit, filter berita relevan (macro + crypto), lalu kirim ke Discord. Jalan otomatis pake GitHub Actions — gratis selamanya selama pemakaian wajar.

## Setup (3 menit)

### 1. Bikin Discord Webhook
1. Buka server Discord lo → pilih channel yang mau jadi tempat news masuk
2. Klik ⚙️ (Edit Channel) → **Integrations** → **Webhooks** → **New Webhook**
3. Kasih nama (misal "News Bot"), klik **Copy Webhook URL**
4. Simpan URL itu (formatnya `https://discord.com/api/webhooks/...`)

### 2. Push project ini ke GitHub repo baru
```bash
git init
git add .
git commit -m "init crypto news bot"
git remote add origin https://github.com/USERNAME/crypto-news-bot.git
git push -u origin main
```

### 3. Set Secret di GitHub repo
Buka repo → Settings → Secrets and variables → Actions → New repository secret:
- `DISCORD_WEBHOOK_URL` = webhook URL dari step 1

### 4. Selesai
Workflow otomatis jalan tiap 30 menit. Mau test langsung tanpa nunggu cron: buka tab **Actions** di repo → pilih workflow "Crypto & Macro News Bot" → klik **Run workflow**.

## Customize

- **Ganti interval**: edit `cron: "*/30 * * * *"` di `.github/workflows/news-bot.yml` (format cron standar, jangan terlalu sering < 15 menit biar sopan ke API gratis)
- **Tambah/kurang keyword**: edit list `KEYWORDS` di `bot.py`
- **Tambah RSS feed**: tambahin URL ke `RSS_FEEDS` di `bot.py`

## Kenapa gratis?

| Komponen | Layanan | Biaya |
|---|---|---|
| Scheduler | GitHub Actions | Gratis (2000 menit/bulan, run ini cuma ~30 detik) |
| Source data | RSS + CryptoPanic public API | Gratis |
| Delivery | Discord Webhook | Gratis unlimited |
| Storage state | JSON file di repo | Gratis |

## Known limitations
- CryptoPanic public endpoint kadang rate-limited kalo terlalu sering — 30 menit interval aman
- Kalo GitHub Actions minute quota abis (jarang banget buat script sesingkat ini), bisa upgrade ke self-hosted runner atau pindah ke Railway cron (ada free tier juga)
- Filter masih keyword-based, bukan AI — kadang ada false positive/negative. Upgrade ke LLM summarization gampang tinggal tambah API call di `bot.py`
