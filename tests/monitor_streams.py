import boto3
import json
import time
from datetime import datetime
from threading import Thread

def get_kinesis_client():
    """Create a Kinesis client for LocalStack."""
    return boto3.client(
        'kinesis',
        endpoint_url='http://localhost:4566',
        region_name='us-east-1',
        aws_access_key_id='test',
        aws_secret_access_key='test'
    )

def monitor_stream(stream_name):
    """Monitor a Kinesis stream and print received records."""
    kinesis = get_kinesis_client()
    
    try:
        # Get shard iterator
        response = kinesis.describe_stream(StreamName=stream_name)
        shard_id = response['StreamDescription']['Shards'][0]['ShardId']
        
        iterator_response = kinesis.get_shard_iterator(
            StreamName=stream_name,
            ShardId=shard_id,
            ShardIteratorType='LATEST'
        )
        shard_iterator = iterator_response['ShardIterator']
        
        print(f"\nStarted monitoring {stream_name}")
        
        while True:
            response = kinesis.get_records(
                ShardIterator=shard_iterator,
                Limit=100
            )
            
            for record in response['Records']:
                try:
                    data = json.loads(record['Data'].decode())
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(f"\n[{timestamp}] {stream_name} received:")
                    print(json.dumps(data, indent=2))
                except Exception as e:
                    print(f"Error processing record: {e}")
            
            shard_iterator = response['NextShardIterator']
            time.sleep(1)  # Avoid hitting rate limits
            
    except Exception as e:
        print(f"Error monitoring {stream_name}: {e}")

def main():
    """Monitor all Kinesis streams."""
    streams = [
        "game-events-stream",
        "session-metrics",
        "revenue-metrics"
    ]
    
    # Create threads for each stream
    threads = []
    for stream_name in streams:
        thread = Thread(target=monitor_stream, args=(stream_name,))
        thread.daemon = True
        threads.append(thread)
    
    # Start all threads
    for thread in threads:
        thread.start()
    
    print("Monitoring all streams. Press Ctrl+C to stop...")
    
    try:
        # Keep main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping stream monitoring...")

if __name__ == "__main__":
    main() 