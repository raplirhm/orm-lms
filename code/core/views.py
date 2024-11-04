from django.shortcuts import render, HttpResponse
from django.http.response import JsonResponse


from core.models import Course, CourseContent, CourseMember, User

# Create your views here.
def index(request):
    return HttpResponse("<h1>Selamat Datang di LMS</h1>")


def allCourse(request):
    allCourse = Course.objects.all().select_related('teacher')
    result = []
    for course in allCourse:
        record = {'id': course.id, 'name': course.name, 
                  'description': course.description, 
                  'price': course.price,
                  'teacher': {
                      'id': course.teacher.id,
                      'username': course.teacher.username,
                      'email': course.teacher.email,
                      'fullname': f"{course.teacher.first_name} {course.teacher.last_name}"
                  }}
        result.append(record)
    return JsonResponse(result, safe=False)

def userProfile(request, user_id):
    user = User.objects.get(pk=user_id)
    courses = Course.objects.filter(teacher=user)
    data_resp = {'username': user.username, 'email': user.email,
                 'fullname': f"{user.first_name}{user.last_name}"}
    data_resp['courses'] = []
    for course in courses:
        course_data = {'id': course.id, 'name': course.name,
                       'description': course.description,
                       'price': course.price}
        data_resp['courses'].append(course_data)

    return JsonResponse(data_resp, safe=False)

from django.db.models import Count, Min, Max, Avg

def courseStat(request):
    courses = Course.objects.all()
    statistic = courses.aggregate(course_count=Count('*'),
                               max_price=Max('price'),
                               min_price=Min('price'),
                               avg_price=Avg('price'))
    cheapest_list = Course.objects.filter(price=statistic['min_price'])
    expensive_list = Course.objects.filter(price=statistic['max_price'])
    popular_list = Course.objects.annotate(member_count=Count('coursemember'))\
    .order_by('-member_count')[:3]
    unpopuler_list = Course.objects.annotate(member_count=Count('coursemember'))\
    .order_by('member_count')[:3]

    data_resp = {
        'course_count': statistic['course_count'],
        'min_price': statistic['min_price'],
        'max_price': statistic['max_price'],
        'avg_price': statistic['avg_price'],
        'cheapest': [course.name for course in cheapest_list],
        'expensive': [course.name for course in expensive_list],
        'populer': [course.name for course in popular_list],
        'unpopuler': [course.name for course in unpopuler_list],

    }
    return JsonResponse(data_resp, safe=False)


def userStat(request):
    users = User.objects.all()
    stats = users.aggregate(user_count=Count('*'),)

    jumlah_user_membuat_course = User.objects.filter(course__isnull=False).distinct().count()
    jumlah_user_tidak_memiliki_course = User.objects.filter(course__isnull=True).count()
    rata_rata_course_per_user = User.objects.annotate(num_courses=Count('course')).aggregate(Avg('num_courses'))['num_courses__avg']
    user_terbanyak_courses = User.objects.filter(course__isnull=False).annotate(num_courses=Count('course')).order_by('-num_courses')[:1]
    user_not_courses = User.objects.filter(course__isnull=True).annotate(num_courses=Count('course')).order_by('-num_courses')[:1]



    data_resp = {
        'user_count': stats['user_count'],
        'jumlah_user_membuat_course': jumlah_user_membuat_course,
        'jumlah_user_tidak_memiliki_course': jumlah_user_tidak_memiliki_course,
        'rata_rata_course_per_user': rata_rata_course_per_user,
        'user_terbanyak_courses': [user.username for user in user_terbanyak_courses],
        'user_not_courses': [user.username for user in user_not_courses],


    }
    return JsonResponse(data_resp, safe=False)
