from django.contrib import admin
from .models import News, NewsImage, Teacher, TeacherAchievement, Grade, Student, Achievement, SchoolStat

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    # Bu yerda grade__name qo'shilgani uchun sinf bo'yicha ham qidiradi
    search_fields = ['full_name', 'id_number', 'grade__name'] 
    list_display = ('full_name', 'grade', 'id_number')
    list_filter = ('grade',)

# 1. Yangiliklar
class NewsImageInline(admin.TabularInline):
    model = NewsImage
    extra = 1

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'views', 'likes')
    readonly_fields = ('views', 'likes')
    inlines = [NewsImageInline]

# 2. O'qituvchilar
class TeacherAchievementInline(admin.TabularInline):
    model = TeacherAchievement
    extra = 1

@admin.register(Teacher) # SHU YERDA RO'YXATDAN O'TDI
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'position', 'subject', 'degree', 'gender')
    list_filter = ('degree', 'gender', 'subject', 'position')
    search_fields = ('full_name', 'position', 'subject')
    inlines = [TeacherAchievementInline]

# 3. O'quvchilar
class AchievementInline(admin.TabularInline):
    model = Achievement
    extra = 1

@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    # MANA SHU QATOR DROPDOWN-NI QIDIRUVGA AYLANTIRADI
    autocomplete_fields = ['student'] 
    list_display = ('student', 'title')

# 4. QOLGANLARI (Bularни dekoratori yo'q, shuning uchun pastda yozamiz)
admin.site.register(Grade)
admin.site.register(SchoolStat)
admin.site.register(TeacherAchievement)

# 5. GALEREYA (albomsiz — rasm shunchaki yuklanadi)
from .models import GalleryImage
@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ('caption', 'image', 'created_at')
    list_filter = ('created_at',)
# DIQQAT: Bu yerda endi admin.site.register(Teacher) yoki (Student) YOZILMAYDI!pip install google-genai