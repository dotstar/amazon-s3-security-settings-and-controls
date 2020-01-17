#!/bin/bash -xe\n"
# sudo yum update -y\n"
# AZ=`curl -s http://169.254.169.254/latest/meta-data/placement/availability-zone`\n"
# REGION=${AZ::-1}\n"
BUCKET01=$(aws cloudformation list-exports --query Exports[].[Name,Value] --output text | grep LabBucketName | cut -f2)

# echo 'AdminInstance' | sudo tee -a  /proc/sys/kernel/hostname\n"
dd if=/dev/zero of=/tmp/output  bs=1M  count=1\n"
aws s3api put-object --bucket $BUCKET01 --key app1/file1 --body /tmp/output\n"
aws s3api put-object --bucket $BUCKET01 --key app1/file2 --body /tmp/output\n"
aws s3api put-object --bucket $BUCKET01 --key app1/file3 --body /tmp/output\n"
aws s3api put-object --bucket $BUCKET01 --key app1/file4 --body /tmp/output\n"
aws s3api put-object --bucket $BUCKET01 --key app1/file5 --body /tmp/output\n"
aws s3api put-object --bucket $BUCKET01 --key app2/file1 --body /tmp/output\n"
aws s3api put-object --bucket $BUCKET01 --key app2/file2 --body /tmp/output\n"
aws s3api put-object --bucket $BUCKET01 --key app2/file3 --body /tmp/output\n"
aws s3api put-object --bucket $BUCKET01 --key app2/file4 --body /tmp/output\n"
aws s3api put-object --bucket $BUCKET01 --key app2/file5 --body /tmp/output\n"
# sleep 2\n"
# aws ec2 terminate-instances --instance-ids $(curl -s http://169.254.169.254/latest/meta-data/instance-id) --region $REGION\n"