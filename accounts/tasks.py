from __future__ import absolute_import, unicode_literals
from celery import shared_task
from django.core.mail import send_mail


@shared_task
def send_tmp_password(email, username, new_pwd):
    send_mail(
        "Worka Service Team",
        f"안녕하세요 {username}님 :)\n\nWorka에서 임시 비밀번호를 발급해드렸습니다."
        f"\n\n임시 비밀번호는 {new_pwd} 입니다. \n\n"
        "로그인 후 비밀번호를 변경해주세요 :)",
        "workaservice@gmail.com",
        [email],
        fail_silently=False,
    )
    return None
