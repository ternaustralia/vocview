from flask import render_template

from pyldapi.register_renderer import RegisterRenderer


class Register(RegisterRenderer):
    def __init__(self, request, label, comment, items, contained_item_classes, register_template=None, description=None):
        self.description = description

        super().__init__(request, request.base_url, label, comment, items, contained_item_classes, len(items),
                         register_template=register_template)

    def render(self):
        if self.view == 'reg' and self.format == 'text/html':
            return render_template(self.register_template, title='Vocabularies Register', description=self.description,
                                   concept_schemes=self.register_items)
        if self.view == 'reg' or self.view == 'alternates':
            return super(Register, self).render()
