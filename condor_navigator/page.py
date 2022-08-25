from abc import ABC, abstractmethod
from typing import Type, Dict

from django.contrib.auth.decorators import login_required
from django.db.models import Model, ForeignKey, ManyToManyField
from django.db.models.fields.related_descriptors import ReverseManyToOneDescriptor, ManyToManyDescriptor
from django.urls import path
from django.views import View
from django.views.generic.base import ContextMixin
from condor_navigator.utils import _value_or_default



class CondorPage(ABC):
    def __init__(self, name, title=None, login_required=True):
        self._name = name
        self._title = title if title is not None else name
        self._registered_navigator = None
        self._login_required = login_required
        # self._route = f'{self.name}/' if route is None else route


    @property
    def login_required(self):
        return self._login_required

    def _add_condor_context(self, context: Dict):
        context['navigator'] = self.navigator
        context['pages'] = self
        return context

    def get_condor_view_mixin(self) -> Type['CondorViewMixin']:
        class CondorViewMixin(ContextMixin):
            def get_context_data(inner_self, **kwargs):
                context = super().get_context_data(**kwargs)
                self._add_condor_context(context)
                return context
        return CondorViewMixin

    @abstractmethod
    def _get_view(self, *args, **kwargs) -> Type[View]:
        pass

    def get_view(self, *args, **kwargs) -> Type[View]:
        view = self._get_view(*args, **kwargs).as_view()
        if self.login_required:
            view = login_required(view, login_url=self.navigator.not_logged_url)
        return view

    @property
    def navigator(self) -> 'CondorNavigator':
        return self._registered_navigator

    # Name
    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value

    # Title
    @property
    def title(self) -> str:
        return self._title

    @title.setter
    def title(self, value: str):
        self._title = value

    # URLs
    @property
    def route_name(self):
        return self.name

    @property
    def route(self):
        return f'{self.name}/'

    @property
    def default_path(self, *args, **kwargs):
        return path(self.route, self.get_view(*args, **kwargs), name=self.route_name)

    @property
    def paths(self, *args, **kwargs):
        return [self.default_path]


class CondorModelPage(CondorPage):
    def __init__(self, model: Type[Model], page_name=None):
        self._model = model
        page_name = self.model_name if page_name is None else page_name
        super().__init__(name=page_name, title=self.model_verbose_name)

    def _add_condor_context(self, context: Dict):
        super()._add_condor_context(context)
        context['model'] = self.model
        return context

    @property
    def model(self) -> Type[Model]:
        return self._model

    @property
    def model_name(self) -> str:
        return self._model._meta.model_name

    @property
    def model_verbose_name(self) -> str:
        return self._model._meta.verbose_name

    def model_fks(self):
        return get_model_fks(self.model)

    def model_fk_names(self):
        return [field.name for field in self.model_fks()]

    def model_key_names(self):
        return self.model_fk_names() + ['pk']

    def model_reverse_fks(self):
        reverse_fks = []
        for k, v in self.model.__dict__.items():
            if isinstance(v, ReverseManyToOneDescriptor):
                related_foreign_keys = get_model_fks(v.rel.related_model)
                for rfk in related_foreign_keys:
                    if rfk.related_model == self.model:
                        reverse_fks.append(rfk)

            if isinstance(v, ManyToManyDescriptor):
                related_foreign_keys = get_model_fks(v.rel.related_model)
                for rfk in related_foreign_keys:
                    if rfk.related_model == self.model:
                        reverse_fks.append(rfk)

        return reverse_fks

    def model_reverse_fk_names(self):
        return [fk.name for fk in self.model_reverse_fks()]


    def model_forward_fields(self):
        fields = self.model._meta._forward_fields_map
        unique_fields = {f: v for f, v in fields.items()
                         if not (f.endswith('_id') and f[:-3] in fields.keys() and fields[f[:-3]] == fields[f])}
        return unique_fields

    def model_fields_map(self):
        fields = self.model._meta.get_fields()
        return {f.code: f for f in fields}

    def model_object_to_dict(self, model_object):
        object_fields = {}
        model_fields = self.model_forward_fields()
        for f_name, field in model_fields.items():
            field_value = model_object.__getattribute__(f_name)
            if field_value.__class__.__name__ == 'ManyRelatedManager':
                field_value = field_value.all()
            object_fields[f_name] = field_value
        return object_fields

def get_model_fks(model):
    return [field for field in model._meta.fields if isinstance(field, ForeignKey)]
