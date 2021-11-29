r"""
This module wires the application's functionality into [PySide6](https://wiki.qt.io/Qt_for_Python) **Qt** widgets. This module is relatively isolated from the rest of the application, in the sense that it is not imported anywhere in the application; however, it does import a fair chunk of the modules into its namespace; the flow is entirely in one direction. `scrilla.gui` imports from all the other modules, but the other modules do not import from `scrilla.gui`. A programmatic cul-de-sac.
"""
