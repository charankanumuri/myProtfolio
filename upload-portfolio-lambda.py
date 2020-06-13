import json
import boto3
import io
import zipfile
import mimetypes

def lambda_handler(event, context):
    s3 = boto3.resource('s3')
    sns = boto3.resource('sns')

    topic = sns.Topic('arn:aws:sns:ap-south-1:705123275076:DeployPortfolioTopic')

    try:
        portfolio_bucket = s3.Bucket('portfolio.4myiot.net')
        build_bucket = s3.Bucket('portfoliobuild.4myiot.net')

        portfolio_zip = io.BytesIO()
        build_bucket.download_fileobj('portfoliobuild.zip', portfolio_zip)

        with zipfile.ZipFile(portfolio_zip) as myzip:
            for nm in myzip.namelist():
                obj = myzip.open(nm)
                portfolio_bucket.upload_fileobj(obj, nm,ExtraArgs={'ContentType': mimetypes.guess_type(nm)[0]})
                portfolio_bucket.Object(nm).Acl().put(ACL='public-read')
        print("Job Done!!!")
        topic.publish(Subject="Portfolio Deployed!!!", Message="Your Portfolio deployed successfully.")
    except:
        topic.publish(Subject="Portfolio Deployment Failed...", Message="Your Portfolio deployment was not successful.")
        raise
    return {'body': json.dumps('Hello from Lambda!')}
