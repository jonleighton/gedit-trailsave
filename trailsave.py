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

        self.save_position()
        self.doc.begin_user_action()

        text = self.doc.get_text(self.doc.get_start_iter(), self.doc.get_end_iter(), False)
        text = re.sub('[ \t]*$', '', text, flags=re.MULTILINE)
        text = re.sub('\n+$', '', text)

        self.doc.set_text(text, len(text))

        self.doc.end_user_action()
        self.restore_position()

    def save_position(self):
        """Save the cursor/scroll position"""

        self.scroll = self.view.get_vadjustment()

        cursor = self.doc.get_iter_at_mark(self.doc.get_insert())

        self.cursor_line        = cursor.get_line()
        self.cursor_line_offset = cursor.get_line_offset()

    def restore_position(self):
        """Restore the cursor/scroll position"""

        end_iter         = self.doc.get_end_iter()
        self.cursor_line = min(self.cursor_line, end_iter.get_line())

        cursor_line_iter        = self.doc.get_iter_at_line(self.cursor_line)
        self.cursor_line_offset = min(
          self.cursor_line_offset,
          max(cursor_line_iter.get_chars_in_line() - 1, 0)
        )

        cursor = self.doc.get_iter_at_line_offset(self.cursor_line, self.cursor_line_offset)
        self.doc.place_cursor(cursor)

        # FIXME: This doesn't actually work
        self.view.set_vadjustment(self.scroll)
