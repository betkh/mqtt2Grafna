#!/usr/bin/env python3
"""
CSV Temperature Data Query Tool
Query temperature data from CSV file with various options
"""

import csv
import pandas as pd
from datetime import datetime, timedelta
import argparse

CSV_FILENAME = "temperature_data.csv"


def load_csv_data():
    """Load data from CSV file"""
    try:
        df = pd.read_csv(CSV_FILENAME)
        # Convert datetime string to datetime object
        df['datetime'] = pd.to_datetime(df['datetime'])
        return df
    except FileNotFoundError:
        print(f"Error: CSV file '{CSV_FILENAME}' not found!")
        return None
    except Exception as e:
        print(f"Error loading CSV file: {e}")
        return None


def show_recent_data(df, limit=10):
    """Show recent temperature data"""
    if df is None or df.empty:
        print("No data available")
        return

    print(f"\n=== Recent Temperature Data (Last {limit} records) ===")
    recent = df.tail(limit)
    for _, row in recent.iterrows():
        print(f"Time: {row['datetime']} | Temperature: {row['temperature']}°C")


def show_statistics(df):
    """Show temperature statistics"""
    if df is None or df.empty:
        print("No data available")
        return

    print("\n=== Temperature Statistics ===")
    print(f"Total records: {len(df)}")
    print(f"Average temperature: {df['temperature'].mean():.2f}°C")
    print(f"Minimum temperature: {df['temperature'].min():.2f}°C")
    print(f"Maximum temperature: {df['temperature'].max():.2f}°C")
    print(
        f"Temperature range: {df['temperature'].max() - df['temperature'].min():.2f}°C")


def filter_by_temperature(df, min_temp=None, max_temp=None):
    """Filter data by temperature range"""
    if df is None or df.empty:
        print("No data available")
        return

    filtered = df.copy()

    if min_temp is not None:
        filtered = filtered[filtered['temperature'] >= min_temp]
        print(f"Filtered for temperature >= {min_temp}°C")

    if max_temp is not None:
        filtered = filtered[filtered['temperature'] <= max_temp]
        print(f"Filtered for temperature <= {max_temp}°C")

    if filtered.empty:
        print("No data matches the temperature filter")
        return

    print(f"\n=== Filtered Data ({len(filtered)} records) ===")
    for _, row in filtered.iterrows():
        print(f"Time: {row['datetime']} | Temperature: {row['temperature']}°C")


def filter_by_time(df, hours=None, start_time=None, end_time=None):
    """Filter data by time range"""
    if df is None or df.empty:
        print("No data available")
        return

    filtered = df.copy()

    if hours is not None:
        cutoff_time = datetime.now() - timedelta(hours=hours)
        filtered = filtered[filtered['datetime'] >= cutoff_time]
        print(f"Filtered for last {hours} hours")

    if start_time is not None:
        start_dt = pd.to_datetime(start_time)
        filtered = filtered[filtered['datetime'] >= start_dt]
        print(f"Filtered from {start_time}")

    if end_time is not None:
        end_dt = pd.to_datetime(end_time)
        filtered = filtered[filtered['datetime'] <= end_dt]
        print(f"Filtered until {end_time}")

    if filtered.empty:
        print("No data matches the time filter")
        return

    print(f"\n=== Filtered Data ({len(filtered)} records) ===")
    for _, row in filtered.iterrows():
        print(f"Time: {row['datetime']} | Temperature: {row['temperature']}°C")


def export_to_new_csv(df, output_filename, min_temp=None, max_temp=None, hours=None):
    """Export filtered data to new CSV file"""
    if df is None or df.empty:
        print("No data available")
        return

    filtered = df.copy()

    if min_temp is not None:
        filtered = filtered[filtered['temperature'] >= min_temp]

    if max_temp is not None:
        filtered = filtered[filtered['temperature'] <= max_temp]

    if hours is not None:
        cutoff_time = datetime.now() - timedelta(hours=hours)
        filtered = filtered[filtered['datetime'] >= cutoff_time]

    if filtered.empty:
        print("No data matches the filter criteria")
        return

    filtered.to_csv(output_filename, index=False)
    print(f"Exported {len(filtered)} records to {output_filename}")


def main():
    parser = argparse.ArgumentParser(
        description='Query temperature data from CSV file')
    parser.add_argument('--recent', type=int, default=10,
                        help='Show recent N records (default: 10)')
    parser.add_argument('--stats', action='store_true', help='Show statistics')
    parser.add_argument('--min-temp', type=float,
                        help='Filter by minimum temperature')
    parser.add_argument('--max-temp', type=float,
                        help='Filter by maximum temperature')
    parser.add_argument('--hours', type=int, help='Filter by last N hours')
    parser.add_argument(
        '--start-time', help='Filter from start time (YYYY-MM-DD HH:MM:SS)')
    parser.add_argument(
        '--end-time', help='Filter until end time (YYYY-MM-DD HH:MM:SS)')
    parser.add_argument('--export', help='Export filtered data to CSV file')

    args = parser.parse_args()

    # Load data
    df = load_csv_data()
    if df is None:
        return

    print(f"Loaded {len(df)} records from {CSV_FILENAME}")

    # Show recent data
    if args.recent > 0:
        show_recent_data(df, args.recent)

    # Show statistics
    if args.stats:
        show_statistics(df)

    # Filter by temperature
    if args.min_temp is not None or args.max_temp is not None:
        filter_by_temperature(df, args.min_temp, args.max_temp)

    # Filter by time
    if args.hours is not None or args.start_time is not None or args.end_time is not None:
        filter_by_time(df, args.hours, args.start_time, args.end_time)

    # Export data
    if args.export:
        export_to_new_csv(df, args.export, args.min_temp,
                          args.max_temp, args.hours)


if __name__ == "__main__":
    main()
