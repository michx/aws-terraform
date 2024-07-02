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
response=log_client.describe_log_groups()
lgs=response['logGroups']
lgs_name=[]
for group in lgs:
    if 'eks' in group['logGroupName']:
        print ('Found  the following log group : ',group['logGroupName'])

