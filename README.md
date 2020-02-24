# **Amazon S3 Security Settings and Controls**

© 2020 Amazon Web Services, Inc. and its affiliates. All rights reserved.
This sample code is made available under the MIT-0 license. See the LICENSE file.

---
## Workshop Summary

This lab is a fork of the S3 Security lab created by Mike Burbey (https://github.com/aws-samples/amazon-s3-security-settings-and-controls ).  It has been edited for time.  The student may wish to review that lab for additional security settings and controls.  

This workshop will focus on several areas of the [AWS Security Best Practices for S3](https://docs.aws.amazon.com/AmazonS3/latest/dev/security-best-practices.html), including:

1. Block Public Access
2. Require HTTPS
3. Require SSE-S3 Encryption
4. Enable Versioning
5. Using VPC endpoints and S3 Bucket policies
6. Extra Credit - Share your bucket with another AWS account

### Requirements

* AWS account - if you're doing this workshop as a part of an AWS event, you will be provided an account through a platform called Event Engine. The workshop administrator will provide instructions. If the event specifies you'll need your own account or if you're doing this workshop on your own, it's easy and free to [create an account](https://aws.amazon.com/) if you do not have one already.
* If using your own AWS account you will need to run a submit CloudFormation template which creates a VPC, Cloud9, and an S3 bucket.  Instructions follow, expand the section *"> If you are using your own account"*

Familiarity with AWS, S3, CloudFormation, and Cloud9 is a plus but not required.

<details><summary>If you are using your own account</summary>

## Deploy AWS resources using CloudFormation

### Use the CloudFormation CLI to create the lab

The lab CloudFormation templates are in the *cfn* directory. We've automated the creation of the stack, which includes a Cloud9 instance, a small VPC, and a pre-populated S3 bucket.

Download the lab to a shell where you will have access to _git_, the _AWS CLI_,  and _make_.

We need an S3 bucket, to upload our CloudFormation custom resource.  The bucket is created based on the Linux UUID command.  Make sure that _uuid_ is available on your system before building the CloudFormation template.


```
git clone https://github.com/dotstar/amazon-s3-security-settings-and-controls.git
cd amazon-s3-security-settings-and-controls/cfn
make deploy
```
</details>

<details><summary>If you are running this lab at an AWS Event</summary>



If you are running this at an AWS event, the CloudFormation script has already been executed for you.  You have a terminal session, powered by AWS Cloud9.

At the event, you will be provided a 12-digit hash which provides temporary access to an AWS account.


## 1. Getting started with _Event Engine_

In this first lab, we will create parameters.

Start by logging into to [Event Engine](https://dashboard.eventengine.run/login).

Enter your 12-digit hash and Accept.


![Login](img/1.png).


Select AWS Console. 

<div align="center">

![AWS Console button](img/2.png)
</div>

And again on the Team Dashboard, select Console 
<div align="center">

![AWS Console button 2](img/3.png)

</div>

From the AWS console, navigate to [Cloud9](https://console.aws.amazon.com/cloud9/home?region=us-east-1) and "Open IDE"
<div align="center">

![Cloud9 IDE](img/4.png)
</div>

</details>

### IMPORTANT: Workshop Cleanup

If you're attending an AWS event and are provided an account to use, you can ignore this section because we'll destroy the account once the workshop concludes.  

**If you are using your own account**, it is **VERY** important you clean up resources created during the workshop. Follow these steps once you're done going through the workshop to delete resources that were created.  Please follow the instructions, at the end of the lab, to delete these resources.  If you used the CloudFormation templates, as described in the instructions, simply delete the CloudFormation stack.  One way to do this is:

```
cd cfn
make delete
```

## Exercise #1 - Block Public Access

By default, AWS buckets are not publicly accessible.  You do not need to make them publicly available to share with another account, role, or user.  We will explore one method of granting read-only access to another account later in this lab.

There are legitimate reasons to enable public access, such as using S3 to host web content or to share public-domain data.  The general rule, don't make the bucket public without purpose.

Should you make a bucket public, you'll see this console icon.
<div align="center">

![public button](img/5.png)
</div>

For this lab we will **not** be adding any public S3 access.  We will set a policy to disable public access for the account-wide.

Navigate to the [S3 Console](https://console.aws.amazon.com/s3/home?region=us-east-1#).

On the left-side panel, there is a selection "Block public access (account settings)"

<div align="center">

![account defaults](img/6.png)
</div>

Click here, to set the account-wide defaults.

<div align="center">

![account default settings](img/7.png)
</div>

Click Edit, then select the check mark, Block _all_ public access.  Click **Save** to save your changes, then confirm that you really intend to block public access.

A word of explanation on these choices. There are two ways to control access, ACLs and bucket policies. The ACL mechanism is dated and not recommended for future use, but remains for backward compatibility.  We will visit bucket policies, a little later on in this lab.

For both _ACLs_ and _bucket policies_, you can chose whether to enforce rules for existing or future buckets.

You have successfully set the account to not allow public S3 access.  Please proceed to exercise 2.

## Exercise #2- Require HTTPS

In this exercise we will create a S3 Bucket Policy that requires connections to be secure.

1. Navigate to the [S3 console](https://s3.console.aws.amazon.com/s3/home). 
2. Select our bucket.  If you are unsure of it's name, check the CloudFormation outputs.
3. Click on the **Permissions** tab.  
4. Click **Bucket Policy**.  
5. Copy the bucket policy below and paste into the Bucket Policy Editor.
```json
{
"Statement": [
{
   "Action": "s3:*",
   "Effect": "Deny",
   "Principal": "*",
   "Resource": "arn:aws:s3:::BUCKET_NAME/*",
   "Condition": {
       "Bool": {
        "aws:SecureTransport": false
        }
    }
    }
  ]
}
```

6. Replace BUCKET_NAME with the bucket name.  Sample bucket policy below.

  ![](/images/https_bucket_policy.png)

7. Click **Save**
8. In your Cloud9 terminal run the following command. You will need to replace <YOUR-BUCKET_NAME_HERE> with the name of your S3 bucket.  The command should return a __403 error__ since the endpoint-url is HTTP.

```bash
    export bucket=<YOUR-BUCKET-NAME-HERE>
    aws s3api head-object --endpoint-url http://s3.amazonaws.com --key app1/file1 --bucket ${bucket}
```

9. In your Cloud9 terminal run the following command. This command should succeed since it is using HTTPS.

```bash
    aws s3api --endpoint-url https://s3.amazonaws.com head-object --key app1/file1 --bucket ${bucket}
```
This will return output similar to the following on success.

```json
{
    "AcceptRanges": "bytes", 
    "ContentType": "binary/octet-stream", 
    "LastModified": "Mon, 24 Feb 2020 15:51:49 GMT", 
    "ContentLength": 1048576, 
    "ETag": "\"b6d81b360a5672d80c27430f39153e2c\"", 
    "Metadata": {}
}
```
You have successfully set the bucket policy to require HTTPS.  Please proceed to Exercise 3.

## Exercise #3- Require SSE-S3 Encryption

In this exercise we will create a S3 Bucket Policy that requires data at rest encryption.  We will also look at Default Encryption.

1. Navigate to the [S3 console](https://s3.console.aws.amazon.com/s3/home) and open the bucket. 
3. Click on the **Permissions** tab.  
4. Click **Bucket Policy**.  
5. Delete the bucket policy we created in lab2.  Click **Delete**, click **Delete** to confirm.  
6. Copy the bucket policy below and paste into the Bucket Policy Editor, then **Save**.

   This policy denies __PUT__ requests which don't included the _x-amz-server-side-encryption_ header, thus it denies all unencrypted PUTS.  If interested, visit [this blog](https://aws.amazon.com/blogs/security/how-to-prevent-uploads-of-unencrypted-objects-to-amazon-s3/) for more information on requiring bucket object encryption.


```json
{
    "Statement": [
        {
            "Effect": "Deny",
            "Principal": "*",
            "Action": "s3:PutObject",
            "Resource": "arn:aws:s3:::BUCKET_NAME/*",
            "Condition": {
                "StringNotEquals": {
                    "s3:x-amz-server-side-encryption": "AES256"
                }
            }
        }
    ]
}
```




7. Time to test the new policy. Go to your SSH session and create a small text file using the following command.
   ```
   cd ~  
   echo "123456789abcdefg" > textfile  
   ```
8.  Attempt to PUT an object without encryption. The request should fail.
  ```
  # put the object without encryption - **this should fail**
  aws s3api put-object --key text01 --body textfile --bucket ${bucket}
  ```
9. PUT an object using SSE-S3.  The request should succeed.
  ```
  # put the object with encryption
  aws s3api put-object --key text01 --body textfile --server-side-encryption AES256 --bucket ${bucket}  
  ```
10. From the AWS console, click  **Services**  and select  **S3.** 

Default Encryption for AES-256 (SSE-S3) is enabled.  

###### What if you want both HTTPS and Encryption?

A bucket can only have a single policy.  As such, by pasting in the policy above, you are removing the policy to require HTTPS which we created in the prior exercise.  To have both HTTPS and require server-side encryption, you add both statements as a JSON array, similar to:

```json

{
  "Statement": [
    {
      "Action": "s3:*",
      "Effect": "Deny",
      "Principal": "*",
      "Resource": "arn:aws:s3:::BUCKET_NAME/*",
      "Condition": {
        "Bool": {
          "aws:SecureTransport": false
        }
      }
    },
    {
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:PutObject",
      "Resource": "arn:aws:s3:::BUCKET_NAME/*",
      "Condition": {
        "StringNotEquals": {
          "s3:x-amz-server-side-encryption": "AES256"
        }
      }
    }
  ]
}

```
11. Change the bucket policy to require https and to require object encryption by using the policy above.  Run the test commands in labs 2 and 3 to confirm successful policy creation.

## Exercise #4 - Enable Versioning

S3 is designed to provide 99.999999999% durability (11 9's). For example, if you store 10,000,000 objects with Amazon S3, you can on average expect to incur a loss of a single object once every 10,000 years. In addition, Amazon S3 Standard, S3 Standard-IA, and S3 Glacier are all designed to sustain data in the event of an entire S3 Availability Zone loss.

The biggest threat to your data is an application bug or human error.  One way to protect against this is to enable [versioning](https://docs.aws.amazon.com/AmazonS3/latest/dev/Versioning.html).

Versioning allows you to preserve, retrieve, and restore every version of every object stored in an Amazon S3 bucket. Once you enable versioning for a bucket, Amazon S3 preserves existing objects anytime you perform a PUT, POST, COPY, or DELETE operation on them. By default, GET requests will retrieve the most recently written version. Older versions of an overwritten or deleted object can be retrieved by specifying a version in the request.

Since versioning potentially keeps multiple copies of your object, incremental storage prices apply.  You can use [ Lifecycle rules ](https://docs.aws.amazon.com/AmazonS3/latest/user-guide/create-lifecycle.html) along with versioning to implement a rollback window for your Amazon S3 objects.

In this lab, you will enable versioning of a bucket, then delete an object.  Finally, you will _undelete_ the object.

1. Navigate to the [S3 Console](https://console.aws.amazon.com/s3/home?region=us-east-1)
2. Click on your bucket, then select Properties.


<div align="center">

![account defaults](img/8.png)
</div>

3. Select the Versioning button, and enable Versioning.

<div align="center">

![account defaults](img/9.png)
</div>

4. In the terminal window, create a temporary file, and over-write one of the existing files in the bucket.

```bash
bucket=YOUR_BUCKET_NAME_HERE
dd if=/dev/zero of=/tmp/tmpfile bs=1024 count=5
aws s3 cp /tmp/tmpfile s3://$bucket/app1/file1 --sse AES256
```

5. Go back to the S3 console to explore the result.  Make sure you are on the **Overview** tab.  Navigate to /app1 in your bucket, and click the button "Verions Show".  

You now have the old version and the new version of the **_/app1/file1_** object.

<div align="center">

![file versions](img/10.png)
</div>

6. In the terminal, delete the file.

```bash
bucket=YOUR_BUCKET_NAME_HERE
aws s3 rm s3://$bucket/app1/file1
```

In the console you will see that the file was deleted, by placing a _Delete marker_ above it.  Hit the refresh or toggle the Versions Hide/Show button to see the impact.

<div align="center">

![file versions](img/11.png)
</div>

7. Undelete the file, by deleting the _Delete marker_.  Select the Delete marker, Actions -> Delete.

Versioning comes in handy if you accidentally delete an object.  For more robust data protection, it is often combined with [MFA delete](https://docs.aws.amazon.com/AmazonS3/latest/dev/UsingMFADelete.html) requirements or  [replicating](https://docs.aws.amazon.com/AmazonS3/latest/dev/replication.html) the object to another bucket in a second account.

Note - Versioning can not be disabled, but it can be suspended.  

## Exercise #5- Restrict Access to a  S3 VPC Endpoint

In this exercise we will configure a S3 VPC Endpoint and a bucket policy to limit access to only requests that pass through the VPC Endpoint.  This is an easy way to limit access to only clients in your VPC.

1. In the AWS Console go to [VPC](https://console.aws.amazon.com/vpc/home?region=us-east-1#dashboard:).  
2. Click **Endpoints**.  
3. Click **Create Endpoint**.
4. Select the **S3** service name.
![](/images/vpc_endpoint_1.png)
5. We are going to setup an endpoint which can only be accessed from our VPC.  To do this, select the **SecurityWorkshop** VPC from the drop down menu.
![](/images/vpc_endpoint_2.png)
6. Do not select any route tables for now.  
![](/images/vpc_endpoint_3.png)
7. Leave Policy set to **Full Access**
![](/images/vpc_endpoint_4.png)
8. Click **Create endpoint**.
9. Click **Close**
10. Record the **Endpoint ID**.  
![](/images/vpc_endpoint_5.png)
12. From the AWS console, click  **Services**  and select  **S3.**
13. Click the bucket name. (Copied from CloudFormation Outputs previously.)
14. Click on the **Permissions** tab.  
14. Click **Bucket Policy**.  
15. Replace the existing policy with the bucket policy below.
    Copy and paste this JSON into the Bucket Policy Editor.

```json
{
    "Statement": [
        {
            "Action": "s3:*",
            "Effect": "Deny",
            "Resource": "arn:aws:s3:::BUCKET_NAME/*",
            "Condition": {
                "StringNotEquals": {
                    "aws:sourceVpce": "VPC_ENDPOINT_ID"
                }
            },
            "Principal": "*"
        }
    ]
}
```

16. Replace **BUCKET_NAME** with the bucket name and **VPC_ENDPOINT_ID** with the Endpoint ID.  Sample bucket policy below.  
![](/images/vpc_endpoint_6.png)
17. Click **Save**
18. Go to your SSH session, the request will fail since the S3 VPCE isn't associated with a route table.  
  
  ```bash
  aws s3api head-object --key app1/file1 --bucket ${bucket}
  ```
  We haven't finished configuring the VPC to use the new endpoint.  Let's do that next.

19. In the AWS Console go to [VPC](https://console.aws.amazon.com/vpc/home?region=us-east-1#dashboard:)
20. Click **Endpoints**.  
21. The VPC Endpoint should be selected.  Select **Actions**, then click **Manage Route Tables**.
22. Select the Route Table that is associated with **S3SecurityWorkshopSubnet Public Subnets**
You may need to hover over the subnets in the "Associated With" column to find the appropriate networks.

![](/images/vpc_endpoint_7.png)
23.  Click **Modify Route Tables**.  
    This will cause the hosts inside your VPC to route through the VPC gateway endpoint, inside your VPC to access S3.  The request will **not** have to travel across public Internet address space.

    This action changes the routing in your public subnets so that S3 traffic is routed to the S3 VPC endpoint, rather than out to the public Internet.
24.  Go to your SSH session, run the following command. The request should now succeed.  
  
```bash
  aws s3api head-object --key app1/file1 --bucket ${bucket}
```

25. From the AWS console, click  **Services**  and select  **S3.**
26. Click the bucket name. (Copied from CloudFormation Outputs previously.)
27. Click on the **Permissions** tab.  
28. Click **Bucket Policy**.
29. Click **Delete**, click **Delete** to confirm.

## Lab 6 - Extra Credit - Share your bucket with another AWS account

There are times, when you may want to share specific data with another AWS account.  While this might be accomplished with an access control list, it is recommended to use bucket policies. [ ACLs, an older feature of S3, are still supported but no longer recommended ].

#### Enable access to a bucket from another account

For this lab, you will need a partner, with a second AWS account.  You will create a bucket, add some content, and share that bucket with your partner.

1. Create a bucket, and add a file to the bucket.  From the CLI, type

```bash
 bucket=NEW_BUCKET_NAME_HERE
 aws s3 mb s3://$bucket
 dd if=/dev/zero of=/tmp/foo bs=1024 count=1024
 aws s3 cp /tmp/foo s3://$bucket/shared-data/foo
```

2. Verify the bucket contents

```bash
 aws s3 ls s3://$bucket --recursive
```

3. Verify that there is no policy on the new bucket
```bash
 aws s3api get-bucket-policy --bucket $bucket
```

4. Select a partner, and get their account number.

For this lab, select a partner.  Use their account number, and share only the /shared-data prefix with that partner.  You will need to know their account number.  One way to learn this is from the console.  If you click right, on the login at the top right of the console, your account number will be included in that information.  The console generates account numbers with “-“ for readability; the actual account number doesn’t include these “-“ symbols.

An alternate method is through the CLI.  Ask you partner to run the command

```bash
 aws sts get-caller-identity  | grep Account
```

Make a note of their account number, you will need it to generate the bucket policy.

5. Have your partner try to access your new AWS bucket.  It should fail, because they don't have access.

```bash
 aws s3 ls s3://daveaws-tmp123456
```


6. Navigate to your bucket in the S3 console. ( https://console.aws.amazon.com/s3/home?region=us-east-1 ).  Click on your bucketname to open the bucket you just created.  You may need to refresh the browser for the new bucket to be listed. Select the Permissions tab.

<div align="center">

![account defaults](img/12.png)
</div>


Select **Bucket Policy**

<div align="center">

![account defaults](img/13.png)
</div>

Near the bottom of the screen, select “**Policy generator**”
We need to create two elements of the policy.  We’d like the other account to be able to GetObjects and ListObjects.

_Create GetObject Element of policy_
**Type of Policy:** S3 Bucket Policy
**Principal:** The account number you are sharing with
**Actions:** 
GetObject
**Amazon Resource Name:** _( note, edit this for the bucket you created ).  **Be sure to include the “*” at the end.**_

**arn:aws:s3:::YOUR-BUCKET-NAME/\***

This ARN matches all objects in bucket “YOUR-BUCKET-NAME”.  

Click **Add Statement** to add permissions to GET objects.

Before you leave this page, we are going to add a 2nd policy, which will allow the other AWS account to list which objects are in the bucket.

_Create ListBucket Element of policy_
**Type of Policy:** S3 Bucket Policy
**Principal:** The account number you are sharing with
**Actions:** 
ListBucket
**Amazon Resource Name:** _( note, edit this for the bucket you created. )
_  
arn:aws:s3:::YOUR-BUCKET-NAME/*

The **"*"** at the end is important, this policy says allow the account to get **All** of the objects.

When you’ve entered the data for your policy, click **Add Statement**.

Click **Generate Policy** and the generator creates your bucket policy JSON.

**Copy the resulting policy JSON to a text file, or into your copy/paste buffer**.  It should look something like:

```json
{
  "Id": "Policy1579374599915",
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "Stmt1579374406593",
      "Action": [ 
        "s3:GetObject"
      ],
      "Effect": "Allow",
      "Resource": "arn:aws:s3:::YOUR-BUCKET-NAME/*",
      "Principal": {
        "AWS": [
          "1234567890AB"
        ]
      }
    },
    {
      "Sid": "Stmt1579374574931",
      "Action": [
        "s3:ListBucket"
      ],
      "Effect": "Allow",
      "Resource": "arn:aws:s3:::YOUR-BUCKET-NAME",
      "Principal": {
        "AWS": [
          "1234567890AB"
        ]
      }
    }
  ]
}
```

Return to the prior S3 tab, where you were editing the bucket policy, and paste in the new policy, then click **Save**.

6. Go to your partners account and verify that you can access the bucket.

```bash
 bucket=YOUR_BUCKET_NAME
 # List the other account's bucket
 aws s3 ls s3://$bucket --recursive
 # Pull the object (GetObject) from the other account's bucket
 aws s3 cp s3://$bucket/shared-data/foo /tmp/myfile
 ls -l /tmp/myfile
```


It is also possible to share just the contents of a single prefix with another account, using a Condition statement.  See this [blog post](https://aws.amazon.com/blogs/security/writing-iam-policies-grant-access-to-user-specific-folders-in-an-amazon-s3-bucket/) for more information on sharing just one folder.


#### Enable access to a bucket from another account

So, are we done?  Probably not.  This policy shared the bucket with a whole account.  Many times we need finer granularity than an account, we want to share with a role within an account.

If you are running as an assumed role, as is common in Enterprise customer accounts, adjust the policy you just made.  Change the principal from your partner's account number to her role.  One way to determine the role, again, is with the CLI.  Find the role of your labmate:

```bash
 aws sts get-caller-identity  | grep Arn
```

The role your looking for starts with "arn:sts:: ....".

7. Change the bucket policy to grant access via the temporary role, rather than to the whole AWS account.  Hint, the policy is same as you generated earlier, but has a role instead of an account number.  

<details><summary>Hint</summary>


```json
{
  "Id": "Policy1579374599915",
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "Stmt1579374406593",
      "Action": [ 
        "s3:GetObject"
      ],
      "Effect": "Allow",
      "Resource": "arn:aws:s3:::YOUR-BUCKET-NAME/*",
      "Principal": {
        "AWS": [
          "YOUR-ROLE-HERE"
        ]
      }
    },
    {
      "Sid": "Stmt1579374574931",
      "Action": [
        "s3:ListBucket"
      ],
      "Effect": "Allow",
      "Resource": "arn:aws:s3:::YOUR-BUCKET-NAME",
      "Principal": {
        "AWS": [
          "YOUR-ROLE-HERE"
        ]
      }
    }
  ]
}
```
</details>

8. Test that your new bucket policy still allows access. Go to your partners account and verify that you can access the bucket.

```bash
 bucket=YOUR_BUCKET_NAME
 # List the other account's bucket
 aws s3 ls s3://$bucket --recursive
 # Pull the object (GetObject) from the other account's bucket
 aws s3 cp s3://$bucket/shared-data/foo /tmp/myfile
 ls -l /tmp/myfile
```

 
#### **You have successfully completed this S3 high-level security overview workshop.**  If you are using your own account, please remember to delete the lab resources.

## Clean Up Resources

To ensure you don't continue to be billed for services in your account from this workshop follow the steps below to remove all resources created ruing the workshop.

1. Delete your S3 buckets, using the console, or run the following command.  
  
  ```bash
  aws s3 rm s3://${bucket} --recursive
  ```

2. From the AWS console, click  **Services**  and select  **Config.**  
2. Click **Rules**.  
3. Click **s3_bucket_public_write_prohibited**.
4. Click **Edit**.
5. Click **Delete Rule**.(Must scroll down)
6. Click **Delete**
7. In the AWS Console go to **VPC**.  
8. Click **Endpoints**.
9. Select the Endpoint created earlier, select **Actions**, click **Delete Endpoint**.  
10. Click **Yes,Delete**.
11. From the AWS console, click  **Services**  and select  **CloudFormation.**  
12. Select **S3SecurityWorkshop**.  
13. Click **Delete**.  
14. Click **Delete stack**.  
15. It will take a few minutes to delete everything.  Refresh the page to see an updated status.  **S3SecurityWorkshop** will be removed from the list if everything has been deleted correctly.
