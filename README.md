emdf2brat
=========

A simple 2-way converter between Event Mention Detection Format(EMDF) and Brat

brat2emdf.py:

1. ID convention

The default set up follows Brat v1.3 ID convention: 
  - T: text-bound annotation
  - R: relation
  - E: event
  - A: attribute
  - M: modification (alias for attribute, for backward compatibility)
  - N: normalization [new in v1.3]
  - #: note

Further development might allow customized ID convention.

2. This code only scan and detect event mentions and its attributes. Event arguments and entities are currently not handled. Annotations other than Event Mention (with its attributes and Text Spans) will be ignored, which means, it will only read "E" annotations and its related attributes.

3. Discontinuous text-bound annotations will be supported

emdf2brat.py:

This code is under development
