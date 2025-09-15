#!/usr/bin/env python3
import boto3
import sys

def delete_multiple_datasets(account_id, dataset_ids, region='us-east-1'):
    """Delete multiple QuickSight datasets"""
    quicksight = boto3.client('quicksight', region_name=region)
    
    for dataset_id in dataset_ids:
        try:
            quicksight.delete_data_set(
                AwsAccountId=account_id,
                DataSetId=dataset_id
            )
            print(f"✅ Deleted: {dataset_id}")
        except Exception as e:
            print(f"❌ Failed to delete {dataset_id}: {str(e)}")

if __name__ == "__main__":
    # Usage: python delete_datasets.py account_id dataset1 dataset2 dataset3
    if len(sys.argv) < 3:
        print("Usage: python delete_datasets.py <account_id> <dataset_id1> [dataset_id2] ...")
        sys.exit(1)
    
    account_id = sys.argv[1]
    dataset_ids = sys.argv[2:]
    
    delete_multiple_datasets(account_id, dataset_ids)
