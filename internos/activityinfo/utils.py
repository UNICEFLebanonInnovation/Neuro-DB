import os
import csv
import datetime
import subprocess


def r_script_command_line(script_name, args):
    command = 'Rscript'
    path = os.path.dirname(os.path.abspath(__file__))
    path2script = path+'/RScripts/'+script_name

    cmd = [command, path2script, str(args)]

    try:
        subprocess.check_output(cmd, universal_newlines=True)
    except subprocess.CalledProcessError as e:
        print("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))
        return 0

    return 1


def read_data_from_file(ai_id):
    from internos.activityinfo.models import ActivityReport
    month = datetime.datetime.now().strftime("%M")
    month_name = datetime.datetime.now().strftime("%B")
    path = os.path.dirname(os.path.abspath(__file__))
    path2file = path+'/AIReports/'+str(ai_id)+'_ai_data.csv'

    data = []
    with open(path2file) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            instance, created = ActivityReport.objects.get_or_create(
                month=month,
                database=row['database'],
                site_id=row['site.id'],
                report_id=row['report.id'],
                database_id=row['database.id'],
                partner_id=row['partner.id'],
                indicator_id=row['indicator.id'],
                indicator_name=unicode(row['indicator.name'], errors='replace'),
            )
            if instance:
                instance.month_name = month_name
                instance.partner_label = row['partner.label'] if 'partner.label' in row['partner.label'] else ''
                instance.location_adminlevel_caza_code = row['location.adminlevel.caza.code'] if 'location.adminlevel.caza.code' in row else ''
                instance.location_adminlevel_caza = unicode(row['location.adminlevel.caza'], errors='replace') if 'location.adminlevel.caza' in row else ''
                instance.partner_description = unicode(row['partner.description'], errors='replace') if 'partner.description' in row else ''
                instance.form = row['form'] if 'form' in row else ''
                instance.governorate = row['Governorate'] if 'Governorate' in row else ''
                instance.location_longitude = row['location.longitude'] if 'location.longitude' in row else ''
                instance.form_category = row['form.category'] if 'form.category' in row else ''
                instance.indicator_units = row['indicator.units'] if 'indicator.units' in row else ''
                instance.project_description = unicode(row['project.description'], errors='replace') if 'project.description' in row else ''
                instance.location_adminlevel_cadastral_area_code = row['location.adminlevel.cadastral_area.code'] if 'location.adminlevel.cadastral_area.code' in row else ''
                instance.location_name = unicode(row['location.name'], errors='replace') if 'location.name' in row else ''
                instance.project_label = unicode(row['project.label'], errors='replace') if 'project.label' in row else ''
                instance.location_adminlevel_governorate_code = row['location.adminlevel.governorate.code'] if 'location.adminlevel.governorate.code' in row else ''
                instance.end_date = row['end_date'] if 'end_date' in row else ''
                instance.lcrp_appeal = row['LCRP Appeal'] if 'LCRP Appeal' in row else ''
                instance.indicator_value = row['indicator.value'] if 'indicator.value' in row else ''
                instance.funded_by = row['Funded_by'] if 'Funded_by' in row else ''
                instance.location_latitude = row['location.latitude'] if 'location.latitude' in row else ''
                instance.indicator_category = row['indicator.category'] if 'indicator.category' in row else ''
                instance.location_alternate_name = row['location.alternate_name'] if 'location.alternate_name' in row else ''
                instance.start_date = row['start_date'] if 'start_date' in row else ''
                instance.location_adminlevel_cadastral_area = unicode(row['location.adminlevel.cadastral_area'], errors='replace') if 'location.adminlevel.cadastral_area' in row else ''
                instance.location_adminlevel_governorate = row['location.adminlevel.governorate'] if 'location.adminlevel.governorate' in row else ''
                # instance.row_data = row
                instance.save()
            data.append(row)

    return data
