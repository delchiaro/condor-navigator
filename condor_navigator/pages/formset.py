from abc import ABC
from typing import Type

from bootstrap_modal_forms.generic import BSModalCreateView, BSModalReadView, BSModalUpdateView, BSModalDeleteView
from bootstrap_modal_forms.mixins import CreateUpdateAjaxMixin
from django.db.models import Model, ManyToManyField, QuerySet
from django.urls import reverse_lazy, re_path
from django.views import View
from django.views.generic import ListView
from django_addanother.views import CreatePopupMixin, UpdatePopupMixin
from extra_views import FormSetView, CreateWithInlinesView, UpdateWithInlinesView, InlineFormSetFactory, \
    ModelFormSetView, InlineFormSetView

from condor_navigator.forms import condor_bsmf_form
from condor_navigator.page import CondorModelPage


class FormSetpage(CondorModelPage):
    def __init__(self, model: Type[Model], page_name=None, paginated_by=30, template_name=None,
                 fields=None, excluded_fields=('id',)):
        super().__init__(model, page_name)
        self._paginated_by = paginated_by
        self._template_name = "pages/formset.html" if template_name is None else template_name
        self._fields = "__all__" if fields is None else fields
        self._excluded_fields = tuple() if excluded_fields is None else excluded_fields
        self.title = self.title

    @property
    def fields(self):
        return self._fields

    @property
    def excluded_fields(self):
        return self._excluded_fields

    @property
    def route(self):
        return f'{self.name}_formset'

    @property
    def route_name(self):
        return super().route_name + '_formset'


    @property
    def paths(self, *args, **kwargs):
        filtered_path = re_path(f'{self.route}', self._get_view(*args, **kwargs).as_view(), name=self.route_name)
        return [filtered_path]

    def _get_view(self, *args, **kwargs) -> Type[View]:
        CondorViewMixin = self.get_condor_view_mixin()

        class CondorFormSetView(CondorViewMixin, InlineFormSetView):
            navigator = self.navigator
            model = self._model
            form_class = condor_bsmf_form(self._model, condor_fields=self._fields)
            template_name = self._template_name

            def get_key_filter_kwargs(iself):
                return {key: iself.kwargs[key] for key in self.model_key_names() if key in iself.kwargs.keys()}

            def get_queryset(iself):
                queryset = CondorFormSetView.model.objects.all()
                filter_kwargs = iself.get_key_filter_kwargs()
                if len(filter_kwargs) > 0:
                    return queryset.filter(**filter_kwargs)
                return queryset

            def get_context_data(iself, **kwargs):
                context = super().get_context_data(**kwargs)
                filter_kwargs = iself.get_key_filter_kwargs()
                filter_str = ', '.join([f"{k}={v}" for k, v in filter_kwargs.items()])
                context['query'] = filter_str
                context['page'] = self
                context['related_fk_models'] = {fk.id: fk.model for fk in self.model_reverse_fks()}
                return context

        return CondorFormSetView

