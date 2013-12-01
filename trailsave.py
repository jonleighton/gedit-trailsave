# Copyright (C) 2006-2011 Osmo Salomaa & Jon Leighton
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

"""Automatically strip all trailing whitespace before saving."""

from gi.repository import GObject, Gedit
import re

class SaveWithoutTrailingSpacePlugin(GObject.Object, Gedit.ViewActivatable):
    """Automatically strip all trailing whitespace before saving."""

    __gtype_name__ = "SaveWithoutTrailingSpacePlugin"
    view = GObject.property(type=Gedit.View)

    def __init__(self):
        GObject.Object.__init__(self)

    def do_activate(self):
        """Activate plugin."""

        self.doc = self.view.get_buffer()
        self.handler_id = self.doc.connect("save", self.on_document_saving)

    def do_deactivate(self):
        """Deactivate plugin."""

        self.doc.disconnect(self.handler_id)

    def do_update_state(self):
        """Window state updated"""
        pass

    def on_document_saving(self, *args):
        """Strip trailing spaces in document."""

        self.doc.begin_user_action()
        self.strip_trailing_spaces()
        self.strip_eof_newlines()
        self.doc.end_user_action()

    def strip_trailing_spaces(self):
        """
        Pull the buffer into a Python string and then work out which parts we need to delete
        using regular expressions. This is signficiantly faster than just iterating through.
        """

        text = self.doc.get_text(self.doc.get_start_iter(), self.doc.get_end_iter(), False)

        compiledpattern = re.compile('.*?([ \t]+)$', flags=re.MULTILINE)

        start_iter = self.doc.get_start_iter()
        end_iter   = self.doc.get_start_iter()

        line_no        = 0 # Last matched line no
        last_match_pos = 0 # Last matched position in the string

        for match in re.finditer(compiledpattern, text):
            # Count the newlines since the last match
            line_no += text.count('\n', last_match_pos, match.start())

            # Work out the offsets within the line
            whitespace_start = match.start(1) - match.start()
            whitespace_end   = match.end(1) - match.start()

            # Update the iterators and do the deletion
            start_iter.set_line(line_no)
            start_iter.set_line_offset(whitespace_start)

            end_iter.set_line(line_no)
            end_iter.set_line_offset(whitespace_end)

            self.doc.delete(start_iter, end_iter)

            # Update the last match position
            last_match_pos = match.end()

    def strip_eof_newlines(self):
        """Strip empty lines at the end of the file"""

        itr = self.doc.get_end_iter()

        if itr.starts_line():
            while itr.backward_char():
                if not itr.ends_line():
                    itr.forward_to_line_end()
                    break
            self.doc.delete(itr, self.doc.get_end_iter())
