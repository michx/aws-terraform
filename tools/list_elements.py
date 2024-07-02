import boto3
import botocore.exceptions
import json,time

defined_vpc_name='education-vpc'
defined_cluster_name = 'eks-badapp'

#List Keys for this project's cluster having alias = alias/eks/$defined_cluster_name
kms_client= boto3.client('kms')
response=kms_client.list_keys()
for key in response['Keys']:
    if aliases:=kms_client.list_aliases(KeyId=key['KeyId']):
        for alias in aliases['Aliases']:
            if alias['AliasName']==str('alias/eks/'+defined_cluster_name):
                print ('Found Key for cluster ', defined_cluster_name,' : ',alias['AliasId'])
                