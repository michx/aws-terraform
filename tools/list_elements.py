import boto3
import botocore.exceptions
import json,time

defined_vpc_name='education-vpc'
defined_cluster_name = 'eks-badapp'

#List Keys for this project's cluster having alias = alias/eks/$defined_cluster_name
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
cluster_found=False
client = boto3.client('eks')
try:
    response = client.describe_cluster(name=defined_cluster_name)
    print ('Found the following cluster:',defined_cluster_name,' with cluster-id', response['cluster']['id'])
    cluster_found=True
except:
    print ('EKS Cluster is not here !!')

# Checking Node Groups for Cluster
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

iam=boto3.client('iam')
role_found=False
try:
    roles=iam.list_roles()['Roles']
    for role in roles:
        if defined_cluster_name in role['RoleName']:
            print ('EBSCSI Role is present...')
            role_found=True         
except:
    print ('EBSCSI Role is not here !!')
if role_found==True:
    print ('EKS Role is not here !!') 
try:
    iam.list_policies(Arn='arn:aws:iam::aws:policy/service-role/AmazonEBSCSIDriverPolicy')
    print ('EBSCSI Policy is present...')
except:
    print ('EBSCSI Policy is not here !!')