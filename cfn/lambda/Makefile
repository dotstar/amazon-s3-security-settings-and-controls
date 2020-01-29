zip=initbucket.zip
all: zip push 

zip:
	cd package && zip -r9 ../../${zip} .
	zip -g ../${zip} init-bucket.py
push:
	aws s3 cp ../${zip} s3://daveaws/lambda/${zip}
create-lambda:
	aws lambda create-function \
		--function-name "init-bucket" \
		--description "used by CloudFormation to create a bucket with simple content" \
		--handler "init-bucket.handler" \
		--timeout 120 \
		--memory-size 512 \
		--zip-file fileb://../${zip} \
		--runtime python3.7 \
		--role "arn:aws:iam::428505257828:role/cdd-init-bucket-lambda-role"

delete:
	aws lambda delete-function --function-name init-bucket
requirements:
	rm -rf package
	pip install -r requirements.txt --target ./package

stackname=lb4
stack:
	aws cloudformation create-stack --stack-name ${stackname} --template-body file://test-custom.yml --capabilities CAPABILITY_IAM
delete-stack:
	aws cloudformation delete-stack --stack-name ${stackname}
update-stack:
	aws cloudformation update-stack --stack-name ${stackname} --template-body file://test-custom.yml
