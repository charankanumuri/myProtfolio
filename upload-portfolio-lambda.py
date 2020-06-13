import json
import boto3
import io
import zipfile
import mimetypes

def lambda_handler(event, context):
    s3 = boto3.resource('s3')
    sns = boto3.resource('sns')

    topic = sns.Topic('arn:aws:sns:ap-south-1:705123275076:DeployPortfolioTopic')

    location = {
        "bucketName": 'portfoliobuild.4myiot.net',
        "objectKey": 'portfoliobuild.zip'
    }
    try:
        job = event.get("CodePipeline.job")

        if job:
            for artifact in job["data"]["inputArtifacts"]:
                if artifact["name"] == "MyAppBuild":
                    location = artifact["location"]["s3Location"]

        print("Building Portfolio from "+ str(location))

        portfolio_bucket = s3.Bucket('portfolio.4myiot.net')
        build_bucket = s3.Bucket(location["bucketName"])

        portfolio_zip = io.BytesIO()
        build_bucket.download_fileobj(location["objectKey"], portfolio_zip)

        with zipfile.ZipFile(portfolio_zip) as myzip:
            for nm in myzip.namelist():
                obj = myzip.open(nm)
                portfolio_bucket.upload_fileobj(obj, nm,ExtraArgs={'ContentType': mimetypes.guess_type(nm)[0]})
                portfolio_bucket.Object(nm).Acl().put(ACL='public-read')
        print("Job Done!!!")
        topic.publish(Subject="Portfolio Deployed!!!", Message="Your Portfolio deployed successfully.")
        if job:
            client = boto3.client('codepipeline')
            client.put_job_success_result(jobId=job["id"])
    except:
        topic.publish(Subject="Portfolio Deployment Failed...", Message="Your Portfolio deployment was not successful.")
        raise
    return {'body': json.dumps('Hello from Lambda!')}
