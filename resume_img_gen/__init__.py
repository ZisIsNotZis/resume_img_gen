"""resume_img_gen — turn structured resume data into HTML, PDF, and PNG images.

Three stages, each usable on its own:

    render   JSON data + an HTML template  ->  HTML
    pdf      Markdown (optional front matter) ->  PDF      (pandoc + WeasyPrint)
    shot     HTML  ->  PNG or PDF                            (headless Chromium)

The bundled ``templates/`` are design canvases whose every content string is a
``{{token}}``.  Keep text in your data file, never in the template, so the two
can evolve independently.
"""

__version__ = "0.1.0"
