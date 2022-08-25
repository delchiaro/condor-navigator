from abc import ABC
from typing import Type

from bootstrap_modal_forms.generic import BSModalCreateView, BSModalReadView, BSModalUpdateView, BSModalDeleteView
from bootstrap_modal_forms.mixins import CreateUpdateAjaxMixin
from django.db.models import Model, ManyToManyField, QuerySet
from django.urls import reverse_lazy, re_path
from django.views import View
from django.views.generic import ListView
from django_addanother.views import CreatePopupMixin, UpdatePopupMixin

from condor_navigator.forms import condor_bsmf_form
from condor_navigator.page import CondorModelPage


class CondorModelFormPage(CondorModelPage, ABC):
    def __init__(self, model: Type[Model], page_name=None, form_fields=None, form_class=None):
        super().__init__(model, page_name)
        if form_class is not None:
            self.set_form(form_class)
        else:
            self.set_default_form(form_fields)

    def set_form(self, form_class):
        self._form = form_class

    def set_default_form(self, form_fields=None):
        fields = "__all__" if form_fields is None else form_fields
        self._form = condor_bsmf_form(self._model, condor_fields=fields)

    @property
    def form(self):
        return self._form

class CreatePage(CondorModelFormPage):
    def __init__(self, model: Type[Model], success_page: CondorModelPage, page_name=None,
                 form_fields=None, form_class=None, template_name=None):
        super().__init__(model, page_name, form_fields, form_class)
        self._success_page = success_page
        self._template_name = "pages/create.html" if template_name is None else template_name

    @property
    def route(self):
        return f'{self.name}/create'

    @property
    def route_name(self):
        return super().route_name + '_create'

    def _get_view(self, *args, **kwargs) -> Type[View]:
        CondorViewMixin = self.get_condor_view_mixin()

        class CondorCreateView(CondorViewMixin, CreateUpdateAjaxMixin, BSModalCreateView):
            model = self._model
            template_name = self._template_name
            success_message = 'Create success.'
            success_url = reverse_lazy(self._success_page.route_name)
            form_class = self.form

            def form_valid(self, form):
                result = super().form_valid(form)
                return result



        return CondorCreateView


class ReadPage(CondorModelFormPage):
    def __init__(self, model: Type[Model], page_name=None,
                 form_fields=None, form_class=None, template_name=None):
        super().__init__(model, page_name, form_fields, form_class)
        self._template_name = "pages/read.html" if template_name is None else template_name

    @property
    def route(self):
        return f'{self.name}/<int:pk>/read'

    @property
    def route_name(self):
        return super().route_name + '_read'

    def _get_view(self, *args, **kwargs) -> Type[View]:
        CondorViewMixin = self.get_condor_view_mixin()

        class CondorReadView(CondorViewMixin, CreatePopupMixin, UpdatePopupMixin, BSModalReadView):
            model = self._model
            template_name = self._template_name
            form_class = self.form  # .set_readonly(True)

            def get_context_data(iself, **kwargs):
                context = super().get_context_data(**kwargs)
                fields = {}
                fields_objects = self.model_forward_fields()
                fields_values = self.model_object_to_dict(context['object'])
                for fname, fvalue in fields_values.items():
                    if isinstance(fvalue, QuerySet):
                        fvalue = ", ".join(str(v) for v in fvalue)
                    # fields[fields_objects[fname].verbose_name] = fvalue
                    fields[fname] = (fields_objects[fname].verbose_name, fvalue)
                context['fields'] = fields
                return context

        return CondorReadView


class UpdatePage(CondorModelFormPage):
    def __init__(self, model: Type[Model], success_page: CondorModelPage, page_name=None,
                 form_fields=None, form_class=None, template_name=None):
        super().__init__(model, page_name, form_fields, form_class)
        self._success_page = success_page
        self._template_name = "pages/update.html" if template_name is None else template_name

    @property
    def route(self):
        return f'{self.name}/<int:pk>/update'

    @property
    def route_name(self):
        return super().route_name + '_update'

    def _get_view(self, *args, **kwargs) -> Type[View]:
        CondorViewMixin = self.get_condor_view_mixin()

        class CondorUpdateView(CondorViewMixin, CreatePopupMixin, UpdatePopupMixin, CreateUpdateAjaxMixin,
                               BSModalUpdateView):
            model = self._model
            template_name = self._template_name
            success_message = 'Update success.'
            success_url = reverse_lazy(self._success_page.route_name)
            form_class = self.form

        return CondorUpdateView


class DeletePage(CondorModelFormPage):
    def __init__(self, model: Type[Model], success_page: CondorModelPage, page_name=None,
                 form_fields=None, form_class=None, template_name=None):
        super().__init__(model, page_name, form_fields, form_class)
        self._success_page = success_page
        self._template_name = "pages/delete.html" if template_name is None else template_name

    @property
    def route(self):
        return f'{self.name}/<int:pk>/delete'

    @property
    def route_name(self):
        return super().route_name + '_delete'

    def _get_view(self, *args, **kwargs) -> Type[View]:
        CondorViewMixin = self.get_condor_view_mixin()

        class CondorDeleteView(CondorViewMixin, CreatePopupMixin, UpdatePopupMixin, BSModalDeleteView):
            model = self._model
            template_name = self._template_name
            success_message = 'Delete success.'
            success_url = reverse_lazy(self._success_page.route_name)
            form_class = self.form

        return CondorDeleteView




class ListPage(CondorModelPage):
    def __init__(self, model: Type[Model], page_name=None, paginated_by=30, template_name=None,
                 fields=None, excluded_fields=('id',)):
        super().__init__(model, page_name)
        self._paginated_by = paginated_by
        self._template_name = "pages/list.html" if template_name is None else template_name
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
        return f'{self.name}'

    @property
    def route_name(self):
        return super().route_name + '_list'


    @property
    def paths(self, *args, **kwargs):
        keys = [k for k in self.model_key_names()]
        filters_path_str = [f"(?:/{k}-(?P<{k}>\d+))?" for k in keys]
        filters_path_str = ''.join(filters_path_str)

        filtered_path = re_path(f'^{self.route}{filters_path_str}$', self._get_view(*args, **kwargs).as_view(),
                                name=self.route_name)

        # return [filtered_path, select_id_path_str]
        return [filtered_path]
        # return [self.default_path]


    def _get_view(self, *args, **kwargs) -> Type[View]:
        CondorViewMixin = self.get_condor_view_mixin()

        class CondorListView(CondorViewMixin, CreatePopupMixin, UpdatePopupMixin, ListView):
            navigator = self.navigator
            paginate_by = self._paginated_by
            model = self._model
            form_class = condor_bsmf_form(self._model, condor_fields=self._fields)
            template_name = self._template_name

            def get_key_filter_kwargs(iself):
                return {key: iself.kwargs[key] for key in self.model_key_names() if key in iself.kwargs.keys()}

            def get_queryset(iself):
                queryset = CondorListView.model.objects.all()
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

        return CondorListView



class ListCRUDPage(ListPage):
    def __init__(self, model: Type[Model], page_name=None, list_paginated_by=30,
                 form_class=None, form_fields=None,
                 list_fields=None, list_excluded_fields=('id',), **kwargs):
        super().__init__(model, page_name, list_paginated_by, fields=list_fields, excluded_fields=list_excluded_fields)
        # self.list = ListPage(model, page_name, list_paginated_by, fields=form_fields)
        self.create = CreatePage(model, self, page_name, form_fields=form_fields, form_class=form_class)
        self.read = ReadPage(model, page_name, form_fields=form_fields, form_class=form_class)
        self.update = UpdatePage(model, self, page_name, form_fields=form_fields, form_class=form_class)
        self.delete = DeletePage(model, self, page_name, form_fields=form_fields, form_class=form_class)

    @property
    def pages(self):
        return self, self.create, self.read, self.update, self.delete
