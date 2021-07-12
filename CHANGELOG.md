# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [1.2.3] - 2021-07-05
### Added
- Error handling when reading data from file.


## [1.2.2] - 2021-06-23
### Added
- Perform OWL RL reasoning if enabled in background task.


## [1.2.1-postfix1] - 2021-06-23
### Fixed
- Create missing folders for Celery filesystem broker on web app startup.


## [1.2.1] - 2021-06-23
### Added
- Trigger background task on before_first_request.


## [1.2.0] - 2021-06-22
### Added
- Background tasks with Celery + filesystem broker.
- Watchdog to reload data in memory when background task pulls down new data.
### Changed
- RDFLib 4.2.2 -> 5.0.0


## [1.1.5] - 2021-05-21
### Added
- MathJax JavaScript dependency to render Math symbols in LateX.


## [1.1.4] - 2021-05-18
### Fixed
- Conditionally renders the Method's equipments list correctly now for both HTML values as well as for individuals.


## [1.1.3] - 2021-05-18
### Fixed
- Rendering of the Method's equipments list. It now renders correctly a list of individuals.


## [1.1.2] - 2021-05-18
### Added
- Methods template now renders additional properties.
- Accessing the viewer still works when viewer re-pulls new triples from sources.


## [1.1.1] - 2021-05-11
### Added
- CORS support.


## [1.1.0] - 2020-02-22
### Added
- Re-pull triples for 'memory' store mode.
### Changed
- Improved the views for different SKOS types (Concept, ConceptScheme, Collection). No requirement for use with OrderedCollection, so will be ignored for now. This improvement will allow us to manage and add different views more cleanly in the future.


## [1.0.6] - 2020-11-09
### Added
- python-dotenv
- Load from .env file for config.py
- Viewer now understands owl:deprecated and does not show it to the user through SKOS properties narrower, broader, hasTopConcept and in the search.


## [1.0.5] - 2020-11-03
### Fixed
- Time since last pull of remote data showing 'None' in the jinja template. Now it shows the time since last pull as expected (regardless of triplestore config type).


## [1.0.4] - 2020-11-03
### Changed
- Triplestore type in config.py changed to 'memory' as default. Better for deployments by removing the overhead of loading from disk a pickle file on each request.
- Only call the get_db function in @app.before_request if the RDF triples are not yet loaded in memory.
- get_properties function calls get_label function with the parameter 'create' as False. Significantly improving the speed of loading concepts since properties don't need to make a HTTP call the dereference the URI of properties without labels loaded in memory.  


## [1.0.3] - 2020-10-23
### Added
- Functionality to show and redirect externally linked concepts.


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