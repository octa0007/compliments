"""
Daily Turkish compliment email sender.
Runs via GitHub Actions every morning.
"""
import os, smtplib, math
from datetime import date, datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# ── CONFIG ────────────────────────────────────────────────────
LOVER_NAME   = "Sultan"          # ← her name / nickname
SENDER_NAME  = "Seni seven"     # ← how you sign off
SITE_URL     = os.environ.get("SITE_URL", "")   # set as GitHub secret
# ─────────────────────────────────────────────────────────────

COMPLIMENTS = [
    "Gülüşün odayı aydınlatıyor, tıpkı güneşin sabahı aydınlattığı gibi.",
    "Sen dünyayı daha güzel bir yer yapıyorsun, sadece var olarak.",
    "Varlığın tek başına bir armağan — bunu hiç unutma.",
    "Gözlerin içindeki güzelliği yansıtıyor; görmek isteyenlere yeter.",
    "Seninle geçen her an, hayatımın en değerli anları arasında.",
    "Zekân ve güzelliğin mükemmel bir uyum içinde dans ediyor.",
    "Kalbinin iyiliği seni dünyada eşsiz kılıyor.",
    "Seninle olmak cenneti yeryüzünde yaşatıyor.",
    "Sesinin tonu beni her seferinde büyülüyor.",
    "Sen her bakışta biraz daha güzelleşiyorsun.",
    "Düşünce biçimin beni her zaman hayrete düşürüyor.",
    "Seninle gülmek dünyanın en güzel sesi.",
    "Sen olmasan bu dünya ne kadar eksik kalırdı.",
    "Güçlü ve nazik olmayı bir arada başarmak için seçilmiş gibisin.",
    "Her geçen gün seni bir önceki günden daha çok seviyorum.",
    "Sen benim en büyük ilham kaynağımsın.",
    "Bakışlarında bir dünya var; içinde kaybolmak istiyorum.",
    "Seninle geçirdiğim her dakika, bir hazine gibi saklıyorum içimde.",
    "Seni düşündüğümde her şey daha hafif hissettiriyor.",
    "Hem güçlü hem şefkatli olmayı — bunu çok az kişi başarır.",
    "Kahkahanı duymak benim için en değerli armağan.",
    "Sen benim kalbimin en huzurlu köşesisin.",
    "Varlığın sadece benim için değil, çevrendeki herkes için bir şans.",
    "Seninle baş başa geçirilen her an, ömrümün en değerlisi.",
    "Seni sevmek hayatımın en doğru kararı.",
    "Sen benim için güneşin doğduğu yönsün.",
    "Her halin farklı bir güzellik taşıyor.",
    "Seninle her şey daha anlamlı hissettiriyor.",
    "Hem aklımı hem kalbimi dolduruyorsun.",
    "Kibarlığın ve nezaketin seni çok özel yapıyor.",
    "Seninle olmak, hayatımın en büyük şansı.",
    "Sen benim en sevdiğim hikayesin.",
    "Seninle geçen her mevsim renkleniyor ve anlam kazanıyor.",
    "Senin varlığın hayatıma anlam katıyor.",
    "Her gün seninle biraz daha büyüyorum.",
    "Sen benim için çok değerlisin — bunu her zaman bil.",
    "Seninle olmak bir rüya, ama gerçeğinden daha güzel.",
    "Güzelliğin içten geliyor; bu seni gerçekten eşsiz kılıyor.",
    "Sen benim dünyamın en güzel köşesisin.",
    "Kalbin kadar güzel bir ruh az görülür.",
    "Seninle olmak bana tam bir huzur veriyor.",
    "Her bakışın kalbimi ısıtıyor, her seferinde.",
    "Hem akıllı hem zarif; ikisini bu kadar güzel taşıyan az.",
    "Gözlerin içindeki sonsuz derinliği yansıtıyor.",
    "Seni sevmek, nefes almak kadar doğal geliyor bana.",
    "Sen benim için her gün yeniden doğan bir mucizesin.",
    "Zarif duruşun ve güzel kalbinle gerçekten eşsizsin.",
    "Her geçen gün sana olan sevgim biraz daha derinleşiyor.",
    "Sen hem güçlü hem naifsin — bu kombinasyon seni eşsiz yapıyor.",
    "Sen benim için güneşin ilk ışığı gibisin.",
    "Seninle her sabaha uyanmak, hayatımın en büyük lüksü.",
    "Seti tanımak, hayatıma en güzel şeyi katmak oldu.",
    "Sen her zaman çevreni daha aydınlık bir yere dönüştürüyorsun.",
    "Güzelliğin zamanla değil, kalpten geliyor — bu hiç solmaz.",
    "Seninle birlikte olmak, her gün küçük bir mucize.",
    "Senin gibisi gerçekten az; bu dünyada bunu bilen şanslı.",
    "Her gülüşünde bir dünya var ve ben o dünyada yaşamak istiyorum.",
    "Sen benim için yıldızlardan daha parlaksın.",
    "Seninle geçirilen her anı ömrüm boyunca hatırlayacağım.",
    "Sen benim kalbimin en sevdiği şarkısısın.",
    "Seni düşündüğümde her şey yerine oturuyor.",
    "Sana olan sevgim her gün biraz daha büyüyor.",
    "Seninle olmak, hayatımın en iyi kararı — her gün bunu hissediyorum.",
    "Sen benim için hem sığınak hem macera.",
    "Kırşehir seni doğurmuş, dünya sana şükretmeli.",
    "Meri jaan, sen benim canım, ruhum, her şeyimsin — bunu her zaman bil.",
    "Mein fettisacki, ne kadar tatlı ve eşsiz birisin — kelimeler yetmiyor.",
    "Sevgili buggi schnuggi'm, seninle her gün yeni bir mucize başlıyor.",
    "Meri jaan — bu kelime tam seni anlatıyor; sen gerçekten benim caanımsın.",
    "Her sabah gözlerini açtığında bil ki, buggi schnuggi'm, biri seni çok seviyor.",
    "Meri jaan, seni sevmek hayatımın en güzel görevidir.",
    "Mein fettisacki, seninle olmak benim için dünyanın en büyük lüksü.",
    "Buggi schnuggi'm, seninle paylaşılan kahkahalar benim en sevdiğim müzik.",
    "Meri jaan, seninle her adım daha anlamlı.",
    "Mein fettisacki, sen benim için dünyanın en tatlı sırrısın.",
    "Meri jaan — seninle geçirilen her an, ömrümün en güzel sayfaları.",
    "Buggi schnuggi'm, seninle paylaşılan her an hazineye dönüşüyor.",
    "Mein fettisacki, seninle her gün yeni bir maceraya atılmak istiyorum.",
    "Seninle olmak, en güzel kitabı sonuna kadar okumak gibi — bitmesini istemiyorum.",
    "Sen benim için hem liman hem ufuksun.",
    "Seni sevmek bir seçim değil, bir ihtiyaç — o kadar doğal.",
    "Her sabah seni düşünerek uyanmak, günün en güzel başlangıcı.",
    "Seninle paylaşılan sessizlik bile anlamlı.",
    "Sen benim için kelimelerden büyüksün.",
    "Her halinle büyüleyicisin — sevinçli, düşünceli, hatta hüzünlüyken bile.",
    "Seti sevmek, en güzel şiiri ezbere bilmek gibi — asla unutmuyorum.",
    "Seninle olmak, en güzel melodiyi her gün yeniden duymak gibi.",
    "Gözlerindeki ışık hiç sönmüyor — bu seni eşsiz yapıyor.",
    "Seti sevmek kolayın kolayı — doğal, saf ve sonsuz.",
    "Seninle olmak, hayatımın en doğru cümlesi.",
    "Sen benim kalbimin en sık ziyaret ettiği yerisin.",
    "Seninle olan her hatıra, içimi ısıtıyor.",
    "Seti sevmek, hayatımın en büyük onuru.",
    "Yengeç burçlusun — kalbinin derinliği ve sezgilerinin gücü seni gerçekten özel kılıyor.",
    "Ay'ın çocuğusun; tıpkı Ay gibi her haliyle büyüleyicisin.",
    "Ejderha yılında doğmuşsun — o güç, cesaret ve büyü sende hep hissedilir.",
    "Su elementi sana o derin sezgiyi vermiş; duyguları bu kadar güzel taşımak bir hediyedir.",
    "Doğduğun gün dünya çok güzel bir hediye aldı — seni.",
    "Ay seni yönetir; bu yüzden hem derinsin hem sırlısın hem de büyüleyicisin.",
    "Hem cesur hem de şefkatlisin — bu ikisi bir arada az görülür.",
    "Güçlü bir kalbin var — hem kendini hem de sevdiklerini koruyorsun.",
    "Sevgin her şeyi iyileştiriyor — bu nadiren görülen bir güç.",
    "Sen içten dışa, her açıdan güzelsin.",
    "Seninle olmak beni daha iyi bir insan yapıyor.",
    "Seti düşünmek bile yüzümde gülümseme açıyor.",
    "Varlığın güneşin olmadığı günlerde bile sıcak hissettiriyor.",
    "Sana olan sevgim her geçen günle kökleniyor, derinleşiyor.",
    "Seninle geçirilen her gün, bir armağan gibi hissettiriyor.",
    "Sana baktığımda, dünyanın en güzel tablosunu görüyorum.",
    "Seninle olmak beni her gün daha mutlu ediyor.",
    "Seninle olmak, en güzel rüyayı gerçek gibi yaşamak.",
    "Sen benim için her günün en güzel sebebisin.",
    "Her gün biraz daha sana hayran kalıyorum.",
    "Seninle her anı doyasıya yaşamak istiyorum.",
    "Her sabah gözlerimi açtığımda, seninle aynı dünyada olmak için teşekkür ediyorum.",
    "Sen benim için yıldızlardan da güzel, güneşten de sıcaksın.",
    "Sen benim için hem geçmiş hem gelecek — her şeyimsin.",
    "Senin varlığın bana güç veriyor, dayanma gücü.",
    "Sen benim için hem ışık hem yönsün.",
    "Seninle geçirilen her an, hayatımın en güzel anısı olmaya aday.",
    "Sen benim için bir evren — keşfetmeye doyamıyorum.",
    "Seti sevmek, dünyanın en doğal şeyi.",
    "Sen benim için kelimelerle anlatılamayan bir güzelliksin.",
    "Sen benim için hem sabah hem akşam — günümün tamamısın.",
    "Seninle olmak, hayatımın en güzel sayfası.",
    "Meri jaan, seninle her şey daha büyük, daha derin, daha güzel.",
    "Buggi schnuggi'm, sen benim için dünyanın en güzel sürprizisin.",
    "Sen benim için sonsuz — seti anlatacak kelimeler henüz icat edilmedi.",
    "Seninle her sabaha bakmak, hayatımın en büyük ödülü.",
    "Mein fettisacki, seninle paylaşılan sessizlik bile bir şiir.",
    "Meri jaan, sen olmadan hiçbir şey tam olmazdı.",
]

TR_MONTHS = ["Ocak","Şubat","Mart","Nisan","Mayıs","Haziran",
             "Temmuz","Ağustos","Eylül","Ekim","Kasım","Aralık"]
TR_DAYS   = ["Pazartesi","Salı","Çarşamba","Perşembe","Cuma","Cumartesi","Pazar"]

def pick_compliment():
    today = date.today()
    key   = today.year * 10000 + today.month * 100 + today.day
    # Same hash as the website so they match
    h = (key * 2654435761) & 0xFFFFFFFF
    h ^= h >> 16; h = (h * 0x45d9f3b) & 0xFFFFFFFF; h ^= h >> 16
    return COMPLIMENTS[h % len(COMPLIMENTS)]

def turkish_date():
    today = date.today()
    return f"{TR_DAYS[today.weekday()]}, {today.day} {TR_MONTHS[today.month-1]} {today.year}"

def build_email(compliment):
    date_str = turkish_date()
    site_link = f'<a href="{SITE_URL}" style="color:#d4af37">siteye git →</a>' if SITE_URL else ""

    html = f"""
<!DOCTYPE html>
<html lang="tr">
<head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
</head>
<body style="margin:0;padding:0;background:#0d0508;font-family:Georgia,serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#0d0508;padding:40px 20px">
<tr><td align="center">
<table width="560" style="max-width:560px;width:100%">
  <tr><td style="text-align:center;padding-bottom:24px">
    <p style="color:#f0d060;font-size:22px;margin:0;letter-spacing:1px">Sevgili {LOVER_NAME}</p>
    <p style="color:#c9a0b4;font-size:11px;letter-spacing:3px;margin:6px 0 0;text-transform:uppercase">{date_str}</p>
  </td></tr>

  <tr><td style="background:rgba(30,10,20,0.95);border:1px solid rgba(212,175,55,0.2);border-radius:20px;padding:40px 36px;text-align:center">
    <p style="color:#f48fb1;font-size:10px;letter-spacing:4px;text-transform:uppercase;margin:0 0 24px">✦ &nbsp; bugünkü sürprizin &nbsp; ✦</p>
    <p style="color:#fdeef5;font-size:22px;line-height:1.7;font-style:italic;margin:0 0 28px">
      &#8220;{compliment}&#8221;
    </p>
    <p style="color:#c9a0b4;font-size:13px;margin:0">— {SENDER_NAME}</p>
  </td></tr>

  <tr><td style="text-align:center;padding-top:24px">
    <p style="color:#c9a0b4;font-size:12px;margin:0">
      ❤️ &nbsp; Her gün farklı, her gün sana özel
      {"&nbsp;·&nbsp;" + site_link if SITE_URL else ""}
    </p>
  </td></tr>
</table>
</td></tr>
</table>
</body></html>
"""
    plain = f"Sevgili {LOVER_NAME},\n\n\"{compliment}\"\n\n— {SENDER_NAME}\n\n({date_str})"
    return html, plain

def send():
    gmail_user  = os.environ["GMAIL_USER"]
    app_pw      = os.environ["GMAIL_APP_PASSWORD"]
    recipient   = os.environ["RECIPIENT_EMAIL"]

    compliment  = pick_compliment()
    html, plain = build_email(compliment)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"💕 Bugünkü sürprizin, {LOVER_NAME} — {turkish_date()}"
    msg["From"]    = f"{SENDER_NAME} <{gmail_user}>"
    msg["To"]      = recipient

    msg.attach(MIMEText(plain, "plain", "utf-8"))
    msg.attach(MIMEText(html,  "html",  "utf-8"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
        s.login(gmail_user, app_pw)
        s.sendmail(gmail_user, recipient, msg.as_bytes())

    print(f"✓ Sent: {compliment[:60]}…")

if __name__ == "__main__":
    send()
