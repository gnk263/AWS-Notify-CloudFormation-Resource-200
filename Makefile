BUCKET_NAME := gnk263-sam-bucket
STACK_NAME := Notify-CloudFormation-Resource-Stack
NOTIFY_SLACK_URL_KEY := /Slack/INCOMING_WEBHOOK_URL/CloudFormationResource
RESOURCE_THRESHOLD_KEY := /Slack/CloudFormation/Resource/Threshold

build:
	sam build

deploy:
	sam package \
		--output-template-file packaged.yaml \
		--s3-bucket $(BUCKET_NAME)

	sam deploy \
		--template-file packaged.yaml \
		--stack-name $(STACK_NAME) \
		--capabilities CAPABILITY_NAMED_IAM \
		--no-fail-on-empty-changeset \
		--parameter-overrides \
			NotifySlackUrl=$(NOTIFY_SLACK_URL_KEY) \
			ResourceThreshold=$(RESOURCE_THRESHOLD_KEY)
