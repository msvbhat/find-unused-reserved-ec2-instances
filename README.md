# find unused reserved ec2 instances

AWS lets us reserve the ec2 instances in particular instance type in Availability Zone or in particular region.
And reserving ec2 instances gets you discount. But sometimes people just reserve some instance types in a AZ or region
but never run them. So when you reserve instances and not running them, you don't the discounts and you have to pay the
full on-demand cost. Since reserved instances are pure billing concept from AWS there is no way to find reserved instances
which aren't running. You can list running and reserved instances and try to find the instances which are reserved but not
running. But this process is manual, tedious and error prone.

So this script lists all the instances which are reserved but are not running. This lists all sunch instances in a particular
account i.e. it lists unused reserved instances in all regions.

### Pre-Requisites to run the script

* This is a python script. So python 2.7 or python 3 should be installed in the instance.
* The script requires non-standard python module `boto3`. Please install them using `pip install boto3`
* AWS keys which has the permission to read the EC2 instance details.


## How to run the script

The script needs to have AWS keys to access to access the EC2 details. [There are multiple ways to configure the keys](https://boto3.readthedocs.io/en/latest/guide/configuration.html). But the simplest way to use ENV variables

```bash
    # export AWS_ACCESS_KEY_ID=<aws access key>
    # export AWS_SECRET_ACCESS_KEY=<aws secret key>
```

Once you have them setup, simply run the script. The script iterates through each region and lists the unused reserved instances.

```bash
    # python find_unused_reserved_ec2_instances.py
```

## TODO

* List the output in a tabular format properly
* List the instances which running but not reserved
