#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Glances - An eye on your system
#
# Copyright (C) 2014 Nicolargo <nicolas@nicolargo.com>
#
# Glances is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Glances is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
"""
CPU stats (per cpu)
"""

# Import system libs
# Check for PSUtil already done in the glances_core script
from psutil import cpu_times

# Import Glances libs
from glances.plugins.glances_plugin import GlancesPlugin


class Plugin(GlancesPlugin):
    """
    Glances' PerCpu Plugin

    stats is a list
    """

    def __init__(self):
        GlancesPlugin.__init__(self)

        # We want to display the stat in the curse interface
        self.display_curse = True
        # Set the message position
        # It is NOT the curse position but the Glances column/line
        # Enter -1 to right align
        self.column_curse = 0
        # Enter -1 to diplay bottom
        self.line_curse = 1

        # Init stats
        self.stats = []
        self.percputime_total_new = []
        self.percputime_new = []

    def update(self):
        """
        Update Per CPU stats
        """
        # Grab CPU using the PSUtil cpu_times method
        # Per-CPU
        percputime = cpu_times(percpu=True)
        percputime_total = []
        for i in range(len(percputime)):
            percputime_total.append(percputime[i].user +
                                    percputime[i].system +
                                    percputime[i].idle)

        # Only available on some OS
        for i in range(len(percputime)):
            if hasattr(percputime[i], 'nice'):
                percputime_total[i] += percputime[i].nice
        for i in range(len(percputime)):
            if hasattr(percputime[i], 'iowait'):
                percputime_total[i] += percputime[i].iowait
        for i in range(len(percputime)):
            if hasattr(percputime[i], 'irq'):
                percputime_total[i] += percputime[i].irq
        for i in range(len(percputime)):
            if hasattr(percputime[i], 'softirq'):
                percputime_total[i] += percputime[i].softirq
        for i in range(len(percputime)):
            if hasattr(percputime[i], 'steal'):
                percputime_total[i] += percputime[i].steal
        if not hasattr(self, 'percputime_old'):
            self.percputime_old = percputime
            self.percputime_total_old = percputime_total
            self.stats = []
        else:
            self.percputime_new = percputime
            self.percputime_total_new = percputime_total
            perpercent = []
            self.stats = []
            try:
                for i in range(len(self.percputime_new)):
                    perpercent.append(100 / (self.percputime_total_new[i] -
                                             self.percputime_total_old[i]))
                    cpu = {'user': (self.percputime_new[i].user -
                                    self.percputime_old[i].user) * perpercent[i],
                           'system': (self.percputime_new[i].system -
                                      self.percputime_old[i].system) * perpercent[i],
                           'idle': (self.percputime_new[i].idle -
                                    self.percputime_old[i].idle) * perpercent[i]}
                    if hasattr(self.percputime_new[i], 'nice'):
                        cpu['nice'] = (self.percputime_new[i].nice -
                                       self.percputime_old[i].nice) * perpercent[i]
                    if hasattr(self.percputime_new[i], 'iowait'):
                        cpu['iowait'] = (self.percputime_new[i].iowait -
                                         self.percputime_old[i].iowait) * perpercent[i]
                    if hasattr(self.percputime_new[i], 'irq'):
                        cpu['irq'] = (self.percputime_new[i].irq -
                                      self.percputime_old[i].irq) * perpercent[i]
                    if hasattr(self.percputime_new[i], 'softirq'):
                        cpu['softirq'] = (self.percputime_new[i].softirq -
                                          self.percputime_old[i].softirq) * perpercent[i]
                    if hasattr(self.percputime_new[i], 'steal'):
                        cpu['steal'] = (self.percputime_new[i].steal -
                                        self.percputime_old[i].steal) * perpercent[i]
                    self.stats.append(cpu)
                self.percputime_old = self.percputime_new
                self.percputime_total_old = self.percputime_total_new
            except Exception:
                self.stats = []

    def msg_curse(self, args=None):
        """
        Return the dict to display in the curse interface
        """

        # Init the return message
        ret = []

        # Build the string message
        # Header
        msg = "{0:8}".format(_("PER CPU"))
        ret.append(self.curse_add_line(msg, "TITLE"))

        # Total CPU usage
        for cpu in self.stats:
            msg = " {0}".format(format((100 - cpu['idle']) / 100, '>6.1%'))
            ret.append(self.curse_add_line(msg))

        # User CPU
        if ('user' in self.stats[0]):
            # New line
            ret.append(self.curse_new_line())
            msg = "{0:8}".format(_("user:"))
            ret.append(self.curse_add_line(msg))
            for cpu in self.stats:
                msg = " {0}".format(format(cpu['user'] / 100, '>6.1%'))
                ret.append(self.curse_add_line(msg, self.get_alert(cpu['user'], header="user")))

        # System CPU
        if ('user' in self.stats[0]):
            # New line
            ret.append(self.curse_new_line())
            msg = "{0:8}".format(_("system:"))
            ret.append(self.curse_add_line(msg))
            for cpu in self.stats:
                msg = " {0}".format(format(cpu['system'] / 100, '>6.1%'))
                ret.append(self.curse_add_line(msg, self.get_alert(cpu['system'], header="system")))

        # IoWait CPU
        if ('user' in self.stats[0]):
            # New line
            ret.append(self.curse_new_line())
            msg = "{0:8}".format(_("iowait:"))
            ret.append(self.curse_add_line(msg))
            for cpu in self.stats:
                msg = " {0}".format(format(cpu['iowait'] / 100, '>6.1%'))
                ret.append(self.curse_add_line(msg, self.get_alert(cpu['iowait'], header="iowait")))

        # Return the message with decoration
        return ret
