from suit.apps import DjangoSuitConfig
from suit.menu import ParentItem, ChildItem


#  https://github.com/darklow/django-suit/blob/v2/suit/apps.py
class SuitConfig(DjangoSuitConfig):
    # layout = 'vertical'
    # verbose_name = 'Neuro-DB'
    # form_inlines_hide_original = True
    menu = (
        ParentItem('Dashboard', url='/', icon='fa fa-list'),
        ParentItem('Activity Info', children=[
            ChildItem(model='activityinfo.database'),
            ChildItem(model='activityinfo.activity'),
            ChildItem(model='activityinfo.indicator'),
            ChildItem(model='activityinfo.partner'),
            ChildItem(model='activityinfo.attributegroup'),
            ChildItem(model='activityinfo.attribute'),
            ChildItem(model='activityinfo.activityreport'),
        ], icon='fa fa-list'),
        ParentItem('Users', children=[
            ChildItem('Users', model='users.user'),
            ChildItem('Sections', model='users.section'),
            ChildItem('Groups', 'auth.group'),
        ], icon='fa fa-users'),
        ParentItem('Right Side Menu', children=[
            ChildItem('Password change', url='admin:password_change'),

        ], align_right=True, icon='fa fa-cog'),
    )

    # def ready(self):
    #     super(SuitConfig, self).ready()
    #
    #     # DO NOT COPY FOLLOWING LINE
    #     # It is only to prevent updating last_login in DB for demo app
    #     self.prevent_user_last_login()

    # def prevent_user_last_login(self):
    #     """
    #     Disconnect last login signal
    #     """
    #     from django.contrib.auth import user_logged_in
    #     from django.contrib.auth.models import update_last_login
    #     user_logged_in.disconnect(update_last_login)
