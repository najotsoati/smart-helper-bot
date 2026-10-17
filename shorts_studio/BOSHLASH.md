# 🚀 Noutbukda ishga tushirish: qadam-baqadam

Birinchi marta taxminan **30–40 daqiqa** ketadi: kalitlarni olish, o'rnatish va birinchi video. Keyingi safar panel bitta faylni ikki marta bosish bilan ochiladi.

---

## 0. Kalitlarni oldindan tayyorlab qo'ying

Har bir saytda ro'yxatdan o'tib, kalitni (API key) nusxalab, bloknotga saqlab qo'ying.

| Xizmat | Kerakmi | Qayerdan | Narxi |
|---|---|---|---|
| **Claude (Anthropic)** | **majburiy** | https://console.anthropic.com/settings/keys | Balansga pul qo'yasiz. Bitta video (ssenariy, faktlarni tekshirish, kadrlarni baholash) taxminan $0.2–0.5 |
| **Pixabay** | tavsiya (stok videolar) | https://pixabay.com/api/docs/ (ro'yxatdan o'tib kirsangiz, kalit sahifaning "Parameters" qismida ko'rinadi) | bepul |
| **OpenAI** | tavsiya (AI chizmalar) | https://platform.openai.com/api-keys | Balansga pul qo'yasiz. Bir video taxminan $0.3–0.7 |
| **YouTube API kaliti** | ixtiyoriy (trendlar) | https://console.cloud.google.com, "YouTube Data API v3" | bepul |
| **ElevenLabs** | ixtiyoriy (eng jonli ovoz) | https://elevenlabs.io/app/settings/api-keys | bepul tarif bor |

Demak, bitta video taxminan **$0.5–1.2** turadi. Boshlash uchun Claude va OpenAI balansiga $5–10 dan qo'yish yetadi.

> Kalitni hech kimga yubormang va hech qayerga joylamang. Uni faqat panelning o'ziga kiritasiz.

---

## 1. Python va ffmpeg o'rnatish (bir marta)

### Windows
1. **Python 3.12** (3.11 yoki undan yangi bo'lishi kerak): https://www.python.org/downloads/ dan yuklab oling. O'rnatishda birinchi oynada **"Add python.exe to PATH"** belgisini albatta qo'ying.
2. **ffmpeg**: Start menyusida **PowerShell**ni oching va quyidagini yozing:
   ```
   winget install Gyan.FFmpeg
   ```
   O'rnatilgach, PowerShell'ni yopib, qayta oching.

### macOS
Terminal'ni oching:
```
brew install python@3.12 ffmpeg
```
(`brew` yo'q bo'lsa, avval https://brew.sh saytidagi buyruqni bajaring.)

---

## 2. Loyihani yuklab olish

1. GitHub'ga o'z hisobingiz bilan kirgan holda shu havolani oching. ZIP fayl yuklanadi:
   https://github.com/najotsoati/smart-helper-bot/archive/refs/heads/ccr-aa1d78f1-v803px.zip
2. ZIP faylni ochib (Extract), papkani qulay joyga qo'ying, masalan **Hujjatlar** papkasiga.
3. Ichidagi **`shorts_studio`** papkasiga kiring.

Agar `git` ishlatsangiz, yuklab olish o'rniga:
```
git clone -b ccr-aa1d78f1-v803px https://github.com/najotsoati/smart-helper-bot.git
```

---

## 3. Panelni ishga tushirish

- **Windows:** `shorts_studio` ichidagi **`start.bat`** faylini ikki marta bosing.
- **macOS:** Terminal'da `shorts_studio` papkasiga o'ting va `./start.sh` deb yozing.

Birinchi safar kutubxonalar o'rnatiladi, bu 2–3 daqiqa oladi. Keyin brauzerda panel o'zi ochiladi (http://127.0.0.1:8000).

> Qora oynani yopmang: panel shu oyna ochiq turgan paytda ishlaydi. To'xtatish uchun oynada **Ctrl+C** bosing.

---

## 4. Kalitlarni kiritish va tekshirish

1. Panelda **Tizim** bo'limini oching.
2. **API kalitlari**da har bir kalitni o'z maydoniga qo'yib, **Saqlash** tugmasini bosing. Kalit ostida "✓ ishlayapti" yozuvi chiqishi kerak.
3. Pastdagi **Tekshirish** tugmasini bosing. **ffmpeg**, **Claude** va **Microsoft ovozlari** qatorlarida ✓ bo'lishi shart. Qolganlari ixtiyoriy.

✗ chiqsa, yonidagi yozuvni o'qing yoki ekranini yuboring.

---

## 5. Birinchi video

1. **Yaratish** bo'limida mavzu yozing (masalan, `the deepest point of the ocean`) yoki **Viral g'oyalar topish** tugmasini bosing.
2. **Ssenariy yozish** tugmasini bosing (taxminan 1 daqiqa). Faktlar tekshiruvini va hookni ko'rib chiqing, kerak bo'lsa tahrirlang.
3. **Video yasash** tugmasini bosing (taxminan 3–5 daqiqa). Tayyor bo'lgach, video va undagi har bir kadrning matnga mosligi (%) ko'rsatiladi.

Birinchi videoni ko'rib, menga yuboring. Birga sozlaymiz.

---

## 6. YouTube kanalini ulash (keyinroq ham bo'ladi)

[README.md → YouTube kanalini ulash](README.md#youtube-kanalini-ulash) bo'limidagi 5 qadamni bajaring, keyin "Videolar va kanal" bo'limida **Kanalni ulash** tugmasini bosing.

---

## 7. Kechasi ommaviy rejimda qoldirish

1. **Ommaviy** bo'limida har qatorga bitta mavzu yozing (yoki **G'oyalardan to'ldirish** tugmasini bosing) va **Navbatga qo'shish** tugmasini bosing.
2. Noutbukni **quvvatga ulang** va **uyqu rejimini o'chiring**:
   - Windows: *Sozlamalar → Tizim → Quvvat → Ekran va uyqu → Uyqu: Hech qachon*
   - macOS: Terminal'da `caffeinate -i ./start.sh` buyrug'i bilan ishga tushiring.
3. Qopqoqni yopmang, aks holda noutbuk uxlab qoladi.
4. Ertalab **Navbat** ro'yxatida har bir video "tayyor" yoki "xato" deb ko'rsatiladi.

Bitta video taxminan 3–6 daqiqada tayyor bo'ladi. Demak, 10 ta mavzu taxminan 1 soat oladi.

---

## Muammo bo'lsa

| Belgi | Yechim |
|---|---|
| `start.bat` "Python topilmadi" deydi | Python'ni qayta o'rnating, **"Add python.exe to PATH"** belgisini qo'ying |
| "ffmpeg topilmadi" | 1-qadamdagi ffmpeg o'rnatishni bajaring va oynani qayta oching. Yordam bermasa, kompyuterni qayta yoqing (Windows yangi PATH'ni ba'zan shundan keyin ko'radi) |
| Ssenariy ostida "⚠ Faktlarni tekshirib bo'lmadi" | Ssenariy saqlanib qoladi, faqat tekshirilmagan bo'ladi. Odatda sabab: Anthropic hisobingizda veb-qidiruv (web search) o'chiq. Uni console.anthropic.com sozlamalarida yoqing yoki "Faktlarni tekshirish" belgisini olib qo'ying |
| Moslik hisobotida "Stok video: ..." | Pixabay (yoki Pexels) kaliti noto'g'ri yoki xizmat javob bermadi. Video baribir yasaladi: bu sahnalar AI chizma yoki rangli fon bilan almashtiriladi |
| Kalit ostida "Kalit noto'g'ri (401)" | Kalitni qaytadan nusxalang (boshida yoki oxirida bo'sh joy qolmasin) |
| "Ruxsat yo'q (403)" | Hisobda pul bormi yoki xizmat hududingizda ishlaydimi, tekshiring |
| "Limit tugagan (429)" | Balansni to'ldiring yoki biroz kuting |
| Video yasash xato bilan to'xtadi | **Navbat**dagi xato matnini nusxalab yuboring |
| Panel ochilmadi | Qora oynadagi oxirgi qatorlarni nusxalab yuboring |
