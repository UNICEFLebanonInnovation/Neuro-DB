__author__ = 'achamseddine'

import time
import json
import tablib
import httplib
from import_export.formats import base_formats
from internos.taskapp.celery import app
from django.utils.translation import ugettext as _


@app.task
def import_2ndshift_data(params=None):
    from .models import ImportedData

    # ImportedData.objects.filter(type='2nd-shift').delete()
    # ImportedData.objects.filter(type__isnull=True).delete()

    for i in range(36, 320):
        offset = 500 * i
        print(i)
        result = get_data('mdb2.azurewebsites.net', '/api/import-enrollment/?year=2&max=500&offset='+str(offset))
        result = json.loads(result)
        for item in result:
            ImportedData.objects.create(enrollment=item, type='2nd-shift')
        print('DONE')


@app.task
def import_attendance_data(params=None):
    from .models import ImportedData

    ImportedData.objects.filter(type='attendance').delete()
    month = '2'
    year = '2018'
    max_values = 50

    for i in range(0, 200):
        offset = max_values * i
        print(i)
        result = get_data('mdb2.azurewebsites.net', '/api/export-attendances/?year=2&max=50&offset='+str(offset)+'&month='+month+'&year='+year)
        result = json.loads(result)
        for item in result:
            ImportedData.objects.create(enrollment=item, type='attendance')
        print('DONE')


@app.task
def export_2ndshift_data():
    from .models import ImportedData

    enrollments = ImportedData.objects.filter(enrollment__education_year='2017/2018')
    print(ImportedData.objects.filter(enrollment__education_year='2017/2018').count())
    print(ImportedData.objects.filter(enrollment__education_year='2016/2017').count())
    print(ImportedData.objects.filter(enrollment__education_year__isnull=True).count())
    # enrollments = ImportedData.objects.all()[0:120000]
    # enrollments = ImportedData.objects.all()[120000:240000]
    # enrollments = ImportedData.objects.all()[240000:300000]

    data = tablib.Dataset()
    data.headers = [

        'created',
        'modified',
        'dropout_status',
        'disabled',
        'moved',

        'Last non formal education - result',
        'Last non formal education - round',
        'Is the child participated in an ALP/2016-2 program',

        'Last formal education - result',
        'Last formal education - year',
        'Last formal education - school shift',
        'Last formal education - school type',
        'Last formal education - school',
        'Last formal education - CERD',
        'Last formal education - level',

        'Serial number in previous school',

        'Last attendance date',
        'last absence date',

        'Current Section',
        'Current Class',
        'Education year',

        'Phone prefix',
        'Phone number',
        'Student living address',
        'Student ID Number',
        'Student ID Type',
        'Registered in UNHCR',
        'Mother nationality',
        'Mother fullname',
        'Student nationality',
        'Student age',
        # 'Student birthday',
        'Place of birth',
        'year',
        'month',
        'day',
        'Sex',
        'Student first name',
        'Student father name',
        'Student last name',
        # 'Student fullname',

        'First time registered?',
        'Student outreached?',
        'Have barcode with him?',
        'Outreach barcode',

        'Registration date',
        'School',
        'School number',
        'District',
        'Governorate'
    ]

    content = []

    for enrollment in enrollments:
        line = enrollment.enrollment
        # if line['education_year'] == '2016/2017':
        #     continue
        content = [
            line['created'],
            line['modified'],
            line['dropout_status'],
            line['disabled'],
            line['moved'],

            line['last_informal_edu_final_result_name'],
            line['last_informal_edu_round_name'],
            line['participated_in_alp'],

            line['last_year_result'],
            line['last_education_year'],
            line['last_school_shift'],
            line['last_school_type'],
            line['last_school_name'],
            line['last_school_number'],
            line['last_education_level_name'],

            line['number_in_previous_school'],

            line['last_attendance_date'],
            line['last_absent_date'],

            line['section_name'],
            line['classroom_name'],
            line['education_year'],

            line['student_phone_prefix'],
            line['student_phone'],
            line['student_address'],
            line['student_id_number'],
            line['student_id_type'],
            line['student_registered_in_unhcr'],
            line['student_mother_nationality'],
            line['student_mother_fullname'],
            line['student_nationality'],
            line['student_age'],
            line['student_place_of_birth'],
            line['student_birthday_year'],
            line['student_birthday_month'],
            line['student_birthday_day'],
            line['student_sex'],
            line['student_first_name'],
            line['student_father_name'],
            line['student_last_name'],
            # line['student_fullname'],

            line['new_registry'],
            line['student_outreached'],
            line['have_barcode'],
            line['outreach_barcode'],

            line['registration_date'],
            line['school_name'],
            line['school_number'],
            line['district'],
            line['governorate'],
        ]
        data.append(content)

    file_format = base_formats.XLSX()
    data = file_format.export_data(data)
    return data


@app.task
def export_attendance_data(params=None, return_data=False):
    from .models import ImportedData

    queryset = ImportedData.objects.filter(type='attendance' )

    data = tablib.Dataset()

    data.headers = [
        _('School number'),
        _('School'),
        _('School type'),
        _('Education year/ALP round'),

        _('District'),
        _('Governorate'),

        _('Attendance date'),
        _('Validation status'),
        _('Validation date'),
        _('Close reason'),
        _('Exam day'),

        _('Level'),
        _('Section'),

        _('Student fullname'),
        _('Sex'),
        _('Age'),
        _('Attendance status'),
        _('Absence reason')
    ]

    content = []
    for enrollment in queryset:
        line = enrollment.enrollment
        # try:
        #     print(line['students'])
        #     print(type(line['students']))
        # except Exception:
        #     print('---------------')
        #     print(line)
        #     continue
        if not line['students']:
            continue
        for level_section in line['students']:
            attendances = line['students'][level_section]
            students = attendances['students']
            for student in students:
                content = [
                    line['school_number'],
                    line['school_name'],
                    line['school_type'],
                    line['education_year'] if line['education_year'] else line['alp_round'],

                    line['district'],
                    line['governorate'],

                    line['attendance_date'],
                    line['validation_date'],
                    line['validation_status'],
                    line['close_reason'],
                    attendances['exam_day'],

                    student['level_name'],
                    student['section_name'],

                    student['student_fullname'],
                    student['student_sex'],
                    student['student_age'],
                    student['status'],
                    student['absence_reason'] if 'absence_reason' in student else '',
                ]
                data.append(content)

    file_format = base_formats.XLSX()
    data = file_format.export_data(data)
    file_object = open("attendances_data.xlsx", "w")
    file_object.write(data)
    file_object.close()


def get_data(url, apifunc, protocol='HTTPS'):

    token = 'Token 559e40243414a5d8794364e7efa5f527ef62a24c'
    headers = {"Content-type": "application/json", "Authorization": token}

    if protocol == 'HTTPS':
        conn = httplib.HTTPSConnection(url)
    else:
        conn = httplib.HTTPConnection(url)

    conn.request('GET', apifunc, "", headers)
    response = conn.getresponse()
    result = response.read()

    if not response.status == 200:
        if response.status == 400 or response.status == 403:
            raise Exception(str(response.status) + response.reason + response.read())
        else:
            raise Exception(str(response.status) + response.reason)

    conn.close()

    return result
