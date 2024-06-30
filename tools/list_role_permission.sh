#!/bin/bash

# Check if role name is provided
if [ -z "$1" ]; then
    echo "Usage: $0 ROLE_NAME"
    exit 1
fi

ROLE_NAME=$1

# Step 1: List attached policies for the role
echo "Listing policies attached to role: $ROLE_NAME"
POLICIES=$(aws iam list-attached-role-policies --role-name "$ROLE_NAME" --query "AttachedPolicies[].PolicyArn" --output text)

if [ -z "$POLICIES" ]; then
    echo "No policies attached to the role: $ROLE_NAME"
    exit 0
fi

# Step 2: Iterate over each policy ARN and get specific actions
for POLICY_ARN in $POLICIES; do
    echo "Processing policy: $POLICY_ARN"

    # Get policy details to find the default version ID
    POLICY_VERSION_ID=$(aws iam get-policy --policy-arn "$POLICY_ARN" --query "Policy.DefaultVersionId" --output text)

    # Get the policy document for the default version
    POLICY_DOCUMENT=$(aws iam get-policy-version --policy-arn "$POLICY_ARN" --version-id "$POLICY_VERSION_ID" --query "PolicyVersion.Document" --output json)

    # Extract and print the actions
    ACTIONS=$(echo "$POLICY_DOCUMENT" | jq -r '.Statement[].Action | @csv' | tr -d '"')
    echo "Actions granted by policy $POLICY_ARN:"
    echo "$ACTIONS"
    echo ""
done