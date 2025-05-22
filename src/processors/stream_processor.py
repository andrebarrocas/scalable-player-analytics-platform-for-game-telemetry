from typing import Dict, Any
import json
import datetime

from pyflink.table import (
    StreamTableEnvironment,
    EnvironmentSettings,
    DataTypes
)
from pyflink.table.udf import udf
from pyflink.common import Row


def create_table_environment():
    """Create and configure the Flink Table Environment."""
    settings = EnvironmentSettings.new_instance() \
        .in_streaming_mode() \
        .build()
    
    return StreamTableEnvironment.create(environment_settings=settings)


def create_source_table(t_env: StreamTableEnvironment):
    """Create the source table reading from Kinesis."""
    source_ddl = """
        CREATE TABLE game_events (
            event_id STRING,
            timestamp TIMESTAMP(3),
            game_id STRING,
            player_id STRING,
            session_id STRING,
            event_type STRING,
            version STRING,
            payload STRING,
            WATERMARK FOR timestamp AS timestamp - INTERVAL '5' SECOND
        ) WITH (
            'connector' = 'kinesis',
            'stream' = 'game-events-stream',
            'aws.region' = 'us-east-1',
            'scan.stream.initpos' = 'LATEST',
            'format' = 'json'
        )
    """
    t_env.execute_sql(source_ddl)


def create_sink_tables(t_env: StreamTableEnvironment):
    """Create sink tables for different analytics."""
    # Session metrics sink
    session_metrics_ddl = """
        CREATE TABLE session_metrics (
            window_start TIMESTAMP(3),
            window_end TIMESTAMP(3),
            game_id STRING,
            total_sessions BIGINT,
            avg_duration DOUBLE,
            PRIMARY KEY (window_start, window_end, game_id) NOT ENFORCED
        ) WITH (
            'connector' = 'upsert-kinesis',
            'stream' = 'session-metrics',
            'aws.region' = 'us-east-1',
            'format' = 'json'
        )
    """
    
    # Revenue metrics sink
    revenue_metrics_ddl = """
        CREATE TABLE revenue_metrics (
            window_start TIMESTAMP(3),
            window_end TIMESTAMP(3),
            game_id STRING,
            total_revenue DOUBLE,
            transaction_count BIGINT,
            avg_transaction DOUBLE,
            PRIMARY KEY (window_start, window_end, game_id) NOT ENFORCED
        ) WITH (
            'connector' = 'upsert-kinesis',
            'stream' = 'revenue-metrics',
            'aws.region' = 'us-east-1',
            'format' = 'json'
        )
    """
    
    t_env.execute_sql(session_metrics_ddl)
    t_env.execute_sql(revenue_metrics_ddl)


@udf(result_type=DataTypes.ROW([
    DataTypes.FIELD("duration", DataTypes.INT()),
    DataTypes.FIELD("score", DataTypes.INT()),
    DataTypes.FIELD("level", DataTypes.INT())
]))
def extract_game_end_data(payload: str) -> Row:
    """Extract relevant fields from game end events."""
    data = json.loads(payload)
    return Row(
        duration=data.get('duration', 0),
        score=data.get('score', 0),
        level=data.get('level_reached', 0)
    )


@udf(result_type=DataTypes.ROW([
    DataTypes.FIELD("amount", DataTypes.DOUBLE()),
    DataTypes.FIELD("currency_code", DataTypes.STRING())
]))
def extract_purchase_data(payload: str) -> Row:
    """Extract relevant fields from purchase events."""
    data = json.loads(payload)
    return Row(
        amount=float(data.get('amount', 0.0)),
        currency_code=data.get('currency_code', 'USD')
    )


def create_session_analytics(t_env: StreamTableEnvironment):
    """Create session analytics processing logic."""
    # Register UDFs
    t_env.create_temporary_function("extract_game_end_data", extract_game_end_data)
    
    # Session analytics query
    session_query = """
        INSERT INTO session_metrics
        SELECT
            TUMBLE_START(timestamp, INTERVAL '5' MINUTE) as window_start,
            TUMBLE_END(timestamp, INTERVAL '5' MINUTE) as window_end,
            game_id,
            COUNT(DISTINCT session_id) as total_sessions,
            AVG(extract_game_end_data(payload).duration) as avg_duration
        FROM game_events
        WHERE event_type = 'game_end'
        GROUP BY
            TUMBLE(timestamp, INTERVAL '5' MINUTE),
            game_id
    """
    
    t_env.execute_sql(session_query)


def create_revenue_analytics(t_env: StreamTableEnvironment):
    """Create revenue analytics processing logic."""
    # Register UDFs
    t_env.create_temporary_function("extract_purchase_data", extract_purchase_data)
    
    # Revenue analytics query
    revenue_query = """
        INSERT INTO revenue_metrics
        SELECT
            TUMBLE_START(timestamp, INTERVAL '5' MINUTE) as window_start,
            TUMBLE_END(timestamp, INTERVAL '5' MINUTE) as window_end,
            game_id,
            SUM(extract_purchase_data(payload).amount) as total_revenue,
            COUNT(*) as transaction_count,
            AVG(extract_purchase_data(payload).amount) as avg_transaction
        FROM game_events
        WHERE event_type = 'purchase'
        GROUP BY
            TUMBLE(timestamp, INTERVAL '5' MINUTE),
            game_id
    """
    
    t_env.execute_sql(revenue_query)


def main():
    """Main entry point for the stream processor."""
    # Create Table Environment
    t_env = create_table_environment()
    
    # Create source and sink tables
    create_source_table(t_env)
    create_sink_tables(t_env)
    
    # Create analytics
    create_session_analytics(t_env)
    create_revenue_analytics(t_env)
    
    # Execute the job
    t_env.execute("Game Analytics Processor")


if __name__ == "__main__":
    main() 