from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.core.cache import cache
from django.db import models
from django.shortcuts import redirect, render
from django.utils.translation import gettext as _

from .models import (
    Achievement, ExamSession, GalleryImage, Grade, Graduate, News,
    NewsImage, SchoolStat, Student, Teacher, TeacherAchievement,
)

# O'chiriladigan modellar (kontent ma'lumotlari).
# Diqqat: auth.User (admin login), Group, Session, Migrationlar o'chirilmaydi!
MODELS = [
    Achievement,          # o'quvchi yutuqlari (birinchi — Student'ga bog'liq)
    TeacherAchievement,   # o'qituvchi sertifikatlari
    Student,              # o'quvchilar
    NewsImage,            # yangilik rasmlari
    News,                 # yangiliklar
    Graduate,             # bitiruvchilar
    GalleryImage,         # galereya rasmlari
    ExamSession,          # AI imtihon natijalari
    Grade,                # sinflar
    Teacher,              # o'qituvchilar
    SchoolStat,           # statistika
]


def _delete_files(obj):
    """Model ob'ektiga tegishli ImageField fayllarini diskdan o'chirish."""
    for field in obj._meta.fields:
        if isinstance(field, models.ImageField):
            f = getattr(obj, field.name, None)
            if f and hasattr(f, 'name') and f.name:
                try:
                    f.delete(save=False)
                except Exception:
                    pass


@user_passes_test(lambda u: u.is_superuser, login_url='admin:login')
def clear_all_data(request):
    if request.method == 'POST':
        for model in MODELS:
            for obj in model.objects.all():
                _delete_files(obj)
            model.objects.all().delete()
        cache.clear()
        messages.success(request, _("Barcha ma'lumotlar muvaffaqiyatli o'chirildi."))
        return redirect('admin:index')

    counts = {}
    for model in MODELS:
        counts[model._meta.verbose_name_plural] = model.objects.count()
    return render(request, 'admin/clear_data.html', {
        'counts': counts,
        'total': sum(counts.values()),
    })
