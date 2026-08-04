import os
from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django.db.models import Q, F
from django.http import HttpResponse
from django.utils.translation import get_language, gettext as _
from .models import News, Teacher, Grade, Student, Graduate, SchoolStat, GalleryImage, ExamSession
# PDF yaratish uchun kutubxonalar
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import landscape, A4 # MANA SHU QATOR XATONI TUZATADI

# AI IMTIHON TUZILMASI — fanlar YAGONA manba (ai_test_view va apply.html shu yerdan oladi)
AI_EXAM_STRUCTURE = [
    {
        'key': 'aniq',
        'name': "5-sinf Aniq fanlar",
        'icon': 'fa-calculator',
        'color': 'yellow',
        'subjects': [
            ('Matematika', 20, 'fa-calculator'),
            ('Tanqidiy fikrlash', 10, 'fa-brain'),
            ('Ingliz tili', 15, 'fa-language'),
        ],
    },
    {
        'key': 'tabiiy',
        'name': "7-sinf Tabiiy fanlar",
        'icon': 'fa-microscope',
        'color': 'green',
        'subjects': [
            ('Science', 30, 'fa-seedling'),
            ('Ingliz tili', 15, 'fa-language'),
        ],
    },
]
AI_EXAMS_BY_KEY = {e['key']: e for e in AI_EXAM_STRUCTURE}


# 1. BOSH SAHIFA
def home(request):
    """Barcha asosiy ma'lumotlarni bosh sahifaga chiqarish"""
    news = News.objects.all().order_by('-created_at')[:3]
    teachers = Teacher.objects.all()
    director = Teacher.objects.filter(position__icontains='direktor').first()
    stats = SchoolStat.objects.all()
    gallery_images = GalleryImage.objects.all().order_by('-created_at')[:10]
    return render(request, 'main/index.html', {
        'news': news, 
        'teachers': teachers, 
        'director': director,
        'stats': stats,
        'gallery_images': gallery_images
    })

# 2. QIDIRUV TIZIMI
# main/views.py dagi search_results funksiyasini shu bilan almashtir:

def search_results(request):
    query = request.GET.get('q', '')
    if query:
        # icontains - bu katta-kichik harfni farqlamay qidiradi
        news_list = News.objects.filter(Q(title__icontains=query) | Q(content__icontains=query))
        teachers_list = Teacher.objects.filter(Q(full_name__icontains=query) | Q(subject__icontains=query))
        students_list = Student.objects.filter(Q(full_name__icontains=query) | Q(id_number__icontains=query))
    else:
        news_list = teachers_list = students_list = []
    
    return render(request, 'main/search_results.html', {
        'query': query,
        'news': news_list,       # Template-da 'news' deb ishlatamiz
        'teachers': teachers_list, # Template-da 'teachers' deb ishlatamiz
        'students': students_list  # Template-da 'students' deb ishlatamiz
    })
# 3. PORTFOLIO - SINFLAR RO'YXATI
def portfolio_grades(request):
    """Sinflar portfoliosini ko'rsatish"""
    grades = Grade.objects.all().order_by('name')
    return render(request, 'main/portfolio.html', {'grades': grades})

# 4. SINF TAFSILOTLARI VA TARTIBLASH
# views.py ichidagi grade_detail funksiyasini shu bilan almashtir:

# views.py ichidagi grade_detail funksiyasini shu bilan yangila:

def grade_detail(request, grade_id):
    grade = get_object_or_404(Grade, id=grade_id)
    
    # 1. SINFIDAGI JAMI O'QUVCHILAR SONI (Qidiruvdan oldin hisoblaymiz)
    total_students_count = Student.objects.filter(grade=grade).count()
    
    sort_by = request.GET.get('sort', 'name')
    query = request.GET.get('q', '')
    
    # 2. O'quvchilarni olish
    students = Student.objects.filter(grade=grade)
    
    # 3. Qidiruv filtri (faqat jadval uchun)
    if query:
        students = students.filter(
            Q(full_name__icontains=query) | Q(id_number__icontains=query)
        )
    
    # 4. Saralash
    mapping = {'name': 'full_name', 'score': '-admission_score', 'age': 'birth_date'}
    order_field = mapping.get(sort_by, 'full_name')
    students = students.order_by(order_field)
    
    return render(request, 'main/grade_students.html', {
        'grade': grade, 
        'students': students,
        'total_count': total_students_count, # BU TEPADAGI BANNER UCHUN
        'current_sort': sort_by,
        'search_query': query
    })    
    grade = get_object_or_404(Grade, id=grade_id)
    
    # 1. URL'dan sort va qidiruv parametrlarini olamiz
    sort_by = request.GET.get('sort', 'name')
    query = request.GET.get('q', '')
    
    # 2. Shu sinfga tegishli o'quvchilarni olamiz
    students = Student.objects.filter(grade=grade)
    
    # 3. Agar qidiruv so'zi bo'lsa, filtrlash (Ismi yoki ID raqami bo'yicha)
    if query:
        students = students.filter(
            Q(full_name__icontains=query) | Q(id_number__icontains=query)
        )
    
    # 4. Saralash mantiqi
    mapping = {
        'name': 'full_name',
        'score': '-admission_score',
        'age': 'birth_date',
    }
    order_field = mapping.get(sort_by, 'full_name')
    students = students.order_by(order_field)
    
    return render(request, 'main/grade_students.html', {
        'grade': grade, 
        'students': students,
        'current_sort': sort_by,
        'search_query': query # Qidiruv matnini qaytaramiz
    })
    """Sinfdagi o'quvchilarni saralash bilan ko'rsatish"""
    grade = get_object_or_404(Grade, id=grade_id)
    sort_by = request.GET.get('sort', 'name')
    
    # Saralash xaritasi
    mapping = {
        'name': 'full_name',
        'score': '-admission_score', # Kattadan kichikka
        'age': 'birth_date',
    }
    
    order_field = mapping.get(sort_by, 'full_name')
    students = Student.objects.filter(grade=grade).order_by(order_field)
    
    return render(request, 'main/grade_students.html', {
        'grade': grade, 
        'students': students,
        'current_sort': sort_by
    })

# 5. O'QUVCHI PROFILI
def student_detail(request, pk):
    """O'quvchi shaxsiy sahifasi va yutuqlari"""
    student = get_object_or_404(Student, pk=pk)
    # Achievements_list - bu Achievement modelidagi related_name
    achievements = student.achievements_list.all()
    return render(request, 'main/student_detail.html', {
        'student': student,
        'achievements': achievements
    })

# 8. YANGILIKLAR TAFSILOTI
def news_detail(request, pk):
    """Yangilik batafsil sahifasi va 10 tagacha rasmlar galereyasi"""
    item = get_object_or_404(News, pk=pk)

    # LAYK: DB'da umumiy hisob, session'da foydalanuvchining holati
    likes_session = request.session.get('news_likes', {})
    liked = likes_session.get(str(pk), False)
    if request.method == "POST":
        if liked:
            News.objects.filter(pk=pk, likes__gt=0).update(likes=F('likes') - 1)
            liked = False
        else:
            News.objects.filter(pk=pk).update(likes=F('likes') + 1)
            liked = True
        likes_session[str(pk)] = liked
        request.session['news_likes'] = likes_session
        request.session.modified = True

    # KO'RISHLAR: DB'da hisoblanadi
    News.objects.filter(pk=pk).update(views=F('views') + 1)
    item.refresh_from_db()

    similar_news = News.objects.exclude(pk=pk).order_by('-created_at')[:3]
    return render(request, 'main/news_detail.html', {
        'item': item,
        'views_count': item.views,
        'liked': liked,
        'likes_count': item.likes,
        'similar_news': similar_news,
    })

# 10. BITIRUVCHILAR RO'YXATI
def graduates_list(request):
    graduates = Graduate.objects.all().order_by('-year')
    return render(request, 'main/graduates.html', {'graduates': graduates})

# 11. ALOQA VA QABUL
def contact(request): return render(request, 'main/contact.html')
def apply_info(request):
    return render(request, 'main/apply.html', {'exams': AI_EXAM_STRUCTURE})
# main/views.py ga qo'shing:

def news_all(request):
    """Barcha yangiliklar sahifasi"""
    all_news = News.objects.all().order_by('-created_at')
    news_likes = request.session.get('news_likes', {})
    news_meta = [
        {
            'item': item,
            'views': item.views,
            'likes': item.likes,
            'liked': news_likes.get(str(item.pk), False),
        }
        for item in all_news
    ]
    return render(request, 'main/news_all.html', {'news': news_meta})
def teacher_detail(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    achievements = teacher.achievements_list.all() # Sertifikatlarni olamiz
    return render(request, 'main/teacher_detail.html', {'teacher': teacher, 'achievements': achievements})
def gallery_list(request):
    images = GalleryImage.objects.all().order_by('-created_at')
    return render(request, 'main/gallery.html', {'images': images})
from google import genai
import json
import re # Matnni tozalash uchun
from concurrent.futures import ThreadPoolExecutor, as_completed
from django.shortcuts import render
from .models import ExamSession

_genai_client = None


def _get_genai_client():
    global _genai_client
    if _genai_client is None:
        _genai_client = genai.Client(api_key=settings.GEMINI_API_KEY)
    return _genai_client


def _genai_json(prompt):
    """Gemini'ga bitta so'rov yuborib, sof JSON qaytaradi."""
    response = _get_genai_client().models.generate_content(model='gemini-3.1-flash-lite', contents=prompt)
    return json.loads(re.sub(r'```json|```', '', response.text).strip())


def _generate_questions(exam_name, subject_splits, target_lang):
    """Fanlarni PARALLEL (3 ta so'rov bir vaqtda) ishlatib tezroq test tuzadi."""
    total = sum(count for _, count in subject_splits)

    def build_prompt(subject, count):
        return f"""
    Vazifa: Oltiariq Ixtisoslashtirilgan maktabi "{exam_name}" yo'nalishi uchun "{subject}" fanidan aynan {count} ta savol tuzing. Jami imtihonda {total} ta savol bo'ladi.
    Bu savollar iqtidorli o'quvchilar uchun — {exam_name} yosh darajasidagi eng qiyin (olimpiada darajasidagi) savollar bo'lsin. Har bir savolga 4 ta variant (a, b, c, d), to'g'ri javob va qisqacha tushuntirish qo'shing.
    Tili: {target_lang}.
    QIYINLIK TALABLARI:
    1. Savollar BEVOSITA oson ko'rinadigan bo'lmasin — o'quvchi bir necha bosqichli fikrlash, taqqoslash yoki mantiq ishlatishi SHART bo'lsin. Yodlangan ta'riflarni emas, bilimni QO'LLASH va TAHLIL talab qiladigan savollar bering.
    2. Noto'g'ri variantlar (distraktorlar) ham O'XSHASH va ISHONARLI bo'lsin — o'quvchi faqat variantlarga qarab emas, bilimi bilan hal qilsin. Variantlar bir-biriga yaqin va chalg'ituvchi bo'lsin.
    3. Ayrim savollarga keraksiz (chalg'ituvchi) ma'lumot qo'shing — o'quvchi qaysi ma'lumot muhimligini farqlay olishi kerak.
    4. Javobi bir so'z yoki bitta raqam bilan aniq ko'rinadigan "trivial" savollardan qoching.
    MUHIM QOIDA:
    1. To'g'ri javoblar FAQAT "A" bo'lmasin! To'g'ri javob variantlarini (a, b, c, d) harflari orasida TASODIFIY (random) taqsimlang.
    2. Format: FAQAT sof JSON qaytar. Boshqa hech narsa yozma.
    Shablon: [{{ "q": "savol", "a": "v1", "b": "v2", "c": "v3", "d": "v4", "correct": "variant_harfi", "explanation": "isbot(isbotni yaxshilab tushuntiring)" }}]
    """

    results = {}
    with ThreadPoolExecutor(max_workers=min(3, len(subject_splits))) as pool:
        futures = {pool.submit(_genai_json, build_prompt(subject, count)): subject for subject, count in subject_splits}
        for future in as_completed(futures):
            results[futures[future]] = future.result()

    merged = []
    for subject, _ in subject_splits:
        merged.extend(results[subject])
    return json.dumps(merged, ensure_ascii=False)


def _translate_questions(questions_json, target_lang):
    """Mavjud testni qayta TUZMAYDI, faqat tilini almashtiradi."""
    prompt = f"""
    Quyidagi imtihon savollarini "{target_lang}" ga tarjima qiling. Savollarning MAZNUNINI o'zgartirmang, faqat tilini almashtiring.
    "correct" maydonidagi variant harfini O'ZGARTIRMANG. Faqat "q", "a", "b", "c", "d", "explanation" matnlarini tarjima qiling.
    Variantlar soni va tartibi bir xil bo'lsin. FAQAT sof JSON qaytaring, boshqa hech narsa qo'shmang.
    {questions_json}
    """
    data = _genai_json(prompt)
    if not isinstance(data, list) or len(data) == 0:
        raise ValueError("Empty translation response")
    return json.dumps(data, ensure_ascii=False)


def ai_test_view(request, subject_type):
    """AI imtihon. Savollar session'da keshlanadi:
    - reload/sahifa qayta ochilganda → qayta tuzilmaydi
    - til almashtirilganda → qayta tuzilmaydi, faqat tili almashtiriladi
    """
    exam = AI_EXAMS_BY_KEY.get(subject_type)
    if exam is None:
        subject_type = 'aniq'
        exam = AI_EXAMS_BY_KEY['aniq']
    exam_name = _(exam['name'])
    subject_splits = [(_(name), qty) for name, qty, _icon in exam['subjects']]

    if request.method == "POST":
        # POST mantiqi (ball hisoblash)
        request.session.pop(f'ai_exam_{subject_type}', None)  # Yangi urinish uchun keshni tozalaymiz
        user_answers = request.POST
        questions_json = request.POST.get('questions_data')
        questions = json.loads(questions_json)
        
        results = []
        score = 0
        total = len(questions)
        for i, q in enumerate(questions, 1):
            user_ans = user_answers.get(f'q{i}')
            is_correct = user_ans == q['correct']
            if is_correct: score += 1
            results.append({
                'question': q['q'],
                'user_ans': q.get(user_ans, _("Javob berilmagan")),
                'correct_ans': q.get(q['correct']),
                'is_correct': is_correct,
                'explanation': q.get('explanation', _("Tushuntirish mavjud emas"))
            })
        
        percent = (score / total) * 100 if total > 0 else 0
        return render(request, 'main/test_result.html', {
            'score': score, 'total': total, 'percent': percent, 'results': results, 'subject': exam_name
        })

    # AI GENERATSIYA QISMI (GET REQUEST)
    current_lang = get_language()
    lang_map = {'uz': 'O‘zbek tilida', 'ru': 'на Русском языке', 'en': 'in English'}
    target_lang = lang_map.get(current_lang, 'O‘zbek tilida')
    cache_key = f'ai_exam_{subject_type}'

    error_msg = None
    questions = []
    clean_json = "[]"

    try:
        cached = request.session.get(cache_key)
        if cached and cached.get('lang') == current_lang:
            # Xuddi shu tildagi test allaqachon bor → tezda ko'rsatamiz
            clean_json = cached['questions_json']
            questions = json.loads(clean_json)
        elif cached:
            # Til o'zgardi → qayta TUZMAYMIZ, faqat tarjima qilamiz
            try:
                clean_json = _translate_questions(cached['questions_json'], target_lang)
                request.session[cache_key] = {'lang': current_lang, 'questions_json': clean_json}
            except Exception:
                clean_json = cached['questions_json']  # tarjima ishlamasa ham test yo'qolmaydi
            questions = json.loads(clean_json)
        else:
            # Birinchi marta → parallel generatsiya
            clean_json = _generate_questions(exam_name, subject_splits, target_lang)
            request.session[cache_key] = {'lang': current_lang, 'questions_json': clean_json}
            questions = json.loads(clean_json)
    except Exception as e:
        error_msg = str(e)
        questions = []; clean_json = "[]"
    
    return render(request, 'main/ai_test.html', {
        'questions': questions, 
        'questions_data': clean_json, 
        'subject': exam_name,
        'subject_type': subject_type,
        'error_msg': error_msg,
    })    
def ai_test_select(request):
    """Fan tanlash sahifasi"""
    return render(request, 'main/ai_test_select.html')
def generate_certificate(request):
    if request.method == "POST":
        full_name = request.POST.get('full_name').upper()
        score = request.POST.get('score')
        subject = request.POST.get('subject')
        lang = get_language()

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="certificate_{full_name}.pdf"'

        # Sertifikat uchun Landscape (Yotiq) A4 o'lchami
        p = canvas.Canvas(response, pagesize=landscape(A4))
        width, height = landscape(A4)

        # 1. SHABLONNI ORQA FONGA QO'YISH
        template_path = os.path.join(settings.BASE_DIR, 'main/static/main/img/cert_template.jpg')
        p.drawImage(template_path, 0, 0, width=width, height=height)

        # 2. SHRIFTLARNI SOZLASH
        font_path = os.path.join(settings.BASE_DIR, 'main/static/main/fonts/arial.ttf')
        font_bold_path = os.path.join(settings.BASE_DIR, 'main/static/main/fonts/arialbd.ttf')
        pdfmetrics.registerFont(TTFont('Arial', font_path))
        pdfmetrics.registerFont(TTFont('Arial-Bold', font_bold_path))
        
        # 3. ISM-FAMILIYANI YOZISH (Markazda)
        p.setFillColor(HexColor('#0f172a'))
        p.setFont("Arial-Bold", 40)
        p.drawCentredString(width/2, height/2 - 1*cm, full_name)

        # 4. TABRIKNOMA MATNI (Tilda qarab o'zgaradi)
        cert_texts = {
            'uz': f"{subject} fani bo'yicha imtihonda {score} ball to'plagani uchun berildi.",
            'ru': f"Выдан за получение {score} баллов на экзамене по предмету {subject}.",
            'en': f"Awarded for scoring {score} points in the {subject} exam.",
        }
        p.setFont("Arial", 18)
        p.drawCentredString(width/2, height/2 - 3*cm, cert_texts.get(lang, cert_texts['uz']))

        # 5. SANA VA MUALLIF
        p.setFont("Arial", 12)
        p.drawString(4*cm, 3*cm, "24.07.2026")
        p.drawRightString(width - 4*cm, 3*cm, "Abdurahmon Maxsutaliyev")

        p.showPage()
        p.save()
        return response
