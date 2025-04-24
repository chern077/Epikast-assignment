import json
import psycopg2
import os

DB_HOST = os.environ["DB_HOST"]
DB_NAME = os.environ["DB_NAME"]
DB_USER = os.environ["DB_USER"]
DB_PASSWORD = os.environ["DB_PASSWORD"]
DB_PORT = os.environ.get("DB_PORT", "5432")

def lambda_handler(event, context):
    try:
        granularity = event.get("granularity", "daily").lower()

        group_by = {
            "hourly": "DATE_TRUNC('hour', log_time)",
            "daily": "DATE_TRUNC('day', log_time)",
            "weekly": "DATE_TRUNC('week', log_time)"
        }.get(granularity)

        if not group_by:
            return {"statusCode": 400, "body": json.dumps({"error": "Invalid granularity"})}

        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT
        )

        cursor = conn.cursor()
        cursor.execute(f"""
            SELECT {group_by} AS period, COUNT(*) 
            FROM logs 
            GROUP BY period 
            ORDER BY period;
        """)
        results = cursor.fetchall()
        cursor.close()
        conn.close()

        return {
            "statusCode": 200,
            "body": json.dumps({str(row[0]): row[1] for row in results})
        }

    except Exception as e:
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
