stack=s3
template=main.yml
test:
	# cfn-lint ${template} --ignore-checks W3010,W1001,W8001
	cfn-lint ${template}

package: lambda
	aws s3 cp s3.yml s3://daveaws/cloudformation/s3/s3.yml
	aws s3 cp vpc.yml s3://daveaws/cloudformation/s3/vpc.yml
	aws cloudformation package \
	  --template-file ${template} \
	  --s3-bucket daveaws \
	  --s3-prefix cloudformation/s3 \
	  --output-template-file packaged-${stack}

deploy: package
	aws cloudformation deploy \
	  --template-file packaged-${stack} \
	  --stack-name ${stack} \
  	  --capabilities CAPABILITY_NAMED_IAM

delete:
	aws cloudformation delete-stack --stack-name ${stack}
	
change: lambda
	aws cloudformation create-change-set --stack-name ${stack} \
        --change-set-name my-changes \
	--template-body file://${template} \
	--parameters file://${parameters} \
	--capabilities CAPABILITY_NAMED_IAM

outputs:
	aws cloudformation describe-stacks --stack-name ${stack} --query Stacks[].Outputs[] 
	
resources:
	aws cloudformation describe-stack-resources --stack-name ${stack} --query StackResources[].[LogicalResourceId,ResourceStatus,Timestamp] --output table

# crstack  for 2nd stack that was used to testing the custom resource
crstack=testcustom7

create-custom:
	aws cloudformation create-stack \
	  --stack-name ${crstack} \
	  --template-body file://test-custom.yml \
	  --capabilities CAPABILITY_IAM

update-custom:
	aws cloudformation update-stack --stack-name ${crstack} --template-body fileL//test-custom.yml --capabilities CAPABILITY_IAM
test-custom:
	cfn-lint test-custom.yml 

delete-custom:
	aws cloudformation delete-stack --stack-name ${crstack}

lambda:
	cd lambda && make zip && make push