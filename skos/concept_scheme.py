import skos
from skos.common_properties import CommonPropertiesMixin


class ConceptScheme(CommonPropertiesMixin):
    def __init__(self, uri):
        super().__init__(uri)
        self.top_concepts = skos.get_top_concepts(uri)
