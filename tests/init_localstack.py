import boto3
import time

def create_localstack_resources():
    """Initialize AWS resources in LocalStack."""
    # LocalStack endpoint
    endpoint_url = "http://localhost:4566"
    
    # Create Kinesis client
    kinesis = boto3.client(
        'kinesis',
        endpoint_url=endpoint_url,
        region_name='us-east-1',
        aws_access_key_id='test',
        aws_secret_access_key='test'
    )
    
    # Create S3 client
    s3 = boto3.client(
        's3',
        endpoint_url=endpoint_url,
        region_name='us-east-1',
        aws_access_key_id='test',
        aws_secret_access_key='test'
    )
    
    print("Creating Kinesis streams...")
    streams = [
        "game-events-stream",
        "session-metrics",
        "revenue-metrics"
    ]
    
    for stream_name in streams:
        try:
            kinesis.create_stream(
                StreamName=stream_name,
                ShardCount=1
            )
            print(f"Created Kinesis stream: {stream_name}")
        except kinesis.exceptions.ResourceInUseException:
            print(f"Stream {stream_name} already exists")
    
    print("\nCreating S3 buckets...")
    buckets = [
        "game-analytics-raw-data-dev",
        "game-analytics-processed-data-dev"
    ]
    
    for bucket_name in buckets:
        try:
            s3.create_bucket(Bucket=bucket_name)
            print(f"Created S3 bucket: {bucket_name}")
        except s3.exceptions.BucketAlreadyExists:
            print(f"Bucket {bucket_name} already exists")
    
    print("\nWaiting for streams to become active...")
    time.sleep(3)
    
    # Verify streams are active
    for stream_name in streams:
        try:
            response = kinesis.describe_stream(StreamName=stream_name)
            status = response['StreamDescription']['StreamStatus']
            print(f"Stream {stream_name} status: {status}")
        except Exception as e:
            print(f"Error checking stream {stream_name}: {e}")
    
    print("\nLocalStack resources initialized successfully!")

if __name__ == "__main__":
    create_localstack_resources() 