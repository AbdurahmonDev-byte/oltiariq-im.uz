from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

GENDER_CHOICES = [
    ('M', _('Erkak')),
    ('F', _('Ayol')),
]

# O'qituvchilar
class Teacher(models.Model):
    DEGREE_CHOICES = [
        ('oliy', _('Oliy ma\'lumotli mutaxassis')),
        ('1-daraja', _('1-darajali mutaxassis')),
        ('2-daraja', _('2-darajali mutaxassis')),
    ]
    
    full_name = models.CharField(max_length=100)
    subject = models.CharField(max_length=100)
    image = models.ImageField(upload_to='teachers/')
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='M', verbose_name="Jinsi")
    birth_date = models.DateField(null=True, blank=True, verbose_name="Tug'ilgan sana")
    degree = models.CharField(max_length=20, choices=DEGREE_CHOICES, default='mutaxassis', verbose_name="Darajasi")
    position = models.CharField(max_length=100, blank=True, null=True, verbose_name="Lavozimi (masalan: Maktab direktori, Xalq o'qituvchisi)")
    bio = models.TextField(blank=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefon raqami")

    # achievements qatorini o'chirib tashlasak ham bo'ladi, chunki endi alohida model qilamiz

    def __str__(self): return self.full_name
    def get_absolute_url(self):
        return reverse('teacher_detail', args=[self.pk])

# Sinflar
class Grade(models.Model):
    name = models.CharField(max_length=50)
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, related_name='managed_classes')
    academic_year = models.CharField(max_length=20, default="2025-2026")

    def __str__(self): return self.name
    def get_absolute_url(self):
        return reverse('grade_detail', args=[self.pk])

# O'quvchilar
# main/models.py ichida Student modelini top va buni yoz:

# main/models.py
class Student(models.Model):
    grade = models.ForeignKey('Grade', on_delete=models.CASCADE, related_name='students')
    full_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='M', verbose_name="Jinsi")
    id_number = models.CharField(max_length=20, unique=True, blank=True, null=True)
    photo = models.ImageField(upload_to='students/')
    birth_date = models.DateField(null=True, blank=True)
    admission_score = models.FloatField(default=0)
    is_leader = models.BooleanField(default=False)
    bio = models.TextField()

    def save(self, *args, **kwargs):
        if not self.id_number:
            last_id = Student.objects.all().order_by('id').last()
            self.id_number = f"ID-{last_id.id + 1001 if last_id else 1001}"
        super().save(*args, **kwargs)

    def __str__(self): return self.full_name
    def get_absolute_url(self):
        return reverse('student_detail', args=[self.pk])

# Yutuqlar (Sertifikatlar uchun)
class Achievement(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='achievements_list')
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='certificates/')
    description = models.TextField()

# Yangiliklar
class News(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    main_image = models.ImageField(upload_to='news/')
    created_at = models.DateTimeField(auto_now_add=True)
    views = models.PositiveIntegerField(default=0, verbose_name="Ko'rishlar")
    likes = models.PositiveIntegerField(default=0, verbose_name="Layklar")

    def __str__(self): return self.title
    def get_absolute_url(self):
        return reverse('news_detail', args=[str(self.id)])

# YANGILIKLAR GALEREYASI (Mana shu modelni admin.py qidiryapti)
class NewsImage(models.Model):
    news = models.ForeignKey(News, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='news/gallery/')

# Bitiruvchilar
class Graduate(models.Model):
    full_name = models.CharField(max_length=100)
    year = models.IntegerField()
    image = models.ImageField(upload_to='graduates/')
    achievement = models.CharField(max_length=255)

# models.py ichida SchoolStat modelini toping va mana shunday o'zgartiring:
class SchoolStat(models.Model):
    # Ikonkani rasm sifatida yuklaymiz (PNG yoki SVG)
    icon_image = models.ImageField(upload_to='stats/icons/', verbose_name="Ikonka (Flaticon)")
    value = models.CharField(max_length=20, verbose_name="Qiymat (masalan: 450+)")
    label_uz = models.CharField(max_length=100, verbose_name="Nomi (UZ)")
    label_en = models.CharField(max_length=100, verbose_name="Nomi (EN)")
    label_ru = models.CharField(max_length=100, verbose_name="Nomi (RU)")

    def __str__(self): return self.label_uz

# O'QITUVCHI SERTIFIKATLARI UCHUN YANGI MODEL
class TeacherAchievement(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='achievements_list')
    title = models.CharField(max_length=200, verbose_name="Sertifikat nomi")
    image = models.ImageField(upload_to='teachers/certificates/')
    description = models.TextField(blank=True)

    def __str__(self): return f"{self.teacher.full_name} - {self.title}"
# Galereya rasmlari (albomsiz, shunchaki rasm yuklanadi)
class GalleryImage(models.Model):
    image = models.ImageField(upload_to='gallery/photos/')
    caption = models.CharField(max_length=255, blank=True, verbose_name="Rasm tavsifi (ixtiyoriy)")
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self): return self.caption or self.image.name
class ExamSession(models.Model):
    student_name = models.CharField(max_length=100)
    subject = models.CharField(max_length=50) # Matematika, Ingliz tili...
    score = models.IntegerField(default=0)
    total_questions = models.IntegerField(default=10)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student_name} - {self.score}"