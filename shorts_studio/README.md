# 🎬 Shorts Studio

Qiziqarli faktlar haqida inglizcha **YouTube Shorts / Reels / TikTok** videolarini avtomatik yasaydigan panel.

Oddiy "rasm + robot ovoz" videolaridan farqi: har bir video ko'rishni ushlab qolish qoidalari bo'yicha quriladi.

| Nima | Qanday |
|---|---|
| **Hook** | Claude 3 xil hook yozadi, siz eng kuchlisini tanlaysiz. Salomlashish ham, "Did you know" ham yo'q. |
| **Ssenariy** | Har bir gap keyingisiga qiziqtiradi (open loop), faktlar tobora kuchliroq bo'lib boradi. Oxirgi gap hookka ulanib ketadi (loop). |
| **Tez montaj** | Kadr har 2–3 soniyada almashadi, kesishda "punch" zoom va sekin kamera harakati bor. |
| **Subtitr** | Katta harflar, aytilayotgan so'z sariq rangda "sakraydi", raqamlar va asosiy so'zlar yashil. |
| **Ekrandagi sarlavhalar** | "11 KM DEEP" kabi sariq qutili sarlavhalar. |
| **Ovoz dizayni** | Har kesishda whoosh, boshida impact, musiqa ovoz chiqqanda o'zi pasayadi, ovoz balandligi -14 LUFS. |
| **Progress bar** | Pastdagi sariq chiziq odamni oxirigacha ko'rishga undaydi. |
| **Metadata** | Sarlavha, tavsif, heshteglar va pin qilinadigan izoh tayyor bo'ladi. |

## O'rnatish

Kerak bo'ladi: **Python 3.10+** va **ffmpeg** (`ffmpeg -version` ishlashi kerak).

```bash
cd shorts_studio
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # keyin .env ichiga kalitlarni yozing
```

| Kalit | Majburiymi | Qayerdan olinadi |
|---|---|---|
| `ANTHROPIC_API_KEY` | ha | https://console.anthropic.com |
| `PEXELS_API_KEY` | ha (bo'lmasa fon rangli gradient bo'ladi) | https://www.pexels.com/api/ (bepul) |
| `ELEVENLABS_API_KEY` | yo'q | https://elevenlabs.io. Eng jonli ovoz shu. Kalit bo'lmasa bepul Microsoft ovozlari ishlatiladi. |

Fon musiqasi kerak bo'lsa, `assets/music/` papkasiga mualliflik huquqisiz `.mp3` fayllarni tashlang.

## Ishga tushirish

```bash
uvicorn app:app --reload
```

Brauzerda http://127.0.0.1:8000 manzilini oching. Keyin:

1. **Viral g'oyalar topish** tugmasini bosing yoki mavzuni o'zingiz yozing.
2. **Ssenariy yozish**: hookni tanlang, kerak bo'lsa matnni, video qidiruv so'zlarini va sarlavhalarni tahrirlang.
3. **Video yasash**: ovozni tanlang. 1–3 daqiqada tayyor MP4 chiqadi, sarlavha va heshteglar bilan birga.

Terminaldan ham ishlatsa bo'ladi:

```bash
python cli.py "the deepest point of the ocean" --seconds 45
python cli.py --offline          # kalitsiz sinov: namuna ssenariy, ovozsiz
```

Tayyor videolar `output/` papkasiga saqlanadi.

## Ko'proq ko'rish uchun maslahatlar

- Kuniga 1–3 ta video joylang, bitta mavzu yo'nalishida qoling.
- Birinchi 24 soatdan keyin YouTube Studio'da **"Viewed vs swiped away"** ko'rsatkichini tekshiring. 70% dan past bo'lsa, hook zaif.
- Eng ko'p ko'rilgan videongiz mavzusida 3–5 ta davomini qiling.
