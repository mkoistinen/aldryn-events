import datetime

from django.conf.urls import patterns, url
from django.utils.dates import MONTHS
from django.utils.translation import ugettext_lazy as _

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from .views import EventDatesView
from .utils import build_calendar
from .models import UpcomingPluginItem, Event, EventListPlugin
from .forms import UpcomingPluginForm


class UpcomingPlugin(CMSPluginBase):
    render_template = False
    name = _('Upcoming')
    module = _('Events')
    model = UpcomingPluginItem
    form = UpcomingPluginForm

    def render(self, context, instance, placeholder):
        context['events'] = Event.objects.upcoming(count=instance.latest_entries)
        self.render_template = 'aldryn_events/plugins/upcoming/%s/upcoming.html' % instance.style
        return context

plugin_pool.register_plugin(UpcomingPlugin)


class EventListCMSPlugin(CMSPluginBase):
    render_template = False
    module = _('Events')
    name = _('List')
    model = EventListPlugin

    def render(self, context, instance, placeholder):
        self.render_template = 'aldryn_events/plugins/list/%s/list.html' % instance.style
        context['instance'] = instance
        context['events'] = instance.events.all()
        return context

plugin_pool.register_plugin(EventListCMSPlugin)


class CalendarPlugin(CMSPluginBase):
    render_template = 'aldryn_events/plugins/calendar.html'
    name = _('Calendar')
    module = _('Events')
    cache = False

    def render(self, context, instance, placeholder):
        year = context.get('event_year')
        month = context.get('event_month')

        if not all([year, month]):
            year = str(datetime.datetime.today().year)
            month = str(datetime.datetime.today().month)

        current_date = datetime.date(day=1, month=int(month), year=int(year))

        context['days'] = build_calendar(year, month)
        context['current_date'] = current_date
        context['last_month'] = current_date + datetime.timedelta(days=-1)
        context['next_month'] = current_date + datetime.timedelta(days=35)
        context['calendar_label'] = u'%s %s' % (MONTHS.get(int(month)), year)

        return context

    def get_plugin_urls(self):
        return patterns('',
            url(r'^get-dates/$', EventDatesView.as_view(), name='get-calendar-dates'),
            url(r'^get-dates/(?P<year>[0-9]+)/(?P<month>[0-9]+)/$', EventDatesView.as_view(), name='get-calendar-dates'),
        )


plugin_pool.register_plugin(CalendarPlugin)