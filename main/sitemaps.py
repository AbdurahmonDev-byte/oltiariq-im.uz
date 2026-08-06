# main/sitemaps.py

from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import News, Student, Teacher, Graduate

class StaticViewSitemap(Sitemap):
    priority = 1.0
    changefreq = 'daily'
    def items(self):
        return ['home', 'news_all', 'gallery_list', 'contact', 'apply', 'graduates', 'ai_test_select', 'portfolio']
    def location(self, item):
        return reverse(item)

class NewsSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8
    def items(self): 
        # Tartiblash qo'shildi: yangilari tepada chiqadi
        return News.objects.all().order_by('-created_at')

class StudentSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.6
    def items(self): 
        # Tartiblash qo'shildi: Alifbo bo'yicha
        return Student.objects.all().order_by('full_name')

class TeacherSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.7
    def items(self): 
        # Tartiblash qo'shildi: Ismi bo'yicha
        return Teacher.objects.all().order_by('full_name')

class GraduateSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.7
    def items(self):
        return Graduate.objects.all().order_by('full_name')