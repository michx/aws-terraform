import boto3
import botocore.exceptions
import json,time
from termcolor import colored

defined_vpc_name='education-vpc'
defined_cluster_name = 'eks-badapp'

#List Keys for this project's cluster having alias = alias/eks/$defined_cluster_name
print (colored('#List Keys for this project cluster having alias = alias/eks/$defined_cluster_name','green'))
      
kms_client= boto3.client('kms')
response=kms_client.list_keys()
key_found=False
for key in response['Keys']:
    if aliases:=kms_client.list_aliases(KeyId=key['KeyId']):
        for alias in aliases['Aliases']:
            if alias['AliasName']==str('alias/eks/'+defined_cluster_name):
                print ('Found Key for cluster ', defined_cluster_name,' : ',alias['AliasId'])
                key_found=True
if key_found==False:
    print ("No KMS key found for the EKS cluster")


# Check if EKS Cluster is there
print (colored('# Check if EKS Cluster is there','green'))
cluster_found=False
client = boto3.client('eks')
try:
    response = client.describe_cluster(name=defined_cluster_name)
    print ('Found the following cluster:',defined_cluster_name,' with cluster-id', response['cluster']['id'])
    cluster_found=True
except:
    print ('EKS Cluster is not here !!')

# Checking Node Groups for Cluster
print (colored('# Checking Node Groups for Cluster','green'))
nodegroups_found=False
if cluster_found==True:
    print ('Searching for nodes and nodegroups in :', defined_cluster_name)
    try:
        nodegroups=client.list_nodegroups(clusterName=defined_cluster_name)['nodegroups']
        print ('Found the following node groups: ', nodegroups)
        nodegroups_found=True
        for ng in nodegroups:
            print ('NodeGroup ID :' , ng)
    except:
        print ('No Nodegroups found in cluster ',defined_cluster_name)

# Checking Related Log Groups
print (colored('# Checking Related Log Groups','green'))
log_client=boto3.client('logs')
try:
    response=log_client.describe_log_groups()
except:
    print ('No Log Groups found !!')
lgs=response['logGroups']
logs_found=False
for group in lgs:
    if 'eks' in group['logGroupName']:
        print ('Found  the following log group : ',group['logGroupName'])
        logs_found=True
if logs_found==False:
    print ('No EKS Log Groups found !!')

# Checking IAM role for executing Cluster management
print (colored('# Checking IAM role for executing Cluster management','green'))
iam=boto3.client('iam')
role_found=False
try:
    roles=iam.list_roles()['Roles']
    for role in roles:
        if defined_cluster_name in role['RoleName']:
            print ('EBSCSI Role is present...Role Name :',role['RoleName'])
            role_found=True         
except:
    print ('EBSCSI Role is not here !!')
if role_found==False:
    print ('EKS Role is not here !!') 
try:
    iam.list_policies(Arn='arn:aws:iam::aws:policy/service-role/AmazonEBSCSIDriverPolicy')
    print ('EBSCSI Policy is present...')
except:
    print ('EBSCSI Policy is not here !!')


# Deleting Network Interfaces, Subnets and VPC

network_client=boto3.client('ec2')
response=network_client.describe_vpcs()
for vpc in response['Vpcs']:
    if vpc['Tags'][0]['Value']==defined_vpc_name:
        defined_Vpc_id=vpc['VpcId']
if not defined_Vpc_id:
    print ("VPC not present!!")
else:
    print ("VPC is here with vpc-id : ",defined_Vpc_id)
    subnets=network_client.describe_subnets()['Subnets']
    for subnet in subnets:
        if subnet['VpcId']==defined_Vpc_id:
            # Deleting NAT Gateways
            nat_gateways=network_client.describe_nat_gateways(Filters=[{'Name':'subnet-id','Values':[subnet['SubnetId']]}])
            for nat in nat_gateways['NatGateways']:
                try:
                    network_client.delete_nat_gateway(NatGatewayId=nat['NatGatewayId'])
                    network_client.get_waiter('nat_gateway_deleted')
                    print ('Deleted NAT Gateway for Subnet :', subnet['SubnetId'])
                except botocore.exceptions.ClientError as error:
                    print (error)
            network_interfaces=network_client.describe_network_interfaces(Filters=[{'Name':'subnet-id','Values':[subnet['SubnetId']]}])
            for ifs in  network_interfaces['NetworkInterfaces']:
                try:
                    network_client.delete_network_interface(NetworkInterfaceId=ifs['NetworkInterfaceId'])
                    print ('Delete Network Interface for subnet: ', subnet['SubnetId'])
                except botocore.exceptions.ClientError as error:
                    print (error)
            print ('Found and deleting the following subnet:', subnet['SubnetId'])
            try:
                network_client.delete_subnet(SubnetId=subnet['SubnetId'])
            except botocore.exceptions.ClientError as error:
                print (error)
        # Deleting Internet Gateways
    igw_gateways=network_client.describe_internet_gateways(Filters=[{'Name':'attachment.vpc-id','Values':[defined_Vpc_id]}])
    for igw in igw_gateways['InternetGateways']:
        try:
            network_client.detach_internet_gateway(VpcId=defined_Vpc_id,InternetGatewayId=igw['InternetGatewayId'])
            network_client.delete_internet_gateway(InternetGatewayId=igw['InternetGatewayId'])
            print ('Deleted IGW Gateway for Subnet :', subnet['SubnetId'])
        except botocore.exceptions.ClientError as error:
            print (error)
    # Deleting Routing Tables
    routing_tables=network_client.describe_route_tables(Filters=[{'Name':'vpc-id','Values':[defined_Vpc_id]}])
    for rt in routing_tables['RouteTables']:
        if rt['Associations'][0]['Main']!=True:
            try:
                network_client.delete_route_table(RouteTableId=rt['RouteTableId'])
                print ('Deleted Routing Table for VPC:', defined_vpc_name)
            except botocore.exceptions.ClientError as error:
                print (error)
    # Deleting Security Groups
    security_groups=network_client.describe_security_groups(Filters=[{'Name':'vpc-id','Values':[defined_Vpc_id]}])
    for sg in security_groups['SecurityGroups']:
        if sg['GroupName']!='default':
            for items in network_client.describe_security_group_rules(Filters=[{'Name':'group-id','Values':[sg['GroupId']]}])['SecurityGroupRules']:
                if 'ReferencedGroupInfo' in items.keys() and items['ReferencedGroupInfo']['GroupId']!=sg['GroupId']:
                    try:
                        network_client.revoke_security_group_ingress(SecurityGroupRuleIds=[items['SecurityGroupRuleId']],GroupId=sg['GroupId'])
                    except botocore.exceptions.ClientError as error:
                        print (error)
            try:
                network_client.delete_security_group(GroupId=sg['GroupId'])
                print ('Deleted Routing Table for VPC:', defined_vpc_name)
            except botocore.exceptions.ClientError as error:
                print (error)
    # Deleting VPC
    try:
        network_client.delete_vpc(VpcId=defined_Vpc_id)
        print ('Deleted the VPC: ', defined_vpc_name)
    except botocore.exceptions.ClientError as error:
        print(error)

# Deleting 