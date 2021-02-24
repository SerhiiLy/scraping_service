import os
import sys
import django
import datetime
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth import get_user_model

proj = os.path.dirname(os.path.abspath('manage.py'))
sys.path.append(proj)
os.environ["DJANGO_SETTINGS_MODULE"] = "scraping_service.settings"

django.setup()
from scraping.models import Vacancy, Error, Url
from scraping_service.settings import EMAIL_HOST_USER
ADMIN_USER = EMAIL_HOST_USER

today = datetime.date.today()
subject = f"Розсилка ваканцій за {today}"
text_content = f"Розсилка ваканцій {today}"
from_email = EMAIL_HOST_USER
empty = '<h2>На жаль на сьогодні за Вашим запитом нічого немає</h2>'

User = get_user_model()
qs = User.objects.filter(send_email=True).values('city', 'language', 'email')
users_dct = {}
for i in qs:
    users_dct.setdefault((i['city'], i['language']), [])
    users_dct[(i['city'], i['language'])].append(i['email'])
if users_dct:
    params = {'city_id__in': [], 'language_id__in': []}
    for pair in users_dct.keys():
        params['city_id__in'].append(pair[0])
        params['language_id__in'].append(pair[1])
    qs = Vacancy.objects.filter(**params, timestamp=today).values()[:10]

    vacancies = {}
    for i in qs:
        vacancies.setdefault((i['city_id'], i['language_id']), [])
        vacancies[(i['city_id'], i['language_id'])].append(i)
    for keys, emails in users_dct.items():
        rows = vacancies.get(keys, [])
        html = ''
        for row in rows:
            html += f'<h3><a href="{ row["url"] }">{ row["title"]}</a></h3>'
            html += f'<p>{ row["description"]}</p>'
            html += f'<p>{ row["company"]}</p><br><hr>'
        _html = html if html else empty
        for email in emails:
            to = email
            msg = EmailMultiAlternatives(subject, text_content, from_email, [to])

            msg.attach_alternative(_html, "text/html")
            msg.send()

qs = Error.objects.filter(timestamp=today)
_html = ''
subject = ''
to = ADMIN_USER
text_content = ''
if qs.exists():
    error = qs.first()
    _html = ''
    data = error.data['errors']
    for i in data:
        _html += f'<p><a href="{ i["url"] }">Error: { i["title"]}</a></p>'
    subject = f"Помилки скрапінга {today}"
    text_content = "Помилки скрапінга"
    data = error.data['user_data']
    if data:
        _html += '<hr>'
        _html += '<h2> Побажання користувачів </h2>'
        for i in data:
            _html += f'<p>Місто: {i["city"]}, Спеціальність: {i["language"]} Email: {i["email"]}</p>'
        subject = f"Побажання користувачів {today}"
        text_content = "Побажання користувачів"

qs = Url.objects.all().values('city', 'language')
urls_dct = {(i['city'], i['language']): True for i in qs}
urls_err = ''
for keys in users_dct.keys():
    if keys not in urls_dct:
        if keys[0] and keys[1]:
            urls_err += f'<p> Для міста:{keys[0]} і мови програмування: {keys[1]}  відсутній url</p>'

if urls_err:
    subject += f"Відсутні силки {today}"
    _html += '<hr>'
    subject += f" <h2> Відсутні силки {today}</h2>"
    _html += urls_err

if subject:
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(_html, "text/html")
    msg.send()



# import smtplib
# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText
#
# msg = MIMEMultipart('alternative')
# msg['Subject'] = 'Список вакансий за  {}'.format(today)
# msg['From'] = EMAIL_HOST_USER
# mail = smtplib.SMTP()
# mail.connect(EMAIL_HOST, 25)
# mail.ehlo()
# mail.starttls()
# mail.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
#
# html_m = "<h1>Hello world</h1>"
# part = MIMEText(html_m, 'html')
# msg.attach(part)
# mail.sendmail(EMAIL_HOST_USER, [to], msg.as_string())
# mail.quit()