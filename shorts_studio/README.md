# 🎬 Shorts Studio

Qiziqarli faktlar haqida inglizcha **YouTube Shorts / Reels / TikTok** videolarini avtomatik yasaydigan panel.

> **Birinchi marta ishga tushiryapsizmi?** [BOSHLASH.md](BOSHLASH.md) qo'llanmasini oching: noutbukda qadam-baqadam o'rnatish.

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
| **Maskot "Fakti"** | Multfilm personaj hookni, twistni va oxirgi gapni o'zi aytadi: og'zi ovozga qarab qimirlaydi, ko'zini qisadi, twistda hayron bo'ladi. Faktlar paytida burchakda kichik dumaloq nishonda turadi. |
| **AI chizmalar** | Kamera bilan olib bo'lmaydigan faktlar (tana ichi, koinot, tarix) bir xil uslubdagi maxsus chizmalar bilan ko'rsatiladi. |
| **Kamida 80% moslik** | Har bir kadrni Claude ko'rib, matnga mosligini 0–100 ball bilan baholaydi. 80% dan past chizma yaxshilangan tavsif bilan qayta chiziladi, mos stok video topilmasa sahna chizmaga o'tadi. Natija panelda har sahna bo'yicha ko'rsatiladi. |
| **AI kadr tanlash** | Har sahna uchun 6 tagacha stok video topiladi, Claude ularning rasmlariga qarab eng mos va dramatigini tanlaydi. Birinchi kadr eng kuchlisi bo'ladi. |
| **Infografika** | Raqamlar ekranda sanalib chiqadi, taqqoslashlar o'sib boradigan ustunlar bilan ko'rsatiladi (masalan, Everest va Mariana chuqurligi). |
| **Faktlarni tekshirish** | Claude har bir faktni internetdan tekshiradi, xatolarini to'g'rilaydi va manbasini ko'rsatadi. |
| **Twist** | Twist oldidan riser, twist paytida bass drop va kuchliroq zoom, raqamlarda "ding". |
| **Kayfiyatli musiqa** | Ssenariy kayfiyatiga mos trek tanlanadi (`assets/music/<kayfiyat>/`). |
| **Trend tahlili** | YouTube'da kanal o'rtachasidan ancha ko'p ko'rilayotgan Shorts topiladi va g'oyalar shularga qarab beriladi. |
| **Seriya** | "Ocean Facts #3" kabi belgi video boshida va sarlavhada chiqadi. |
| **Sifat** | Yakuniy eksport: x264 high, CRF 18. YouTube qayta siqqandan keyin ham tiniq qoladi. |
| **Metadata** | Sarlavha, tavsif, heshteglar va pin qilinadigan izoh tayyor bo'ladi. |
| **Maskot ifodalari** | Fakti sahnaga qarab xursand, hayron, qo'rqqan bo'ladi yoki "qarang!" deb ko'rsatadi. |
| **Jonli chizmalar** | Chizmalarda zoom, chapga yoki o'ngga surilish, pastdan yuqoriga ko'tarilish va yengil titrash bor. |
| **A/B hook** | Bitta videoning ikkinchi hook bilan varianti ham yasaladi (`video_b.mp4`). Qo'shimcha chizma xarajati yo'q. |
| **Ommaviy rejim** | Mavzular ro'yxatini berasiz, panel ularni navbat bilan o'zi tayyorlaydi va kerak bo'lsa rejalashtiradi. |
| **YouTube'ga yuklash** | Panel videoni kanalga o'zi yuklaydi yoki belgilangan vaqtga rejalashtiradi. |
| **Natijalardan o'rganish** | YouTube statistikasi (o'tkazib yubormay ko'rganlar ulushi, ko'rilganlik foizi, ko'rishlar) yig'iladi. Claude qaysi hook va mavzular ishlaganini tahlil qilib, kanal uchun qo'llanma yozadi. Keyingi ssenariylar shu qo'llanmaga tayanib yoziladi. |
| **Ishonchlilik** | Barcha ishlar bazada saqlanadi, server qayta ishga tushsa navbat davom etadi. Tarmoq xatolarida avtomatik qayta urinish bor. "Tizim" bo'limida har bir kalitni bitta tugma bilan tekshirasiz. |

## O'rnatish

Kerak bo'ladi: **Python 3.10+** va **ffmpeg** (`ffmpeg -version` ishlashi kerak).

```bash
cd shorts_studio
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Kalitlarni panelning o'zida kiritasiz: **Tizim → API kalitlari** bo'limida kalitni qo'yib, **Saqlash** tugmasini bosing. Kalit darhol ishlay boshlaydi va avtomatik tekshiriladi. Xohlasangiz, `.env.example` faylidan nusxa olib, `.env` faylini qo'lda ham to'ldirishingiz mumkin.

| Kalit | Majburiymi | Qayerdan olinadi |
|---|---|---|
| `ANTHROPIC_API_KEY` | ha | https://console.anthropic.com |
| `PEXELS_API_KEY` | ha (bo'lmasa fon rangli gradient bo'ladi) | https://www.pexels.com/api/ (bepul) |
| `ELEVENLABS_API_KEY` | yo'q | https://elevenlabs.io. Eng jonli ovoz shu. Microsoft ovozlari har doim ro'yxatda qoladi. |
| `OPENAI_API_KEY` | tavsiya | https://platform.openai.com. AI chizmalar uchun (bir video ~$0.3–0.7). Bo'lmasa faqat stok video ishlatiladi. |
| `YOUTUBE_API_KEY` | yo'q | https://console.cloud.google.com, "YouTube Data API v3" (bepul). "Trenddagi Shorts" tugmasi uchun kerak. |

Fon musiqasi kerak bo'lsa, `assets/music/` papkasiga mualliflik huquqisiz `.mp3` fayllarni tashlang (kayfiyat bo'yicha papkalar: [assets/music/README.md](assets/music/README.md)).
O'z personajingizni ishlatmoqchi bo'lsangiz, `assets/mascot/` ichidagi PNG'larni xuddi shu nomlar bilan almashtiring: `<ifoda>_<closed|half|open>.png` (ifodalar: `neutral`, `excited`, `surprised`, `scared`, `pointing`) va ixtiyoriy `<ifoda>_blink.png`. Rasmlar kvadrat va shaffof fonli bo'lsin. Biror ifoda bo'lmasa, uning o'rniga `neutral` ishlatiladi.
Haqiqiy ovoz effektlari kerak bo'lsa, ularni `assets/sfx/` papkasiga tashlang: [assets/sfx/README.md](assets/sfx/README.md).

## Ishga tushirish

- **Windows:** `start.bat` faylini ikki marta bosing.
- **macOS / Linux:** `./start.sh`

Birinchi safar kutubxonalar o'zi o'rnatiladi, keyin brauzerda panel ochiladi. Qo'lda ishga tushirish uchun: `python run.py` yoki `uvicorn app:app`. **Birinchi ish:** "Tizim" bo'limida **Tekshirish** tugmasini bosing. Har bir kalit ishlayaptimi, ko'rsatiladi.

Keyin "Yaratish" bo'limida:

1. **Trenddagi Shorts** tugmasi nishangizda hozir nima ko'rilayotganini ko'rsatadi. **Viral g'oyalar topish** tugmasi shularga asoslanib mavzu taklif qiladi. Mavzuni o'zingiz ham yozishingiz mumkin.
2. **Ssenariy yozish**: faktlar tekshiruvi natijasini ko'rib chiqing, hookni tanlang, kerak bo'lsa matnni, video qidiruv so'zlarini, sarlavhalarni va twist sahnasini tahrirlang.
3. **Video yasash**: ovoz, tezlik, seriya nomi, kadr turi (aralash, faqat chizma yoki faqat video) va maskotni tanlang. 2–4 daqiqada tayyor MP4 chiqadi, sarlavha va heshteglar bilan birga.

Terminaldan ham ishlatsa bo'ladi:

```bash
python cli.py "the deepest point of the ocean" --series "Ocean Facts #1"
python cli.py --offline          # kalitsiz sinov: namuna ssenariy, ovozsiz
```

Tayyor videolar `output/` papkasiga saqlanadi. Chizmalar va stok videolar `output/.cache/` papkasida keshlanadi: qayta urinishda yoki A/B variantda ular qayta chizilmaydi va qayta yuklanmaydi.

## Ommaviy rejim va rejalashtirish

"Ommaviy" bo'limida har qatorga bitta mavzu yozing (yoki **G'oyalardan to'ldirish** tugmasini bosing) va **Navbatga qo'shish** tugmasini bosing. Panel har bir mavzu uchun ssenariy yozadi, faktlarni tekshiradi va video yasaydi. "YouTube'ga yuklash" yoqilgan bo'lsa, videoni kanalga ham yuklaydi. **Rejalashtirib joylash** yoqilsa, videolar kuniga belgilangan soatlarga taqsimlanadi.

## YouTube kanalini ulash

1. https://console.cloud.google.com saytida loyiha oching.
2. **APIs & Services → Library** bo'limida **YouTube Data API v3** va **YouTube Analytics API**ni yoqing.
3. **OAuth consent screen**: turini "External" qiling va o'z emailingizni "Test users" ro'yxatiga qo'shing.
4. **Credentials → Create credentials → OAuth client ID → Desktop app**. JSON faylni yuklab oling va panelda "Videolar va kanal" bo'limida tanlang (yoki `shorts_studio/client_secret.json` nomi bilan saqlang).
5. Panelda "Videolar va kanal" bo'limida **Kanalni ulash** tugmasini bosing va brauzerda ruxsat bering. Panelni o'z kompyuteringizda ishga tushirgan bo'lishingiz kerak.

### Bu xavfsizmi?

- Panelga Google parolingiz berilmaydi. Ruxsatni Google'ning o'z sahifasida berasiz, panel faqat cheklangan token oladi.
- Panel faqat **video yuklay oladi** hamda **kanal ma'lumotlari va statistikani o'qiy oladi**. Videolarni o'chira olmaydi, kanal sozlamalarini o'zgartira olmaydi, izoh yoza olmaydi.
- Token faqat sizning kompyuteringizda (`youtube_token.json`) saqlanadi va GitHub'ga tushmaydi. Ruxsatni istalgan payt bekor qilish mumkin: https://myaccount.google.com/permissions
- Kalitlarni va kanal ulanishini faqat panel ishlayotgan kompyuterning o'zidan o'zgartirish mumkin. Panelni `--host 0.0.0.0` bilan internetga ochmang.
- Google ilovasi "test" rejimida bo'lgani uchun ulanish odatda **7 kunda bir** tugaydi. Bunda panel "Ulanish muddati tugagan" deb ko'rsatadi, siz **Kanalni ulash** tugmasini qayta bosasiz.

### Video qanday yuklanadi

Video kompyuteringizdan to'g'ridan-to'g'ri YouTube'ga yuklanadi. Sarlavha, tavsif va heshteglar avtomatik qo'yiladi, kategoriya Education, "bolalar uchun emas". Video **private** bo'lib yuklanadi yoki belgilangan vaqtga rejalashtiriladi. Pin qilinadigan izohni o'zingiz qo'shasiz. YouTube'ning standart kunlik kvotasi odatda kuniga taxminan 6 ta yuklashga yetadi.

**Muhim:** YouTube'ning bepul API auditidan o'tmagan loyihalarda API orqali yuklangan videolar **"private" bo'lib qoladi**. Yuklash ishlaydi, lekin videoni YouTube Studio'da o'zingiz ochiq qilasiz. Avtomatik rejalashtirish esa faqat auditdan keyin ishlaydi. Audit uchun ariza: https://support.google.com/youtube/contact/yt_api_form

Qo'lda yuklagan videolaringizni ham kuzatish mumkin: video kartasidagi **Havola qo'shish** tugmasini bosib, Shorts havolasini kiriting.

## Natijalardan o'rganish

1. Videolar chiqqandan 2–3 kun o'tgach (YouTube statistikasi kechikib keladi) **Statistikani yangilash** tugmasini bosing.
2. Kamida 3 ta video statistikasi yig'ilgach, **Natijalardan o'rganish** tugmasini bosing. Claude qaysi hook, mavzu va uzunlik yaxshi ishlaganini tahlil qilib, kanal qo'llanmasini yozadi.
3. Shundan keyin har bir yangi ssenariy va g'oya shu qo'llanmaga tayanib yoziladi. Har hafta yangilab turing.

A/B uchun: A va B videolarini turli kunlarda joylang. Qo'llanma qaysi hook yutganini ham ko'rsatadi.

## Testlar

```bash
python -m pytest -q                 # hamma testlar (taxminan 1.5 daqiqa)
python -m pytest -q -m "not slow"   # tezkor testlar (10 soniya)
```

## Ko'proq ko'rish uchun maslahatlar

- Kuniga 1–3 ta video joylang, bitta mavzu yo'nalishida qoling.
- Bitta ovozda qoling, u kanalingiz brendiga aylanadi.
- 30–35 soniyalik videolar odatda uzunlariga qaraganda oxirigacha ko'proq ko'riladi.
- Pastki 20% va o'ng chetni YouTube tugmalari yopadi. Panel matnni shu joylardan uzoqda joylashtiradi.
- Birinchi 24 soatdan keyin YouTube Studio'da **"Viewed vs swiped away"** ko'rsatkichini tekshiring. 70% dan past bo'lsa, hook zaif.
- Eng ko'p ko'rilgan videongiz mavzusida 3–5 ta davomini qiling.
