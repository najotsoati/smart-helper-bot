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
| **AI kadr tanlash** | Har sahna uchun 6 tagacha stok video topiladi, Claude ularning rasmlariga qarab eng mos va dramatigini tanlaydi. Birinchi kadr eng kuchlisi bo'ladi. |
| **Infografika** | Raqamlar ekranda sanalib chiqadi, taqqoslashlar o'sib boradigan ustunlar bilan ko'rsatiladi (masalan, Everest va Mariana chuqurligi). |
| **Faktlarni tekshirish** | Claude har bir faktni internetdan tekshiradi, xatolarini to'g'rilaydi va manbasini ko'rsatadi. |
| **Twist** | Twist oldidan riser, twist paytida bass drop va kuchliroq zoom, raqamlarda "ding". |
| **Kayfiyatli musiqa** | Ssenariy kayfiyatiga mos trek tanlanadi (`assets/music/<kayfiyat>/`). |
| **Trend tahlili** | YouTube'da kanal o'rtachasidan ancha ko'p ko'rilayotgan Shorts topiladi va g'oyalar shularga qarab beriladi. |
| **Seriya** | "Ocean Facts #3" kabi belgi video boshida va sarlavhada chiqadi. |
| **Sifat** | Yakuniy eksport: x264 high, CRF 18. YouTube qayta siqqandan keyin ham tiniq qoladi. |
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
| `ELEVENLABS_API_KEY` | yo'q | https://elevenlabs.io. Eng jonli ovoz shu. Microsoft ovozlari har doim ro'yxatda qoladi. |
| `YOUTUBE_API_KEY` | yo'q | https://console.cloud.google.com, "YouTube Data API v3" (bepul). "Trenddagi Shorts" tugmasi uchun kerak. |

Fon musiqasi kerak bo'lsa, `assets/music/` papkasiga mualliflik huquqisiz `.mp3` fayllarni tashlang (kayfiyat bo'yicha papkalar: [assets/music/README.md](assets/music/README.md)).
Haqiqiy ovoz effektlari kerak bo'lsa, ularni `assets/sfx/` papkasiga tashlang: [assets/sfx/README.md](assets/sfx/README.md).

## Ishga tushirish

```bash
uvicorn app:app --reload
```

Brauzerda http://127.0.0.1:8000 manzilini oching. Keyin:

1. **Trenddagi Shorts** tugmasi nishangizda hozir nima ko'rilayotganini ko'rsatadi. **Viral g'oyalar topish** tugmasi shularga asoslanib mavzu taklif qiladi. Mavzuni o'zingiz ham yozishingiz mumkin.
2. **Ssenariy yozish**: faktlar tekshiruvi natijasini ko'rib chiqing, hookni tanlang, kerak bo'lsa matnni, video qidiruv so'zlarini, sarlavhalarni va twist sahnasini tahrirlang.
3. **Video yasash**: ovoz, tezlik va seriya nomini tanlang. 2–4 daqiqada tayyor MP4 chiqadi, sarlavha va heshteglar bilan birga.

Terminaldan ham ishlatsa bo'ladi:

```bash
python cli.py "the deepest point of the ocean" --series "Ocean Facts #1"
python cli.py --offline          # kalitsiz sinov: namuna ssenariy, ovozsiz
```

Tayyor videolar `output/` papkasiga saqlanadi.

## Ko'proq ko'rish uchun maslahatlar

- Kuniga 1–3 ta video joylang, bitta mavzu yo'nalishida qoling.
- Bitta ovozda qoling, u kanalingiz brendiga aylanadi.
- 30–35 soniyalik videolar odatda uzunlariga qaraganda oxirigacha ko'proq ko'riladi.
- Pastki 20% va o'ng chetni YouTube tugmalari yopadi. Panel matnni shu joylardan uzoqda joylashtiradi.
- Birinchi 24 soatdan keyin YouTube Studio'da **"Viewed vs swiped away"** ko'rsatkichini tekshiring. 70% dan past bo'lsa, hook zaif.
- Eng ko'p ko'rilgan videongiz mavzusida 3–5 ta davomini qiling.
