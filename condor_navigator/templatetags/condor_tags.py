import inspect
from typing import Type

from django.db.models import Model, ForeignKey, ManyToOneRel
from django.db.models.fields.reverse_related import ForeignObjectRel, ManyToManyRel
from django.urls import reverse
from django.utils.html import format_html
from django import template
from recurrence.forms import RecurrenceField

from condor_navigator.navigator import CondorNavigator
from condor_navigator.page import CondorModelPage
from condor_navigator.pages.crud import ListCRUDPage, CondorModelFormPage, ListPage

register = template.Library()



@register.filter(is_safe=True)
def is_recurrence_field(field):
    if isinstance(field.field, RecurrenceField):
        return True
    return False

@register.filter(is_safe=True)
def table_row(object: Model, page: ListPage):

    html = []
    data = []
    for k, field in page.model_fields_map().items():
        # if isinstance(field, ForeignObjectRel):
        # if field.is_relation:
        #     # attrib = object.__getattribute__(field.get_accessor_name())
        #     continue

        if page.fields !='__all__':
            if k not in page.fields:
                continue
        if k in page.excluded_fields:
            continue
        if isinstance(field, ManyToOneRel) or isinstance(field, ManyToManyRel):
            continue
        attrib = object.__getattribute__(k)

        col_value = str(attrib)
        if k == 'id':
            try:
                page = page.navigator.get_model_default_page(object.__class__)
                html.append("<td><a href='{}'><u>{}</u></a></td>")
                if isinstance(page, ListCRUDPage):
                    # data.append(reverse(pages.list.route_name_pk, kwargs={'pk': attrib}))
                    data.append(reverse(page.route_name, kwargs={'pk': attrib}))
                else:
                    data.append(reverse(page.route_name))

            except KeyError:
                html.append("<td>{}</td>")

        elif isinstance(attrib, Model):
            try:
                page = page.navigator.get_model_default_page(attrib.__class__)
                if isinstance(page, ListCRUDPage):
                    # data.append(reverse(pages.list.route_name_pk, kwargs={'pk': attrib.pk}))
                    html.append("<td><a  class='bs-modal' data-form-url='{}' href='#'><u>{}</u></a></td>") # href='{}'
                    # html.append("<td><a href='{}'><u>{}</u></a></td>")

                    data.append(reverse(page.read.route_name, kwargs={'pk': attrib.pk}))
                    # data.append(reverse(page.route_name, kwargs={'pk': attrib.pk}))
                else:
                    html.append("<td><a href='{}'><u>{}</u></a></td>")
                    data.append(reverse(page.route_name))

            except KeyError:
                html.append("<td>{}</td>")

        else:
            html.append("<td>{}</td>")
            try:
                to_many_field_str = ', '.join([str(a) for a in attrib.all()])
                col_value = to_many_field_str
            except:
                pass
        data.append(col_value)


    return format_html("".join(html), *data)

@register.filter(is_safe=True)
def table_header(page: ListPage):
    html = []
    data = []
    for k, field in page.model_fields_map().items():
        # if field.is_relation:
        #     continue

        if page.fields != '__all__':
            if k not in page.fields:
                continue
        if k in page.excluded_fields:
            continue
        if isinstance(field, ManyToOneRel) or isinstance(field, ManyToManyRel):
            continue

        if isinstance(field, ForeignKey):
            field_related_page = page.navigator.get_model_default_page(field.related_model)
            html.append("<th><a href='{}'><u>{}</u></a></th>")
            data.append(reverse(field_related_page.route_name))
            data.append(field.verbose_name)
        # if isinstance(field, ManyToOneRel):
        #     continue
        #     field_related_page = page.navigator.get_model_default_page(field.related_model)
        #     html.append("<th><a href='{}'><u>{}</u></a></th>")
        #     data.append(reverse(field_related_page.route_name))
        #     data.append(field.related_model)
        else:
            html.append("<th>{}</th>")
            data.append(field.verbose_name)
        # if isinstance(field, ForwardManyToManyDescriptor):
        #     pass
    return format_html("".join(html), *data)



# @register.filter(is_safe=True)
# def table_row(object: Model, page: ListPage):
#     data = []
#     html = []
#     # keys = [f.name for f in object._meta.fields]
#     keys = list(set([f.name for f in object._meta._forward_fields_map.values()]))
#     # TODO: use page.model._meta.get_fields() instead of the forward_fields_map
#     #  (in this way we also get the reverse relationships directly here!)
#
#     for k in keys:
#         if page.fields is not '__all__':
#             if k not in page.fields:
#                 continue
#         if k in page.excluded_fields:
#             continue
#         attrib = object.__getattribute__(k)
#
#         col_value = str(attrib)
#         if k == 'id':
#             try:
#                 page = page.navigator.get_model_default_page(object.__class__)
#                 html.append("<td><a href='{}'><u>{}</u></a></td>")
#                 if isinstance(page, ListCRUDPage):
#                     # data.append(reverse(pages.list.route_name_pk, kwargs={'pk': attrib}))
#                     data.append(reverse(page.route_name, kwargs={'pk': attrib}))
#                 else:
#                     data.append(reverse(page.route_name))
#
#             except KeyError:
#                 html.append("<td>{}</td>")
#
#         elif isinstance(attrib, Model):
#             try:
#                 page = page.navigator.get_model_default_page(attrib.__class__)
#                 html.append("<td><a href='{}'><u>{}</u></a></td>")
#                 if isinstance(page, ListCRUDPage):
#                     # data.append(reverse(pages.list.route_name_pk, kwargs={'pk': attrib.pk}))
#                     data.append(reverse(page.route_name, kwargs={'pk': attrib.pk}))
#                 else:
#                     data.append(reverse(page.route_name))
#
#             except KeyError:
#                 html.append("<td>{}</td>")
#
#         else:
#             html.append("<td>{}</td>")
#             try:
#                 to_many_field_str = ', '.join([str(a) for a in attrib.all()])
#                 col_value = to_many_field_str
#             except:
#                 pass
#         data.append(col_value)
#
#
#     return format_html("".join(html), *data)
#
# @register.filter(is_safe=True)
# def table_header(page: CondorModelPage):
#     # if keys == '__all__':
#     # keys = [f.name for f in pages.model._meta.fields]
#     keys = list(set([f.name for f in page.model._meta._forward_fields_map.values()]))
#     # TODO: use page.model._meta.get_fields() instead of the forward_fields_map
#     #  (in this way we also get the reverse relationships directly here!)
#
#     sorted_keys = []
#     extra_unsorted_keys = []
#     for f in page.model._meta.get_fields():
#         if f.name in keys:
#             sorted_keys.append(f.name)
#     for k in keys:
#         if k not in sorted_keys:
#             extra_unsorted_keys.append(k)
#     sorted_keys = sorted_keys + sorted(extra_unsorted_keys)
#
#     html = []
#     data = []
#     for k in sorted_keys:
#         if page.fields is not '__all__':
#             if k not in page.fields:
#                 continue
#         if k in page.excluded_fields:
#             continue
#
#         field = page.model.__getattribute__(page.model, k).field
#         if isinstance(field, ForeignKey):
#             field_related_page = page.navigator.get_model_default_page(field.related_model)
#             html.append("<th><a href='{}'><u>{}</u></a></th>")
#             data.append(reverse(field_related_page.route_name))
#             data.append(field.verbose_name)
#         else:
#             html.append("<th>{}</th>")
#             data.append(field.verbose_name)
#         # if isinstance(field, ForwardManyToManyDescriptor):
#         #     pass
#     return format_html("".join(html), *data)




from typing import Union

PageModelObject =  Union[CondorModelPage, Type[Model], Model]

def get_page(obj: PageModelObject):
    page = None
    if isinstance(obj, CondorModelPage):
        page = obj
    elif isinstance(obj, Model):
        page = CondorNavigator().get_model_default_page(obj.__class__)
    elif inspect.isclass(obj) and issubclass(obj, Model):
        page = CondorNavigator().get_model_default_page(obj)
    return page

def get_lcrud_page(obj: PageModelObject):
    page = get_page(obj)
    if page is not None:
        return page.navigator.get_model_lcrud_page(page.model)
    return None

@register.filter(is_safe=False)
def default_route(obj: PageModelObject):
    page = get_page(obj)
    if page is not None:
        return page.route_name
    return None

@register.filter(is_safe=False)
def create_route(obj: PageModelObject):
    page = get_lcrud_page(obj)
    if isinstance(page, ListCRUDPage):
        return page.create.route_name
    return None

@register.filter(is_safe=False)
def read_route(obj: PageModelObject):
    page = get_lcrud_page(obj)
    if isinstance(page, ListCRUDPage):
        return page.read.route_name
    return None

@register.filter(is_safe=False)
def update_route(obj: PageModelObject):
    page = get_lcrud_page(obj)
    if isinstance(page, ListCRUDPage):
        return page.update.route_name
    return None

@register.filter(is_safe=False)
def delete_route(obj: PageModelObject):
    page = get_lcrud_page(obj)
    if isinstance(page, ListCRUDPage):
        return page.delete.route_name
    return None

@register.filter(is_safe=False)
def list_route(obj: PageModelObject):
    page = get_lcrud_page(obj)
    if isinstance(page, ListCRUDPage):
        return page.route_name
    return None


@register.filter(is_safe=False)
def model_name(obj: PageModelObject):
    page = get_lcrud_page(obj)
    if isinstance(page, ListCRUDPage):
        return page.model_name


@register.filter(is_safe=False)
def default_url(object: PageModelObject):
    # page = CondorNavigator().get_model_default_page(object.__class__)
    route = default_route(object)
    if route is not None:
        return reverse(route)
    return None

@register.filter(is_safe=False)
def create_url(object: PageModelObject):
    return reverse(create_route(object))

@register.filter(is_safe=False)
def read_url(object: Model):
    return reverse(read_route(object), args=[object.id])


@register.filter(is_safe=False)
def update_url(object: Model):
    return reverse(update_route(object), args=[object.id])


@register.filter(is_safe=False)
def delete_url(object: Model):
    return reverse(delete_route(object), args=[object.id])

@register.filter(is_safe=False)
def list_url(object: PageModelObject):
    return reverse(list_route(object))

