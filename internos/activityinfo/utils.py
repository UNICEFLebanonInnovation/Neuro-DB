import os
import csv
import datetime
import subprocess
from django.conf import settings


def r_script_command_line(script_name, ai_db):
    command = 'Rscript'
    path = os.path.dirname(os.path.abspath(__file__))
    path2script = path+'/RScripts/'+script_name

    cmd = [command, path2script, ai_db.username, ai_db.password, str(ai_db.ai_id)]

    try:
        subprocess.check_output(cmd, universal_newlines=True)
    except subprocess.CalledProcessError as e:
        print("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))
        return 0

    return 1


def read_data_from_file(ai_id):
    from internos.activityinfo.models import Database
    from internos.backends.models import ImportLog
    month_name = datetime.datetime.now().strftime("%B")

    try:
        ImportLog.objects.get(
            object_id=ai_id,
            object_type='AI',
            month=month_name,
            status=True)
        update_rows(ai_id)
    except ImportLog.DoesNotExist:
        ImportLog.objects.create(
            object_id=ai_id,
            object_name=Database.objects.get(ai_id=ai_id).name,
            object_type='AI',
            month=month_name,
            status=True)
        add_rows(ai_id)


def get_awp_code(name):
    try:
        if ' - ' in name:
            awp_code = name[:name.find(' - ')]
            # ai_indicator.awp_code = name[re.search('\d', name).start():name.find(':')]
        elif ': ' in name:
            awp_code = name[:name.find(': ')]
        else:
            awp_code = name[:name.find('#')]
    except TypeError as ex:
        awp_code = 'None'
    return awp_code


def add_rows(ai_id):
    from internos.activityinfo.models import ActivityReport

    month = datetime.datetime.now().strftime("%M")
    month_name = datetime.datetime.now().strftime("%B")
    path = os.path.dirname(os.path.abspath(__file__))
    path2file = path+'/AIReports/'+str(ai_id)+'_ai_data.csv'

    with open(path2file) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:

            ActivityReport.objects.create(
                month=month,
                database=row['database'],
                site_id=row['site.id'],
                report_id=row['report.id'],
                database_id=row['database.id'],
                partner_id=row['partner.id'],
                indicator_id=row['indicator.id'],
                indicator_name=unicode(row['indicator.name'], errors='replace'),
                indicator_awp_code=get_awp_code(unicode(row['indicator.name'], errors='replace')),
                month_name=month_name,
                partner_label=row['partner.label'] if 'partner.label' in row else '',
                location_adminlevel_caza_code=row[
                    'location.adminlevel.caza.code'] if 'location.adminlevel.caza.code' in row else '',
                location_adminlevel_caza=unicode(row['location.adminlevel.caza'],
                                                  errors='replace') if 'location.adminlevel.caza' in row else '',
                partner_description=unicode(row['partner.description'],
                                               errors='replace') if 'partner.description' in row else '',
                form=row['form'] if 'form' in row else '',
                governorate=row['Governorate'] if 'Governorate' in row else '',
                location_longitude=row['location.longitude'] if 'location.longitude' in row else '',
                form_category=row['form.category'] if 'form.category' in row else '',
                indicator_units=row['indicator.units'] if 'indicator.units' in row else '',
                project_description=unicode(row['project.description'],
                                               errors='replace') if 'project.description' in row else '',
                location_adminlevel_cadastral_area_code=row[
                    'location.adminlevel.cadastral_area.code'] if 'location.adminlevel.cadastral_area.code' in row else '',
                location_name=unicode(row['location.name'], errors='replace') if 'location.name' in row else '',
                project_label=unicode(row['project.label'], errors='replace') if 'project.label' in row else '',
                location_adminlevel_governorate_code=row[
                    'location.adminlevel.governorate.code'] if 'location.adminlevel.governorate.code' in row else '',
                end_date=row['end_date'] if 'end_date' in row else '',
                lcrp_appeal=row['LCRP Appeal'] if 'LCRP Appeal' in row else '',
                indicator_value=row['indicator.value'] if 'indicator.value' in row else '',
                funded_by=row['Funded_by'] if 'Funded_by' in row else '',
                location_latitude=row['location.latitude'] if 'location.latitude' in row else '',
                indicator_category=row['indicator.category'] if 'indicator.category' in row else '',
                location_alternate_name=row[
                    'location.alternate_name'] if 'location.alternate_name' in row else '',
                start_date=row['start_date'] if 'start_date' in row else '',
                location_adminlevel_cadastral_area=unicode(row['location.adminlevel.cadastral_area'],
                                                              errors='replace') if 'location.adminlevel.cadastral_area' in row else '',
                location_adminlevel_governorate=row[
                    'location.adminlevel.governorate'] if 'location.adminlevel.governorate' in row else '',
            )


def update_rows(ai_id):
    from internos.activityinfo.models import ActivityReport
    path = os.path.dirname(os.path.abspath(__file__))
    path2file = path+'/AIReports/'+str(ai_id)+'_ai_data.csv'

    with open(path2file) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            ActivityReport.objects.update(
                database_id=ai_id,
                indicator_units=row['indicator.units'] if 'indicator.units' in row else '',
                indicator_value=row['indicator.value'] if 'indicator.value' in row else '',
            )
