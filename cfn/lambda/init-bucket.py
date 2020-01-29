from __future__ import print_function
from crhelper import CfnResource
import logging
import boto3
from botocore.exceptions import ClientError
from os import environ

if not 'AWS_DEFAULT_REGION' in environ:
    environ['AWS_DEFAULT_REGION'] = 'us-east-2'
bucketregion=environ['AWS_DEFAULT_REGION']

logger = logging.getLogger(__name__)
# Initialise the helper, all inputs are optional, this example shows the defaults
helper = CfnResource(json_logging=False, log_level='DEBUG', boto_level='CRITICAL')

try:
    ## Init code goes here
    s3 = boto3.client('s3')
except Exception as e:
    helper.init_failure(e)

@helper.create
def create(event, context):
    logger.info("Got Create")
    print(event)
    # Optionally return an ID that will be used for the resource PhysicalResourceId, 
    # if None is returned an ID will be generated. If a poll_create function is defined 
    # return value is placed into the poll event as event['CrHelperData']['PhysicalResourceId']
    #
    # To add response data update the helper.Data dict
    # If poll is enabled data is placed into poll event as event['CrHelperData']
    bucket = event["ResourceProperties"]["Parameters"][0]["BucketName"]
    debug = False
    if debug:
        logger.info("bucket: {}".format(bucket))
    else:
        if createbucketifnotexists(bucket,bucketregion) and fillbucket(bucket):
            helper.Data.update({"Status": "Success"})
        else:
            helper.Data.update({"Status": "Failed"})
        print("helper Data:",helper.Data)
    return


@helper.update
def update(event, context):
    logger.info("Got Update")
    # If the update resulted in a new resource being created, return an id for the new resource. CloudFormation will send
    # a delete event with the old id when stack update completes
    bucket = event["ResourceProperties"]["Parameters"][0]["BucketName"]
    # We have no way to know whether the bucketname changed.
    # If we get an update to the stack, re-create the bucket.
    # Note this could/will cause old bucket to hang around.
    logger.info("creating bucket {}".format(bucket))
    if createbucketifnotexists(bucket,bucketregion) and fillbucket(bucket):
        helper.Data.update({"Status": "Success"})
    else:
        helper.Data.update({"Status": "Failed"})
    print("helper Data:",helper.Data)
    return


@helper.delete
def delete(event, context):
    logger.info("Got Delete")
    # Delete never returns anything. Should not fail if the underlying resources are already deleted. Desired state.
    bucket = event["ResourceProperties"]["Parameters"][0]["BucketName"]
    logger.info("deleting bucket: {}".format(bucket))
    if deletebucketandcontent(bucket):
        helper.Data.update({"Status": "Success"})
    else:
        helper.Data.update({"Status": "Failed"})
    print("helper Data:",helper.Data)
    return


# @helper.poll_create
# def poll_create(event, context):
#     logger.info("Got create poll")
#     # Return a resource id or True to indicate that creation is complete. if True is returned an id will be generated
#     return True

def createbucketifnotexists(bucketname,region):
    try:
        response = s3.head_bucket(Bucket=bucketname)
    except ClientError as e:
        if e.response['Error']['Message'] == "Not Found":
            try:
                response = s3.create_bucket(Bucket=bucketname,CreateBucketConfiguration={'LocationConstraint':region})
            except Exception as e:
                print('unable to create bucket {} - error {}'.format(bucketname,e))
                return False
        else:
            print('unexpected error: ',e)
            return False
    return True

def fillbucket(bucketname):
    ''' place some content in the bucket so our immersion day students have something to work with
    '''

    contentbuffer = 10240*"0123456789ABCDEF"
    for prefix in ['app1','app2']:
        for count in range(1,5):
            key = prefix + "/file" + str(count)
            try:
                response = s3.put_object(
                    Body=contentbuffer,
                    Bucket=bucketname,
                    Key=key,
                    ServerSideEncryption='AES256'
                )
            except Exception as e:
                print('failed to upload object to bucket {} - {}'.format(bucketname,e))
                return False
    return True

def deletebucketandcontent(bucketname):
    '''
        Delete the contents of the bucket, then the bucket
        note - doesn't handle pagination, so will fail for large number of objects
    '''
    try:
        response = s3.get_bucket_versioning(Bucket=bucketname)
        versioning = False
        if 'Status' in response and response.Status == 'Enabled':
            versioning = True
        if not versioning:
            paginator = s3.get_paginator('list_objects_v2')
            pages = paginator.paginate(Bucket=bucketname)
            delete_us = dict(Objects=[])
            for item in pages.search('Contents'):
                delete_us['Objects'].append(dict(Key=item['Key']))
                # flush once aws limit reached
                if len(delete_us['Objects']) >= 1000:
                    s3.delete_objects(Bucket=bucketname, Delete=delete_us)
                    delete_us = dict(Objects=[])
            # flush rest
            if len(delete_us['Objects']):
                s3.delete_objects(Bucket=bucketname, Delete=delete_us)
        else:
            print('deleting versioned buckets not implemented')
            pass
            return False
        s3.delete_bucket(Bucket=bucketname)
    except Exception as e:
        print('could not delete bucket {} - {}'.format(bucketname,e))
        return False
    return True

def handler(event, context):
    helper(event, context)

if __name__ == "__main__":

    bucketname = 'daveaws-tmp-01272020'
    createbucketifnotexists(bucketname,bucketregion)
    fillbucket(bucketname)
    deletebucketandcontent(bucketname)
