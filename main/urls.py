from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.search_results, name='search'),
    path('ai-test/', views.ai_test_select, name='ai_test_select'),
    path('ai-test/start/<str:subject_type>/', views.ai_test_view, name='ai_test'),
    
    # YANGILIKLAR
    path('news/all/', views.news_all, name='news_all'),
    path('news/<int:pk>/', views.news_detail, name='news_detail'),
    
    # GALEREYA
    path('gallery/', views.gallery_list, name='gallery_list'), 
    
    # PORTFOLIO VA SINFLAR
    path('portfolio/', views.portfolio_grades, name='portfolio'),
    path('portfolio/grade/<int:grade_id>/', views.grade_detail, name='grade_detail'),
    path('student/<int:pk>/', views.student_detail, name='student_detail'),
    path('teacher/<int:pk>/', views.teacher_detail, name='teacher_detail'),
    path('graduate/<int:pk>/', views.graduate_detail, name='graduate_detail'),
    
    # BOSHQA
    path('graduates/', views.graduates_list, name='graduates'),
    path('contact/', views.contact, name='contact'),
    path('apply/', views.apply_info, name='apply'),
    
    # ID KARTA VA SERTIFIKAT
    path('generate-certificate/', views.generate_certificate, name='generate_certificate'),
]