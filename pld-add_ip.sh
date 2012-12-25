#!/bin/bash
#  Copyright (C) 2000-2008, Parallels, Inc. All rights reserved.
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
# Adds IP address(es) in a container running SuSE.

VENET_DEV=venet0
IFCFG_DIR=/etc/sysconfig/interfaces/
IFCFG=${IFCFG_DIR}/ifcfg-${VENET_DEV}
NETFILE=/etc/sysconfig/network
HOSTFILE=/etc/hosts

function setup6_network
{
        [ "${IPV6}" != "yes" ] && return 0

        if ! grep -q 'IPV6INIT="yes"' ${IFCFG}; then
                put_param ${IFCFG} IPV6INIT yes
        fi
        if ! grep -q 'IPV6_NETWORKING=yes' ${NETFILE}; then
                put_param ${NETFILE} IPV6_NETWORKING yes
                put_param ${NETFILE} IPV6_GLOBALROUTEDEV ${VENET_DEV}
                NETWORKRESTART=yes
        fi
}

function get_aliases()
{
	IFNUMLIST=

	[ -f ${IFCFG} ] || return
	IFNUMLIST=`grep -e "^IPADDR" ${IFCFG} | sed 's/^IPADDR\(.*\)=.*/\1/'`
}

function init_config()
{

	mkdir -p ${IFCFG_DIR}
	echo "DEVICE=venet0
ONBOOT=yes
BOOTPROTO=static
BROADCAST=0.0.0.0
NETMASK=255.255.255.255
IPADDR=127.0.0.1" > ${IFCFG} ||
	error "Can't write to file ${IFCFG}" ${VZ_FS_NO_DISK_SPACE}

        put_param $NETFILE NETWORKING yes
        put_param $NETFILE GATEWAY ${FAKEGATEWAY}

        # setup ipv6
        setup6_network

	# Set up /etc/hosts
	if [ ! -f ${HOSTFILE} ]; then
		echo "127.0.0.1 localhost.localdomain localhost" > $HOSTFILE
	fi

}

function create_config()
{
	local ip=$1
	local ifnum=$2

#LABEL_${ifnum}=${ifnum}" >> ${IFCFG} ||
	echo "IPADDR${ifnum}=${ip}" >> ${IFCFG} || error "Can't write to file ${IFCFG}" ${VZ_FS_NO_DISK_SPACE}
}

function add_ip()
{
	local ipm
	local ifnum=0
	local found

	if [ "x${VE_STATE}" = "xstarting" ]; then
		if [ -n "${IP_ADDR}" ]; then
			init_config
		elif grep -q "^IPADDR" ${IFCFG}; then
			init_config
		fi
	elif [ "x${IPDELALL}" = "xyes" ]; then
		init_config
	elif [ ! -f "${IFCFG}" ]; then
		init_config
	fi

	get_aliases
	for ipm in ${IP_ADDR}; do
		ip_conv $ipm
		found=
		if grep -q -w "${_IP}" ${IFCFG}; then
			continue
		fi
		while test -z ${found}; do
			let ifnum++
			if ! echo "${IFNUMLIST}" | grep -w -q "${ifnum}"; then
				found=1
			fi
		done
		if echo ${_IP} | grep -q ':' ; then
			setup6_network
		fi
		create_config ${_IP} ${ifnum}
	done
	if [ "x${VE_STATE}" = "xrunning" ]; then
		ifdown $VENET_DEV  >/dev/null 2>&1
		ifup $VENET_DEV  >/dev/null 2>&1
	fi
}

add_ip

exit 0
# end of script
