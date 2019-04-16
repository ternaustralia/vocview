import skos
from skos.common_properties import CommonPropertiesMixin


class Concept(CommonPropertiesMixin):
    def __init__(self, uri):
        super().__init__(uri)
        self.narrowers = skos.get_narrowers(uri)
        self.broaders = skos.get_broaders(uri)
        self.top_concept_of = skos.get_top_concept_of(uri)
