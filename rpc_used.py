#!/usr/bin/env python
#

import os
import sys
import subprocess
import re
import requests

def exec_cmd(cmd, verbose=True):
    result = []
    out = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in iter(out.stdout.readline, b''):
        if verbose:
            print(line.rstrip())
        result.append(line.strip())
    return result

if __name__ == '__main__':
    PARAMS = ['OS_ENDPOINT_TYPE', 'OS_USERNAME', 'OS_PASSWORD', 'OS_TENANT_NAME', 'OS_AUTH_URL']
    ENV_PARAMS = []
    for i in PARAMS:
        ENV_PARAMS.append(os.environ[i])
    NOVA_PARAMS = dict(zip(PARAMS, ENV_PARAMS))

    USAGE_VARS = ['HYP_COUNT', 'DISK_AVAIL', 'DISK_TOTAL', 'DISK_USED', 'RAM_TOTAL', 'RAM_USED', 'VCPUS_TOTAL', 'VCPUS_USED']
    nova_cmd = ['nova', '--endpoint-type', NOVA_PARAMS['OS_ENDPOINT_TYPE'], '--os-username', NOVA_PARAMS['OS_USERNAME'], '--os-password', NOVA_PARAMS['OS_PASSWORD'], '--os-tenant-name', NOVA_PARAMS['OS_TENANT_NAME'], '--os-auth-url', NOVA_PARAMS['OS_AUTH_URL']]
    print('\n-= Overall Environment Resource Utilization =-\n(Percentages take into account allocation ratios)\n')
    hypstats = exec_cmd(nova_cmd + ['hypervisor-stats'], verbose=False)

    USAGE_REGEX = ['count', 'disk_available_least', 'local_gb ', 'local_gb_used', 'memory_mb ', 'memory_mb_used', 'vcpus ', 'vcpus_used']
    USAGE_VALS = []
    for line in hypstats:
        for i in USAGE_REGEX:
            if re.search(i, line):
                USAGE_VALS.append(float(line.split()[3]))
    USAGE = dict(zip(USAGE_VARS, USAGE_VALS))

    hyplist = exec_cmd(nova_cmd + ['hypervisor-list'], verbose=False)
    hypervisors = []
    for line in hyplist:
        if re.search('Compute|compute', line):
            hypervisors.append(line.split()[3])
    hypervisors.sort()

    CONTAINERS = exec_cmd(['lxc-ls'], verbose=False)
    for i in CONTAINERS:
        if re.search('nova_scheduler', i):
            RATIOS = exec_cmd(['lxc-attach', '-n', i, '--', 'grep', 'ratio', '/etc/nova/nova.conf'], verbose=False)

    ALLOCATION_RATIOS = []
    for line in RATIOS:
        for i in ['cpu', 'disk', 'ram']:
            if re.search(i, line):
                ALLOCATION_RATIOS.append(float(line.split()[2]))
    print("Hypervisors in Cluster : %d" % (USAGE['HYP_COUNT']))
    print
    print("Total Disk in Cluster : %s GB" % (USAGE['DISK_TOTAL']))
    print("Disk in Use : %s GB" % (USAGE['DISK_USED']))
    print("Calculated Disk Available : %s GB" % (USAGE['DISK_AVAIL']))
    print("Percent of Disk Used : %.2f %%" % (((USAGE['DISK_TOTAL'] - USAGE['DISK_AVAIL']) / (USAGE['DISK_TOTAL'] * ALLOCATION_RATIOS[0])) * 100 ))
    print
    print("Total RAM in Cluster : %s GB" % (USAGE['RAM_TOTAL']))
    print("RAM in Use : %s GB" % (USAGE['RAM_USED']))
    print("Percent of RAM Used : %.2f %%" % ((USAGE['RAM_USED'] / (USAGE['RAM_TOTAL'] * ALLOCATION_RATIOS[2])) * 100 ))
    print
    print("Total vCPUs in Cluster : %d" % (USAGE['VCPUS_TOTAL']))
    print("vCPUs in Use : %d" % (USAGE['VCPUS_USED']))
    print("Percent of vCPUs Used : %.2f %%" % ((USAGE['VCPUS_USED'] / (USAGE['VCPUS_TOTAL'] * ALLOCATION_RATIOS[0])) * 100 ))
    print
    print("CPU Allocation Ratio : %s\nDisk Allocation Ratio : %s\nRAM Allocation Ratio : %s\n" % (ALLOCATION_RATIOS[0], ALLOCATION_RATIOS[1], ALLOCATION_RATIOS[2]))
