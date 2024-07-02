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
client = boto3.client('eks')
response = client.describe_cluster(name=defined_cluster_name)
if cluster in response:
    print ('Found the following cluster:',defined_cluster_name)
else:
    print ('EKS Cluster is not here !!')