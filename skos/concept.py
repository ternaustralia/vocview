import skos


class Concept:
    def __init__(self, uri):
        self.uri = uri
        self.label = skos.get_label(uri)
        self.class_types = skos.get_class_types(uri)
        self.alt_labels = skos.get_alt_labels(uri)
        self.definition = skos.get_definition(uri)
        self.created = skos.get_created_date(uri)
        self.narrowers = skos.get_narrowers(uri)
        self.broaders = skos.get_broaders(uri)
        self.top_concept_of = skos.get_top_concept_of(uri)
        self.properties = skos.get_properties(uri)
