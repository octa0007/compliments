"""
Günlük iltifat e-postası.
GitHub Actions her sabah çalıştırır.

İltifatlar compliments.js dosyasından okunur — site ile aynı kaynak,
aynı seçim formülü. Yani e-postadaki cümle ile sitedeki cümle her zaman aynıdır.
"""

import json
import math
import os
import re
import smtplib
import sys
from datetime import date, datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr, formatdate
from pathlib import Path

# ── AYARLAR ──────────────────────────────────────────────────
NAME          = "Sultan"           # ona nasıl sesleniyorsun
SENDER_NAME   = "Seni seven"       # imzan
BIRTHDAY      = "2000-06-29"
TOGETHER      = "2023-12-01"       # boş bırakabilirsin: ""
SITE_URL      = os.environ.get("SITE_URL", "")
# ─────────────────────────────────────────────────────────────

TR_MONTHS = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran",
             "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]
TR_DAYS   = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]

ROOT = Path(__file__).resolve().parent


# ── iltifatlar ───────────────────────────────────────────────
def load_compliments():
    """compliments.js içindeki JSON dizisini okur."""
    src = (ROOT / "compliments.js").read_text(encoding="utf-8")
    start, end = src.index("["), src.rindex("]") + 1
    data = json.loads(src[start:end])
    if not data:
        raise ValueError("compliments.js boş görünüyor.")
    return data


# ── günün seçimi (assets/app.js ile birebir aynı) ────────────
def pick(compliments, today):
    n = (today - date(1970, 1, 1)).days
    length = len(compliments)
    step = (today.year * 7919) % length or 1
    while math.gcd(step, length) != 1:
        step = (step + 1) % length or 1
    offset = (today.year * 104729) % length
    return compliments[(step * n + offset) % length]["t"]


def tr_date(d):
    return f"{TR_DAYS[d.weekday()]}, {d.day} {TR_MONTHS[d.month - 1]} {d.year}"


def days_until(iso, today):
    """Yıllık tekrar eden bir tarihe kalan gün ve kaçıncı yıl olduğu."""
    y, m, d = map(int, iso.split("-"))
    try:
        nxt = date(today.year, m, d)
    except ValueError:                      # 29 Şubat
        nxt = date(today.year, m, 28)
    if nxt < today:
        nxt = date(today.year + 1, m, d)
    return (nxt - today).days, nxt.year - y


def occasion_line(today):
    """Bugün özel bir gün mü? (başlık, açıklama) ya da None."""
    bd_days, bd_n = days_until(BIRTHDAY, today)
    if bd_days == 0:
        return f"Mutlu yıllar, {NAME} — {bd_n} yaşındasın", "Bugün dünyanın en güzel günü, çünkü sen bugün doğdun."
    if TOGETHER:
        an_days, an_n = days_until(TOGETHER, today)
        if an_days == 0:
            return f"{an_n}. yıl dönümümüz", "Aynı kararı bugün de veriyorum: sen."
        together = (today - date(*map(int, TOGETHER.split("-")))).days
        if together > 0 and together % 100 == 0:
            return f"{together}. günümüz", "Yüzer yüzer sayıyorum, hiç şaşırmadan."
    if bd_days == 1:
        return "Yarın doğum günün", "Bu gece uyumadan bir dilek tut."
    if bd_days <= 7:
        return f"Doğum gününe {bd_days} gün", f"{bd_n} yaşına sayılı gün kaldı."
    return None


# ── e-posta ──────────────────────────────────────────────────
def build_email(compliment, today):
    date_str = tr_date(today)
    occ = occasion_line(today)

    occ_html = ""
    if occ:
        occ_html = f"""
      <tr><td style="padding:0 0 18px">
        <table width="100%" cellpadding="0" cellspacing="0" role="presentation">
          <tr><td align="center" style="border:1px solid rgba(200,162,76,.45);background:#101838;padding:14px 18px">
            <div style="font-family:Georgia,serif;font-style:italic;font-size:17px;color:#e7ce8c">{occ[0]}</div>
            <div style="font-family:Georgia,serif;font-size:13px;color:#9aa3c0;padding-top:3px">{occ[1]}</div>
          </td></tr>
        </table>
      </td></tr>"""

    footer_link = ""
    if SITE_URL:
        footer_link = (f' &nbsp;·&nbsp; <a href="{SITE_URL}" '
                       f'style="color:#c8a24c;text-decoration:none">bugünün sayfası</a>')

    html = f"""<!DOCTYPE html>
<html lang="tr"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Sana Özel</title></head>
<body style="margin:0;padding:0;background:#060a18">
<table width="100%" cellpadding="0" cellspacing="0" role="presentation" style="background:#060a18;padding:34px 16px">
<tr><td align="center">
  <table width="540" cellpadding="0" cellspacing="0" role="presentation" style="max-width:540px;width:100%">

    <tr><td align="center" style="padding-bottom:22px">
      <div style="font-family:Georgia,serif;font-style:italic;font-size:14px;color:#d98ba0">Sevgili</div>
      <div style="font-family:Georgia,serif;font-size:40px;font-style:italic;color:#e7ce8c;line-height:1.15">{NAME}</div>
      <div style="font-family:Georgia,serif;font-size:12px;color:#6f7896;letter-spacing:1.5px;padding-top:8px">{date_str}</div>
    </td></tr>
{occ_html}
    <tr><td style="background:#f7efe1;padding:6px">
      <table width="100%" cellpadding="0" cellspacing="0" role="presentation"
             style="border:1px solid rgba(200,162,76,.55)">
        <tr><td align="center" style="padding:34px 26px">
          <div style="font-family:Georgia,serif;font-size:13px;font-style:italic;color:#6b5b46;padding-bottom:20px">
            bugün sana söylemek istediğim şey
          </div>
          <div style="font-family:Georgia,serif;font-size:21px;font-style:italic;line-height:1.55;color:#2b2318">
            &ldquo;{compliment}&rdquo;
          </div>
          <div style="font-family:Georgia,serif;font-size:15px;font-style:italic;color:#a3384f;padding-top:22px">
            &mdash; {SENDER_NAME}
          </div>
        </td></tr>
      </table>
    </td></tr>

    <tr><td align="center" style="padding-top:22px">
      <div style="font-family:Georgia,serif;font-size:12px;color:#6f7896">
        Her gün yeni bir söz, sadece sana{footer_link}
      </div>
    </td></tr>

  </table>
</td></tr>
</table>
</body></html>"""

    plain_parts = [f"Sevgili {NAME},", ""]
    if occ:
        plain_parts += [occ[0], occ[1], ""]
    plain_parts += [f'"{compliment}"', "", f"— {SENDER_NAME}", "", date_str]
    if SITE_URL:
        plain_parts += ["", SITE_URL]
    return html, "\n".join(plain_parts)


def send():
    try:
        gmail_user = os.environ["GMAIL_USER"]
        app_pw     = os.environ["GMAIL_APP_PASSWORD"]
        recipient  = os.environ["RECIPIENT_EMAIL"]
    except KeyError as missing:
        sys.exit(f"Eksik ortam değişkeni: {missing}. GitHub secrets ayarlarını kontrol et.")

    today      = datetime.now(timezone.utc).date()
    compliment = pick(load_compliments(), today)
    html, plain = build_email(compliment, today)

    occ = occasion_line(today)
    subject = f"{occ[0]} 🤍" if occ else f"Bugünün sözü, {NAME}"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = formataddr((SENDER_NAME, gmail_user))
    msg["To"]      = recipient
    msg["Date"]    = formatdate(localtime=True)
    msg.attach(MIMEText(plain, "plain", "utf-8"))
    msg.attach(MIMEText(html, "html", "utf-8"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=30) as s:
        s.login(gmail_user, app_pw)
        s.sendmail(gmail_user, [recipient], msg.as_bytes())

    print(f"Gönderildi ({tr_date(today)}): {compliment[:70]}…")


if __name__ == "__main__":
    if "--preview" in sys.argv:
        # Gönderme, sadece göster: python send_compliment.py --preview
        today = date.today()
        text  = pick(load_compliments(), today)
        html, plain = build_email(text, today)
        Path("preview.html").write_text(html, encoding="utf-8")
        print(plain)
        print("\npreview.html yazıldı.")
    else:
        send()
