# Developer's Guide

## Extending the properties displayed for SKOS things
By default, all properties which are not on the "ignored list of properties" are displayed with their property name, URI, and the property value. VocView has the capability of extending on this to display certain properties in a custom way. For example, the list of broader and narrower concepts are displayed differently where each concept is displayed with its readable label with a clickable link. This link resolves within the VocView system to display the information related to the concept. 

To make this possible, a few steps were taken:
- First, add the property to the ignore list in the function `get_properties()` in [skos/__init__.py](skos/__init__.py).
    - The ignored property should be `SKOS.broader`.
- In the `Concept` class in [skos/concept.py](skos/concept.py), add an attribute to the class as `self.broaders = []`, which will be a list (since a concept can have zero to many broader relationships).
 - In [skos/__init__.py](skos/__init__.py), write a function which will retrieve all the broader concepts for the given concept. The function signature should take in one argument `uri`, which will be the URI of the *focus* concept. Append the results to a list and return it.
 - Back in the `Concept` class in [concept.py](skos/concept.py), assign `self.broaders = skos.get_broaders(uri)`.
 - Now create a html file in the directory [templates/macros](templates/macros) called `broaders.html`. Write a Jinja2 macro on how you want the broaders to be displayed for a concept.
 - In [templates/skos.html](templates/skos.html), add the import statement for the new macro and render it here.