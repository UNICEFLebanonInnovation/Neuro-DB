from django.apps import AppConfig
from watson import search as watson


class InternosConfig(AppConfig):
    name = "internos"
    def ready(self):
        watson.register(self.get_model("internos.activityinfo.indicator"))


# from suit.apps import DjangoSuitConfig
# from suit.menu import ParentItem, ChildItem


#  https://github.com/darklow/django-suit/blob/v2/suit/apps.py
# class SuitConfig(DjangoSuitConfig):
#     menu = (
#         ParentItem('Dashboard', url='/', icon='fa fa-list'),
#         ParentItem('Winterization', children=[
#             ChildItem('Programme', model='winterization.programme'),
#             ChildItem('Assessment', model='winterization.assessment'),
#         ], icon='fa fa-users'),
#         ParentItem('Activity Info', children=[
#             ChildItem(model='activityinfo.reportingyear', label='Reporting Years'),
#             ChildItem(model='activityinfo.indicatortag', label='Indicator Tags'),
#             ChildItem(model='activityinfo.database', label='Databases'),
#             ChildItem(model='activityinfo.activity'),
#             ChildItem(model='activityinfo.indicator'),
#             ChildItem(model='activityinfo.partner'),
#             ChildItem(model='activityinfo.attributegroup'),
#             ChildItem(model='activityinfo.attribute'),
#             ChildItem(model='activityinfo.activityreport'),
#             ChildItem(model='activityinfo.liveactivityreport'),
#         ], icon='fa fa-list'),
#         ParentItem('eTools', children=[
#             ChildItem(model='etools.partnerorganization'),
#             ChildItem(model='etools.agreement'),
#             ChildItem(model='etools.pca'),
#             ChildItem(model='etools.travel'),
#             ChildItem(model='etools.engagement'),
#         ], icon='fa fa-list'),
#         ParentItem('Users', children=[
#             ChildItem('Users', model='users.user'),
#             ChildItem('Sections', model='users.section'),
#             ChildItem('Offices', model='users.office'),
#             ChildItem('Groups', 'auth.group'),
#         ], icon='fa fa-users'),
#         ParentItem('Right Side Menu', children=[
#             ChildItem('Password change', url='admin:password_change'),
#
#         ], align_right=True, icon='fa fa-cog'),
#     )
