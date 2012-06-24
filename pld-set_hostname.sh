#!/bin/sh
#  Copyright (C) 2000-2007 SWsoft. All rights reserved.
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#
# This script sets up hostname inside VE for PLD like system
# For usage info see vz-veconfig(5) man page.
#
# Some parameters are passed in environment variables.
# Required parameters:
# Optional parameters:
#   HOSTNM
#       Sets host name for this VE. Modifies /etc/hosts and
#       /etc/sysconfig/network (in PLD)
function set_hostname
{
	local cfgfile="$1"
	local var=$2
	local val=$3

	[ -z "${val}" ] && return 0
	put_param "${cfgfile}" "${var}" "${val}"

	hostname "${val}"
}

change_hostname /etc/hosts "${HOSTNM}" "${IP_ADDR}"
set_hostname /etc/sysconfig/network HOSTNAME "${HOSTNM}"

exit 0

