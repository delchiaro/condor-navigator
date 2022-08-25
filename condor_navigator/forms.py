from bootstrap_modal_forms.forms import BSModalModelForm
from django.db.models import Model, ManyToManyField, DateField
from django.db.models.fields.related_descriptors import ManyToManyDescriptor
from django.urls import reverse_lazy
from django_addanother.widgets import AddAnotherWidgetWrapper, AddAnotherEditSelectedWidgetWrapper
from django import forms

from condor_navigator.widgets import FengyuanChenDatePickerInput, BootstrapDatePickerInput


def get_add_another_widgets(condor_model):
    widgets = {}
    keys = [f.id for f in condor_model._meta.fields]
    for k in keys:
        try:
            attrib = condor_model.__getattribute__(condor_model, k)
            model = attrib.field.related_model()
            widgets[k] = AddAnotherWidgetWrapper(forms.Select, reverse_lazy(model.router.create.id))
            # widgets[k] = AddAnotherEditSelectedWidgetWrapper(forms.Select,
            #                                                            reverse_lazy(model.router.create.name),
            #                                                            reverse_lazy(model.router.update.name, args=['__fk__']))
        except Exception as e:
            pass
    return widgets


from django_select2 import forms as s2forms


def get_select2_multiple_widgets(condor_model, widgets: dict):
    # widgets = {'operators': s2forms.Select2Widget}
    keys = list(set([f.name for f in condor_model._meta._forward_fields_map.values()]))
    for k in keys:
        try:
            attrib = condor_model.__getattribute__(condor_model, k)
            if isinstance(attrib, ManyToManyDescriptor):
                widgets[attrib.field.id] = s2forms.Select2MultipleWidget(attrs={'class': 'form-control s2 pb-4',
                                                                            'multiple': 'multiple',
                                                                            'data-width': '100%'})
        except:
            pass
    # widgets = {'operators': s2forms.Select2MultipleWidget(attrs={'class': 'form-control s2 pb-4',
    #                                                              'multiple': 'multiple',
    #                                                              'data-width': '100%'})}
    return widgets


def inject_custom_widgets(condor_model):
    widgets = {}
    widgets = get_select2_multiple_widgets(condor_model, widgets)
    for field in condor_model._meta.fields:
        if isinstance(field, DateField):
            widgets[field.name] = BootstrapDatePickerInput()
    return widgets

def inject_custom_input_formats(condor_model):
    input_formats = {}
    for field in condor_model._meta.fields:
        if isinstance(field, DateField):
            input_formats[field.name] = '%m/%d/%Y'
    return input_formats

def condor_bsmf_form(condor_model, condor_fields='__all__', exclude_fields=('id',)):
    exclude_fields = tuple() if exclude_fields is None else exclude_fields
    class CondorForm(BSModalModelForm):
        class Meta:
            model = condor_model
            fields = condor_fields
            exclude = exclude_fields
            input_formats = inject_custom_input_formats(condor_model)
            # widgets = condor_model, get_add_another_widgets(condor_model)
            widgets = inject_custom_widgets(condor_model)

        @classmethod
        def set_readonly(cls, readonly=True):
            for field in cls.base_fields.keys():
                cls.base_fields[field].disabled = readonly
            return cls

    return CondorForm

