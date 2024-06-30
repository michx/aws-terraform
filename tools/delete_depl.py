import boto3
import botocore.exceptions
import json,time

defined_vpc_name='education-vpc'

client = boto3.client('eks')

response = client.list_clusters()
clusters=response['clusters']
if clusters:
    print ('Found the following clusters:',clusters)

# Deleting the Node Groups in clusters

for cluster in clusters:
    print ('Searching for nodes and nodegrous in cluster:', cluster)
    nodegroups=client.list_nodegroups(clusterName=cluster)['nodegroups']
    print ('Found the following node groups: ', nodegroups)
    for ng in nodegroups:
        print ('Deleteing thw nodegroup :' , ng)
        ng_deleted=False
        while ng_deleted==False:
            try: 
                response_delete=client.delete_nodegroup(clusterName=cluster,nodegroupName=ng)
                print ('Status :', response_delete['nodegroup']['status'])
                time.sleep(5)
            except:
                print ('Nodegroup Deleted :', ng)
                ng_deleted=True
    cluster_delete=False
    while cluster_delete==False:
        try:
            reponse_delete_cluster=client.delete_cluster(name=cluster)
            print ('Status : ',response_delete_cluster['cluster']['status'])
            time.sleep(5)
        except:
            print ('Cluster deleted :', cluster)
            cluster_delete=True

# Deleting Related Log Groups

log_client=boto3.client('logs')
response=log_client.describe_log_groups()
lgs=response['logGroups']
lgs_name=[]
for group in lgs:
    if 'eks' in group['logGroupName']:
        print ('Found and deleting the following log groups : ',group['logGroupName'])
        log_client.delete_log_group(logGroupName=group['logGroupName'])

# Deleting Network Interfaces, Subnets and VPC

network_client=boto3.client('ec2')
response=network_client.describe_vpcs()
for vpc in response['Vpcs']:
    if vpc['Tags'][0]['Value']==defined_vpc_name:
        defined_Vpc_id=vpc['VpcId']
if defined_Vpc_id:
    subnets=network_client.describe_subnets()['Subnets']
    for subnet in subnets:
        if subnet['VpcId']==defined_Vpc_id:
            # Deleting NAT Gateways
            nat_gateways=network_client.describe_nat_gateways(Filters=[{'Name':'subnet-id','Values':[subnet['SubnetId']]}])
            for nat in nat_gateways['NatGateways']:
                try:
                    network_client.delete_nat_gateway(NatGatewayId=nat['NatGatewayId'])
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
