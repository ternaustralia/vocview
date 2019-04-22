from flask import render_template

from pyldapi.register_renderer import RegisterRenderer


class Register(RegisterRenderer):
    def __init__(self, request, label, comment, items, contained_item_classes, register_template=None, description=None,
                 title=None, search_query=None):
        if title:
            self.title = title
        else:
            self.title = label
        self.description = description
        self.search_query = search_query

        super().__init__(request, request.base_url, label, comment, items, contained_item_classes, len(items),
                         register_template=register_template)

    def render(self):
        if self.view == 'reg' and self.format == 'text/html':
            return render_template(self.register_template,
                                   title=self.title,
                                   description=self.description,
                                   class_type=self.contained_item_classes[0],
                                   items=self.register_items,
                                   search_query=self.search_query)
        if self.view == 'reg' or self.view == 'alternates':
            return super(Register, self).render()
