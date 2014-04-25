# Copyright 2014 Florian Bruhin (The Compiler) <mail@qutebrowser.org>
#
# This file is part of qutebrowser.
#
# qutebrowser is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# qutebrowser is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with qutebrowser.  If not, see <http://www.gnu.org/licenses/>.

"""Contains the Command class, a skeleton for a command."""

import logging

from qutebrowser.commands._exceptions import (ArgumentCountError,
                                              InvalidModeError)

from PyQt5.QtCore import pyqtSignal, QObject


class Command(QObject):

    """Base skeleton for a command.

    Attributes:
        name: The main name of the command.
        maxsplit: Maximum count of splits to be made.
            -1: Split everything (default)
            0:  Don't split.
            n:  Split a maximum of n times.
        hide: Whether to hide the arguments or not.
        nargs: A (minargs, maxargs) tuple, maxargs = None if there's no limit.
        count: Whether the command supports a count, or not.
        desc: The description of the command.
        instance: How to get to the "self" argument of the handler.
                  A dotted string as viewed from app.py, or None.
        handler: The handler function to call.
        completion: Completions to use for arguments, as a list of strings.

    Signals:
        signal: Gets emitted when something should be called via handle_command
                from the app.py context.
    """

    # TODO:
    # we should probably have some kind of typing / argument casting for args
    # this might be combined with help texts or so as well

    signal = pyqtSignal(tuple)

    def __init__(self, name, maxsplit, hide, nargs, count, desc, instance,
                 handler, completion, modes, not_modes):
        # I really don't know how to solve this in a better way, I tried.
        # pylint: disable=too-many-arguments
        super().__init__()
        self.name = name
        self.maxsplit = maxsplit
        self.hide = hide
        self.nargs = nargs
        self.count = count
        self.desc = desc
        self.instance = instance
        self.handler = handler
        self.completion = completion
        self.modes = modes
        self.not_modes = not_modes

    def check(self, args):
        """Check if the argument count is valid and the command is permitted.

        Args:
            args: The supplied arguments

        Raise:
            ArgumentCountError if the argument count is wrong.
            InvalidModeError if the command can't be called in this mode.
        """
        import qutebrowser.keyinput.modes as modeman
        if self.modes is not None and modeman.manager.mode not in self.modes:
            raise InvalidModeError("This command is only allowed in {} "
                                   "mode.".format('/'.join(self.modes)))
        elif (self.not_modes is not None and
              modeman.manager.mode in self.not_modes):
            raise InvalidModeError("This command is not allowed in {} "
                                   "mode.".format('/'.join(self.not_modes)))
        if self.nargs[1] is None and self.nargs[0] <= len(args):
            pass
        elif self.nargs[0] <= len(args) <= self.nargs[1]:
            pass
        else:
            if self.nargs[0] == self.nargs[1]:
                argcnt = str(self.nargs[0])
            elif self.nargs[1] is None:
                argcnt = '{}-inf'.format(self.nargs[0])
            else:
                argcnt = '{}-{}'.format(self.nargs[0], self.nargs[1])
            raise ArgumentCountError("{} args expected, but got {}".format(
                argcnt, len(args)))

    def run(self, args=None, count=None):
        """Run the command.

        Args:
            args: Arguments to the command.
            count: Command repetition count.

        Emit:
            signal: When the command has an instance and should be handled from
                    the app.py context.
        """
        dbgout = ["command called:", self.name]
        if args:
            dbgout += args
        if count is not None:
            dbgout.append("(count={})".format(count))
        logging.debug(' '.join(dbgout))

        if self.instance is not None and self.count and count is not None:
            self.signal.emit((self.instance, self.handler.__name__, count,
                              args))
        elif self.instance is not None:
            self.signal.emit((self.instance, self.handler.__name__, None,
                              args))
        elif count is not None and self.count:
            self.handler(*args, count=count)
        else:
            self.handler(*args)