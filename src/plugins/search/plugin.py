# Copyright (c) 2016-2025 Martin Donath <martin.donath@squidfunk.com>

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.

import json
import logging
import os
import re
from backrefs import bre

from html import escape
from html.parser import HTMLParser
from mkdocs import utils
from mkdocs.config.config_options import SubConfig
from mkdocs.plugins import BasePlugin

from .config import SearchConfig, SearchFieldConfig

try:
    import jieba
except ImportError:
    jieba = None

# -----------------------------------------------------------------------------
# Classes
# -----------------------------------------------------------------------------

# Search plugin
class SearchPlugin(BasePlugin[SearchConfig]):

    # Initialize plugin
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Initialize incremental builds
        self.is_dirty = False
        self.is_dirtyreload = False

        # Initialize search index cache
        self.search_index_prev = None

    # Determine whether we're serving the site
    def on_startup(self, *, command, dirty):
        self.is_dirty = dirty

    # Initialize plugin
    def on_config(self, config):
        if not self.config.enabled:
            return

        # Retrieve default value for language
        if not self.config.lang:
            self.config.lang = [self._translate(
                config, "search.config.lang"
            )]

        # Retrieve default value for separator
        if not self.config.separator:
            self.config.separator = self._translate(
                config, "search.config.separator"
            )

        # Retrieve default value for pipeline
        if self.config.pipeline is None:
            self.config.pipeline = list(filter(len, re.split(
                r"\s*,\s*", self._translate(config, "search.config.pipeline")
            )))

        # Validate field configuration
        validator = SubConfig(SearchFieldConfig)
        for config in self.config.fields.values():
            validator.run_validation(config)

        # Merge with default fields
        if "title" not in self.config.fields:
            self.config.fields["title"] = { "boost": 1e3 }
        if "text" not in self.config.fields:
            self.config.fields["text"] = { "boost": 1e0 }
        if "tags" not in self.config.fields:
            self.config.fields["tags"] = { "boost": 1e6 }

        # Initialize search index
        self.search_index = SearchIndex(**self.config)

        # Set jieba dictionary, if given
        if self.config.jieba_dict:
            path = os.path.normpath(self.config.jieba_dict)
            if os.path.isfile(path):
                jieba.set_dictionary(path)
                log.debug(f"Loading jieba dictionary: {path}")
            else:
                log.warning(
                    f"Configuration error for 'search.jieba_dict': "
                    f"'{self.config.jieba_dict}' does not exist."
                )

        # Set jieba user dictionary, if given
        if self.config.jieba_dict_user:
            path = os.path.normpath(self.config.jieba_dict_user)
            if os.path.isfile(path):
                jieba.load_userdict(path)
                log.debug(f"Loading jieba user dictionary: {path}")
            else:
                log.warning(
                    f"Configuration error for 'search.jieba_dict_user': "
                    f"'{self.config.jieba_dict_user}' does not exist."
                )

    # Add page to search index
    def on_page_context(self, context, *, page, config, nav):
        if not self.config.enabled:
            return

        # Index page
        self.search_index.add_entry_from_context(page)
        page.content = re.sub(
            r"\s?data-search-\w+=\"[^\"]+\"",
            "",
            page.content
        )

    # Generate search index
    def on_post_build(self, *, config):
        if not self.config.enabled:
            return

        # Write search index
        base = os.path.join(config.site_dir, "search")
        path = os.path.join(base, "search_index.json")

        # Generate and write search index to file
        data = self.search_index.generate_search_index(self.search_index_prev)
        utils.write_file(data.encode("utf-8"), path)

        # Persist search index for repeated invocation
        if self.is_dirty:
            self.search_index_prev = self.search_index

    # Determine whether we're running under dirty reload
    def on_serve(self, server, *, config, builder):
        self.is_dirtyreload = self.is_dirty

    # -------------------------------------------------------------------------

    # Translate the given placeholder value
    def _translate(self, config, value):
        env = config.theme.get_env()

        # Load language template and return translation for placeholder
        language = "partials/language.html"
        template = env.get_template(language, None, { "config": config })
        return template.module.t(value)

# -----------------------------------------------------------------------------

# Search index with support for additional fields
class SearchIndex:

    # Initialize search index
    def __init__(self, **config):
        self.config = config
        self.entries = []

    # Add page to search index
    def add_entry_from_context(self, page):
        search = page.meta.get("search") or {}
        if search.get("exclude"):
            return

        # Divide page content into sections
        parser = Parser()
        parser.feed(page.content)
        parser.close()

        # Add sections to index
        for section in parser.data:
            if not section.is_excluded():
                self.create_entry_for_section(section, page.toc, page.url, page)

    # Override: graceful indexing and additional fields
    def create_entry_for_section(self, section, toc, url, page):
        item = self._find_toc_by_id(toc, section.id)
        if item:
            url = url + item.url
        elif section.id:
            url = url + "#" + section.id

        # Set page title as section title if none was given, which happens when
        # the first headline in a Markdown document is not a h1 headline. Also,
        # if a page title was set via front matter, use that even though a h1
        # might be given or the page name was specified in nav in mkdocs.yml
        if not section.title:
            section.title = [str(page.meta.get("title", page.title))]

        # Compute title and text
        title = "".join(section.title).strip()
        text  = "".join(section.text).strip()

        # Segment Chinese characters if jieba is available
        if jieba:
            title = self._segment_chinese(title)
            text  = self._segment_chinese(text)

        # Create entry for section
        entry = {
            "location": url,
            "title": title,
            "text": text
        }

        # Set document tags
        tags = page.meta.get("tags")
        if isinstance(tags, list):
            entry["tags"] = []
            for name in tags:
                if name and isinstance(name, (str, int, float, bool)):
                    entry["tags"].append(str(name))

        # Set document boost
        search = page.meta.get("search") or {}
        if "boost" in search:
            entry["boost"] = search["boost"]

        # Add entry to index
        self.entries.append(entry)

    # Generate search index
    def generate_search_index(self, prev):
        config = {
            key: self.config[key]
                for key in ["lang", "separator", "pipeline", "fields"]
        }

        # Hack: if we're running under dirty reload, the search index will only
        # include the entries for the current page. However, MkDocs > 1.4 allows
        # us to persist plugin state across rebuilds, which is exactly what we
        # do by passing the previously built index to this method. Thus, we just
        # remove the previous entries for the current page, and append the new
        # entries to the end of the index, as order doesn't matter.
        if prev and self.entries:
            path = self.entries[0]["location"]

            # Since we're sure that we're running under dirty reload, the list
            # of entries will only contain sections for a single page. Thus, we
            # use the first entry to remove all entries from the previous run
            # that belong to the current page. The rationale behind this is that
            # authors might add or remove section headers, so we need to make
            # sure that sections are synchronized correctly.
            entries = [
                entry for entry in prev.entries
                    if not entry["location"].startswith(path)
            ]

            # Merge previous with current entries
            self.entries = entries + self.entries

        # Otherwise just set previous entries
        if prev and not self.entries:
            self.entries = prev.entries

        # Return search index as JSON
        data = { "config": config, "docs": self.entries }
        return json.dumps(
            data,
            separators = (",", ":"),
            default = str
        )

    # -------------------------------------------------------------------------

    # Retrieve item for anchor
    def _find_toc_by_id(self, toc, id):
        for toc_item in toc:
            if toc_item.id == id:
                return toc_item

            # Recurse into children of item
            toc_item = self._find_toc_by_id(toc_item.children, id)
            if toc_item is not None:
                return toc_item

        # No item found
        return None

    # Find and segment Chinese characters in string
    def _segment_chinese(self, data):
        expr = bre.compile(r"(\p{script: Han}+)", bre.UNICODE)

        # Replace callback
        def replace(match):
            value = match.group(0)

            # Replace occurrence in original string with segmented version and
            # surround with zero-width whitespace for efficient indexing
            return "".join([
                "\u200b",
                "\u200b".join(jieba.cut(value.encode("utf-8"))),
                "\u200b",
            ])

        # Return string with segmented occurrences
        return expr.sub(replace, data).strip("\u200b")

# -----------------------------------------------------------------------------

# HTML element
class Element:
    """
    An element with attributes, essentially a small wrapper object for the
    parser to access attributes in other callbacks than handle_starttag.
    """

    # Initialize HTML element
    def __init__(self, tag, attrs = None):
        self.tag   = tag
        self.attrs = attrs or {}

    # String representation
    def __repr__(self):
        return self.tag

    # Support comparison (compare by tag only)
    def __eq__(self, other):
        if other is Element:
            return self.tag == other.tag
        else:
            return self.tag == other

    # Support set operations
    def __hash__(self):
        return hash(self.tag)

    # Check whether the element should be excluded
    def is_excluded(self):
        return "data-search-exclude" in self.attrs

# -----------------------------------------------------------------------------

# HTML section
class Section:
    """
    A block of text with markup, preceded by a title (with markup), i.e., a
    headline with a certain level (h1-h6). Internally used by the parser.
    """

    # Initialize HTML section
    def __init__(self, el, depth = 0):
        self.el = el
        self.depth = depth

        # Initialize section data
        self.text  = []
        self.title = []
        self.id = None

    # String representation
    def __repr__(self):
        if self.id:
            return "#".join([self.el.tag, self.id])
        else:
            return self.el.tag

    # Check whether the section should be excluded
    def is_excluded(self):
        return self.el.is_excluded()

# -----------------------------------------------------------------------------

# HTML parser
class Parser(HTMLParser):
    """
    This parser divides the given string of HTML into a list of sections, each
    of which are preceded by a h1-h6 level heading. A white- and blacklist of
    tags dictates which tags should be preserved as part of the index, and
    which should be ignored in their entirety.
    """

    # Initialize HTML parser
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Tags to skip
        self.skip = set([
            "object",                  # Objects
            "script",                  # Scripts
            "style"                    # Styles
        ])

        # Tags to keep
        self.keep = set([
            "p",                       # Paragraphs
            "code", "pre",             # Code blocks
            "li", "ol", "ul",          # Lists
            "sub", "sup"               # Sub- and superscripts
        ])

        # Current context and section
        self.context = []
        self.section = None

        # All parsed sections
        self.data = []

    # Called at the start of every HTML tag
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)

        # Ignore self-closing tags
        el = Element(tag, attrs)
        if not tag in void:
            self.context.append(el)
        else:
            return

        # Handle heading
        if tag in ([f"h{x}" for x in range(1, 7)]):
            depth = len(self.context)
            if "id" in attrs:

                # Ensure top-level section
                if tag != "h1" and not self.data:
                    self.section = Section(Element("hx"), depth)
                    self.data.append(self.section)

                # Set identifier, if not first section
                self.section = Section(el, depth)
                if self.data:
                    self.section.id = attrs["id"]

                # Append section to list
                self.data.append(self.section)

        # Handle preface - ensure top-level section
        if not self.section:
            self.section = Section(Element("hx"))
            self.data.append(self.section)

        # Handle special cases to skip
        for key, value in attrs.items():

            # Skip block if explicitly excluded from search
            if key == "data-search-exclude":
                self.skip.add(el)
                return

            # Skip line numbers - see https://bit.ly/3GvubZx
            if key == "class" and value == "linenodiv":
                self.skip.add(el)
                return

        # Render opening tag if kept
        if not self.skip.intersection(self.context) and tag in self.keep:

            # Check whether we're inside the section title
            data = self.section.text
            if self.section.el in self.context:
                data = self.section.title

            # Append to section title or text
            data.append(f"<{tag}>")

    # Called at the end of every HTML tag
    def handle_endtag(self, tag):
        if not self.context or self.context[-1] != tag:
            return

        # Check whether we're exiting the current context, which happens when
        # a headline is nested in another element. In that case, we close the
        # current section, continuing to append data to the previous section,
        # which could also be a nested section – see https://bit.ly/3IxxIJZ
        if self.section.depth > len(self.context):
            for section in reversed(self.data):
                if section.depth <= len(self.context):

                    # Set depth to infinity in order to denote that the current
                    # section is exited and must never be considered again.
                    self.section.depth = float("inf")
                    self.section = section
                    break

        # Remove element from skip list
        el = self.context.pop()
        if el in self.skip:
            if el.tag not in ["script", "style", "object"]:
                self.skip.remove(el)
            return

        # Render closing tag if kept
        if not self.skip.intersection(self.context) and tag in self.keep:

            # Check whether we're inside the section title
            data = self.section.text
            if self.section.el in self.context:
                data = self.section.title

            # Search for corresponding opening tag
            index = data.index(f"<{tag}>")
            for i in range(index + 1, len(data)):
                if not data[i].isspace():
                    index = len(data)
                    break

            # Remove element if empty (or only whitespace)
            if len(data) > index:
                while len(data) > index:
                    data.pop()

            # Append to section title or text
            else:
                data.append(f"</{tag}>")

    # Called for the text contents of each tag
    def handle_data(self, data):
        if self.skip.intersection(self.context):
            return

        # Collapse whitespace in non-pre contexts
        if not "pre" in self.context:
            if not data.isspace():
                data = data.replace("\n", " ")
            else:
                data = " "

        # Handle preface - ensure top-level section
        if not self.section:
            self.section = Section(Element("hx"))
            self.data.append(self.section)

        # Handle section headline
        if self.section.el in self.context:
            permalink = False
            for el in self.context:
                if el.tag == "a" and el.attrs.get("class") == "headerlink":
                    permalink = True

            # Ignore permalinks
            if not permalink:
                self.section.title.append(
                    escape(data, quote = False)
                )

        # Collapse adjacent whitespace
        elif data.isspace():
            if not self.section.text or not self.section.text[-1].isspace():
                self.section.text.append(data)
            elif "pre" in self.context:
                self.section.text.append(data)

        # Handle everything else
        else:
            self.section.text.append(
                escape(data, quote = False)
            )

# -----------------------------------------------------------------------------
# Data
# -----------------------------------------------------------------------------

# Set up logging
log = logging.getLogger("mkdocs.material.search")

# Tags that are self-closing
void = set([
    "area",                            # Image map areas
    "base",                            # Document base
    "br",                              # Line breaks
    "col",                             # Table columns
    "embed",                           # External content
    "hr",                              # Horizontal rules
    "img",                             # Images
    "input",                           # Input fields
    "link",                            # Links
    "meta",                            # Metadata
    "param",                           # External parameters
    "source",                          # Image source sets
    "track",                           # Text track
    "wbr"                              # Line break opportunities
])
