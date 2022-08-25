from typing import Type

from django.views import View
from django.views.generic import TemplateView

from condor_navigator.page import CondorPage


class IndexPage(CondorPage):
    def __init__(self, name=None, template_name=None):
        super().__init__(name, login_required=False)
        self._template_name = "pages/index.html" if template_name is None else template_name

    @property
    def route(self):
        return f''

    @property
    def route_name(self):
        return super().route_name


    def _get_view(self, *args, **kwargs) -> Type[View]:
        CondorViewMixin = self.get_condor_view_mixin()
        class CondorListView(CondorViewMixin, TemplateView):
            template_name = self._template_name
        return CondorListView
