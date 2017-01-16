import sys
from pprint import pprint

import boto3


def get_unused_reserved_instances(region):
    client = boto3.client('ec2', region_name=region)
    running_instances = client.describe_instances(Filters=[{ \
                        'Name': 'instance-state-name', 'Values': ['running']}])
    running_ec2 = {}
    # populate a dict of {(instance-type, availability-zone):num of instances}
    for instances in running_instances['Reservations']:
        for ec2 in instances['Instances']:
            if not 'SpotInstanceRequestId' in ec2:
                instance_type = ec2['InstanceType']
                az = ec2['Placement']['AvailabilityZone']
                running_ec2[(instance_type, az)] = running_ec2.get(
                    (instance_type, az), 0) + 1

    reserved_instances = client.describe_reserved_instances(
        Filters=[{'Name': 'state', 'Values': ['active']}])
    # populate a dict each for reserved instances with Region and
    # Availability Zone scope.
    reserved_ec2_az = {}
    reserved_ec2_region = {}
    for ri in reserved_instances['ReservedInstances']:
        instance_type = ri['InstanceType']
        instance_count = int(ri['InstanceCount'])
        # populate the {{instance-type, availability-zone) :
        # reserved instance count} for instances with scope Availability Zone
        if ri['Scope'] == 'Availability Zone':
            az = ri['AvailabilityZone']
            reserved_ec2_az[(instance_type, az)] = reserved_ec2_az.get(
                (instance_type, az), 0) + instance_count
        # populate the dict {instance-type : number of instances reserved} for
        # instances with the Region scope.
        elif ri['Scope'] == 'Region':
            reserved_ec2_region[instance_type] = instance_count
        else:
            sys.stderr.write(
                "AWS has updated something and this script doesn't handle it")

    # If an instance is reserved but not running, add it the running
    # instances dict. That makes sure that the running_ec2 is a
    # superset of reserved_ec2_az
    for ec2 in reserved_ec2_az:
        if ec2 not in running_ec2:
            running_ec2[ec2] = 0

    # Subract the reserved instances from the running instances.
    # The negative value in the result means that
    # there are more reserved instances than running instances indicating
    # unused reserved instances
    remaining_running_ec2 = dict([
        (x, running_ec2[x] - reserved_ec2_az.get(x, 0)) for x in running_ec2])

    # Add the keys with negative value to unused_reserved_instances
    unused_reserved_instances = dict([(x, -remaining_running_ec2[x])
                                      for x in remaining_running_ec2 if
                                      remaining_running_ec2[x] < 0])

    # populate the remaining running instances in the region.
    # Exclude the negative values, since they are aready listed in the
    # unused_reserved_instances
    running_ec2_region = {}
    for ec2, count in remaining_running_ec2.items():
        if count > 0:
            running_ec2_region[ec2[0]] = running_ec2_region.get(
                ec2[0], 0) + count

    # Add the instances that are reserved with region scope but not running.
    # This makes sure that the running instance dict is the superset of the
    # reserved instances dict
    for ec2 in reserved_ec2_region:
        if ec2 not in running_ec2_region:
            running_ec2_region[ec2] = 0
    # Any negative value here indicates that there are more reserved
    # instances that running.
    remaining_running_ec2 = dict([(x, running_ec2_region[x] -
                                   reserved_ec2_region.get(x, 0))
                                  for x in running_ec2_region])
    unused_reserved_instances_region = dict([((x, region), -
                                              remaining_running_ec2[x])
                                             for x in remaining_running_ec2 if
                                             remaining_running_ec2[x] < 0])
    return dict(unused_reserved_instances_region.items() + unused_reserved_instances.items())


if __name__ == '__main__':
    client = boto3.client('ec2', region_name='ap-south-1')
    regions = [region['RegionName'] for region in client.describe_regions()['Regions']]
    unused_reserved_instances = {}
    for region in regions:
        unused_reserved_instances.update(get_unused_reserved_instances(region))
    if not unused_reserved_instances:
        print("Congratulations! There are no unused reserved instances")
    else:
        print("You have following reserved instances which aren't being used at the moment")
        pprint(unused_reserved_instances)
