#!/bin/bash
#
[ $(whoami) == 'root' ] || exit
grep '12.04' /etc/lsb-release >/dev/null || exit
[ -a /etc/chef-server ] || exit
echo '[Cookbook version]'
CB_VER=$(knife cookbook list | awk '/nova-network/ {print $2}')
for i in $(knife ssh "role:*" "echo" 2>/dev/null | sort | uniq -w 6); do echo "$i $CB_VER"; done | egrep '[a-zA-Z]'
echo '[Network version]'
[ -f /etc/quantum/quantum.conf ] && NET_VER='Quan'
[ -f /etc/neutron/neutron.conf ] && NET_VER='Neut'
grep FlatDHCPManager /etc/nova/nova.conf > /dev/null && NET_VER='Nova'
for i in $(knife ssh "role:*" "echo" 2>/dev/null | sort | uniq -w 6); do echo "$i $NET_VER"; done | awk 'length>6'
echo '[Gateway device]'
knife ssh "role:*" "ip r | grep default" 2>/dev/null | awk '{print $1,$6}' | sort | uniq -w 6
echo '[NICs]'
knife ssh "role:*" "grep eth /etc/udev/rules.d/70-persistent-net.rules | wc -l" 2>/dev/null
echo '[Kernel version]'
knife ssh "role:*" "uname -r" 2>/dev/null | sort | uniq -w 6
echo '[Nova version]'
knife ssh "role:single-controller OR role:ha-controller1 OR role:ha-controller2 OR role:single-compute" "dpkg -l | grep nova-common" 2>/dev/null | awk '{print $1,$4}' | sort | uniq -w 6
echo '[OVS version]'
knife ssh "role:single-controller OR role:ha-controller1 OR role:ha-controller2 OR role:single-compute" "ovs-vswitchd --version 2>/dev/null | head -n 1" 2>/dev/null | awk '{print $1,$5}' | sort | uniq -w 6
echo '[END]'
