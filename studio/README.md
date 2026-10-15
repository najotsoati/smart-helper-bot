# 🎬 Shorts Studio — Sticky Goes Broke uchun

Mavzu yoki o'z ssenariyingizdan **inglizcha** stickman Shorts yasaydi:

```
Telefon/brauzer ─▶ SERVER (panel + AI xodimlar + ovoz) ─▶ NOUTBUK agenti ─▶ Blender ─▶ TAYYOR/<nom>.mp4
```

| Qadam | Kim qiladi |
|---|---|
| 1. Hook (3 variant, baho bilan) | AI (OpenRouter bepul → Grok zaxira) |
| 2. Ssenariy (beat'lar, gaplar, YouTube matni) | AI |
| 3. Rejissyor jadvali (har kadr: kamera, poza, yuz, matn, tovush) | AI, faqat `studio/vocab.py` lug'atidagi so'zlar bilan |
| 4. Tekshiruvchi | Kod (qoidalar) + AI (retention bo'yicha baho va tuzatish) |
| 5. Ovoz | edge-tts (bepul) yoki ElevenLabs (Liam) |
| 6. Render | Noutbukdagi agent: `stickman_shablon.blend` + `stickman_tools.py` v8 → MP4 |

Har qadamni siz tasdiqlaysiz yoki tahrirlaysiz. O'z ssenariyingizda gaplar so'zma-so'z qoladi;
tayyor storyboard JSON qo'ysangiz, AI umuman ishlatilmaydi.

## Server (Timeweb, Ubuntu)

```bash
git clone <repo> shorts-studio && cd shorts-studio
sudo bash deploy/install.sh          # venv, kutubxonalar, .env, systemd xizmat
nano .env                            # OPENROUTER_API_KEY va boshqalarni yozing
sudo systemctl restart shorts-studio
```

HTTPS uchun Caddy: `apt install caddy`, `deploy/Caddyfile`dagi manzilni o'z IP'ingizga almashtiring
(`185-12-34-56.sslip.io` ko'rinishida), `/etc/caddy/Caddyfile`ga qo'ying, `systemctl reload caddy`.
Panel parolsiz ochilmaydi; parolni HTTPS'siz ishlatmang.

Xotira: panel ~100 MB RAM oladi, Telegram bot bilan birga 2 GB serverga sig'adi.

## Noutbuk agenti (Windows)

1. Python o'rnating (python.org, "Add to PATH" belgisini qo'ying).
2. `agent/` papkasini noutbukka ko'chiring.
3. `agent.ini.example` → `agent.ini`, ichiga server manzili va serverdagi `AGENT_TOKEN`ni yozing.
4. `start_agent.bat` ni ishga tushiring. Agent har 15 soniyada navbatni tekshiradi.

Agent `stickman_shablon.blend`ni Blender'da oynasiz ochadi, keyingi `video_NN.blend`ni yaratadi,
skriptni `video_NN.py` matni sifatida ichiga yozadi, render qiladi, MP4'ni `TAYYOR/`ga ko'chiradi
va panelga yuboradi. Ovozlar `Stickman/studio_audio/<loyiha>/` ga tushadi.

## Testlar

```bash
pip install -r requirements-dev.txt
python -m pytest -q tests
```

## Hali sozlanadigan joylar

- `vocab.BROWS` qiymatlari va ba'zi kamera/matn joylari `video_05`–`video_09` skriptlari bilan solishtirib aniqlanadi.
- Yangi set va gaglar (vaqt mashinasi, muzlatkich, chat ekrani) lug'atga keyingi bosqichda qo'shiladi.
