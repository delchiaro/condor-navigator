from typing import List, Dict, Tuple, Set, Union, TypeVar, Type
from django.db.models import Model

from condor_navigator.page import CondorModelPage, CondorPage
from condor_navigator.pages.crud import ListCRUDPage

T = TypeVar('T')
Iterable = Union[Tuple[T], List[T], Set[T]]


class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class MenuEntry:
    def __init__(self, name: str, pages: List[CondorPage]=None, expanded=False):
        self._name = name
        self._pages = pages if pages is not None else []
        self.expanded = expanded

    def add(self, *pages: CondorPage):
        self._pages += [p for p in pages]

    @property
    def pages(self):
        return self._pages

    @property
    def name(self):
        return self._name



class CondorNavigator(metaclass=Singleton):
    def __init__(self, base_route='condor', page_title=None, menu_title=None):
        self.page_title = 'Condor Navigator' if page_title is None else page_title
        self.menu_title = 'Condor Menu' if menu_title is None else menu_title

        self._login_url = '/accounts/login'
        self._logout_url = '/accounts/logout'
        self._not_logged_url = '/'
        self._base_route = base_route
        self._pages = []
        self._menus: Dict[str, MenuEntry] = {}
        self._models_default_pages: Dict[Type[Model], CondorPage] = {}
        self._models_lcrud_pages: Dict[Type[Model], ListCRUDPage] = {}

        from .pages.index import IndexPage
        self.add_page(IndexPage('index'))


    @property
    def login_url(self):
        return self._login_url

    @property
    def logout_url(self):
        return self._logout_url

    @property
    def not_logged_url(self):
        return self._not_logged_url

    @property
    def pages(self) -> List[CondorPage]:
        """ Get a shallow copy of pages list """
        return [p for p in self._pages]

    def get_model_default_page(self, model: Type[Model]):
        try:
            return self._models_default_pages[model]
        except KeyError:
            return None

    def get_models_default_pages(self, *models: Model):
        return [self.get_model_default_page(m) for m in models]

    def get_model_lcrud_page(self, model: Type[Model]):
        try:
            return self._models_lcrud_pages[model]
        except KeyError:
            return None

    def get_models_lcrud_pages(self, *models: Model):
        return [self.get_model_lcrud_page(m) for m in models]

    @property
    def menus(self) -> Dict[str, MenuEntry]:
        # return {k: [p for p in self._menus[k]] for k  in self._menus.keys()}
        return self._menus

    def __add_page_to_menus(self, page: CondorPage, menus: Union[str, Iterable[str]]):
        menus = [menus] if isinstance(menus, str) else menus
        for menu in menus:
            if menu not in self._menus.keys():
                self._menus[menu] = MenuEntry(menu)
            self._menus[menu].add(page)

    def __add_page(self, page: CondorPage, model_default_page=False, menus: Union[str, Iterable[str]]=None):
        """Register the pages if it's not already registered
        :param page: pages to register in the navigator.
        :param model_default_page: if True, this pages will be used as index pages for the model associated with the pages.
        :param menus: add the current pages to a set of menus defined by this parameter.
        :return: self
        """
        if page not in self._pages:
            self._pages.append(page)
            page._registered_navigator = self
        if isinstance(page, CondorModelPage):
            if model_default_page:
                self._models_default_pages[page.model] = page
        if menus is not None:
            self.__add_page_to_menus(page, menus)
        return self

    def __add_pages(self, *pages: CondorPage, models_default_pages=False, menus: Union[str, Iterable[str]] = None):
        """ Register all the pages that are not already registered, ignore the registered ones."""
        for p in pages:
            self.__add_page(p, model_default_page=models_default_pages, menus=menus)
        return self

    def add_page(self, page: CondorPage, model_default_page=False, menus: Union[str, Iterable[str]]=None):
        assert not isinstance(page, ListCRUDPage), 'Please use register_model to add LCRUDPage related to a Model.'
        return self.__add_page(page, model_default_page, menus)

    def add_pages(self, *pages: CondorPage, models_index_pages=False, menus: Union[str, Iterable[str]] = None):
        for p in pages:
            self.add_page(p, model_default_page=models_index_pages, menus=menus)
        return self

    def register_model(self, model, name=None, list_paginated_by=30, fields=None, form_class=None,
                       model_default_page=True, lcrud_page_type: Type[ListCRUDPage]=ListCRUDPage,
                       lcrud_page_kwargs=None, menus: Union[str, Iterable[str]]=None):
        """ Register a model adding the corresponding lcrud pages """
        lcrud = self.get_model_lcrud_page(model)
        if lcrud is None:
            # We create a new LCRUDPage related to the model only if it does not already exists
            if lcrud_page_kwargs:
                lcrud_page_kwargs = {}
            lcrud = lcrud_page_type(model=model, page_name=name, list_paginated_by=list_paginated_by,
                                    form_fields=fields, form_class=form_class, kwargs=lcrud_page_kwargs)

            self.__add_pages(*lcrud.pages)
            self._models_lcrud_pages[model] = lcrud
        self.__add_page(lcrud, model_default_page, menus)
        return self


    def register_models(self, *models, list_paginated_by=30, models_default_page=True,
                        menus: Union[str, Iterable[str]] = None):
        """ Register a list of models adding the corresponding lcrud pages """
        for model in models:
            self.register_model(model, list_paginated_by=list_paginated_by, model_default_page=models_default_page, menus=menus)
        return self

    @property
    def urls(self):
        return [path for page in self.pages for path in page.paths]


