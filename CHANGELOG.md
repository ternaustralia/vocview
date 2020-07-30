# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## Unreleased
### Changed
- Improved the views for different SKOS types (Concept, ConceptScheme, Collection). No requirement for use with OrderedCollection, so will be ignored for now. This improvement will allow us to manage and add different views more cleanly in the future.


## [1.0.2] - 2020-07-30
### Added
- Methods now show hasParameter and hasCategoricalVariableCollection properties in the html view.


## [1.0.1] - 2020-07-28
### Added
- 404 status code for URIs not found or does not have a recognised class type. 
- New Method view. See http://linked.data.gov.au/def/ausplots-cv/03ba5e75-f322-4f80-a1e3-5a845e4dd807 as an example.
- Started moving macros that do not need to be macros into `templates/elements`. These can be used with the Jinja2 `{% includes %}` statement and no longer need to be imported (like with macros).
- VocView can now dynamically read and present the version number from the CHANGELOG.md file.  
### Removed
- The default alternates view options as 'skos' for the header bar in the HTML view.  
### Changed
- Improved some of the macros in Jinja2. Some don't need to be macros and have since been changed to a normal Jinja2 template. 


## [1.0.0] - 2020-04-17
### Added
- "Version 1.0.0 release"