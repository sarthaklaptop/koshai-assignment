"""
Financial Reconciliation System - Main Entry Point

This script demonstrates how to use the Statement, Settlement, and Reconciliation processors.
"""

import argparse
from pathlib import Path
from processors import (
    process_statement, 
    process_settlement,
    reconcile_data,
    generate_reconciliation_report
)


def main():
    parser = argparse.ArgumentParser(
        description='Financial Reconciliation System - Data Processor'
    )
    parser.add_argument(
        '--statement', '-s',
        type=str,
        help='Path to the Statement file (CSV or Excel)'
    )
    parser.add_argument(
        '--settlement', '-t',
        type=str,
        help='Path to the Settlement file (CSV or Excel)'
    )
    parser.add_argument(
        '--output-dir', '-o',
        type=str,
        default='./output',
        help='Directory to save processed files (default: ./output)'
    )
    parser.add_argument(
        '--reconcile', '-r',
        action='store_true',
        help='Run reconciliation if both files are provided'
    )
    
    args = parser.parse_args()
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    statement_df = None
    settlement_df = None
    
    # Process Statement file
    if args.statement:
        print(f"\n{'='*60}")
        print("Processing Statement File...")
        print(f"{'='*60}")
        
        try:
            statement_df = process_statement(args.statement)
            
            print(f"✓ Loaded {len(statement_df)} records")
            print(f"\nPartner Pin Extraction:")
            print(f"  - Found: {statement_df['Partner_Pin'].notna().sum()}")
            print(f"  - Missing: {statement_df['Partner_Pin'].isna().sum()}")
            
            print(f"\nReconciliation Tags:")
            for tag, count in statement_df['Reconcile_Tag'].value_counts().items():
                print(f"  - {tag}: {count}")
            
            # Save processed file
            output_path = output_dir / 'processed_statement.csv'
            statement_df.to_csv(output_path, index=False)
            print(f"\n✓ Saved to: {output_path}")
            
        except Exception as e:
            print(f"✗ Error processing statement: {e}")
            statement_df = None
    
    # Process Settlement file
    if args.settlement:
        print(f"\n{'='*60}")
        print("Processing Settlement File...")
        print(f"{'='*60}")
        
        try:
            settlement_df = process_settlement(args.settlement)
            
            print(f"✓ Loaded {len(settlement_df)} records")
            
            print(f"\nEstimate Amount (USD) Stats:")
            print(f"  - Min: ${settlement_df['estimate_amount_usd'].min():.2f}")
            print(f"  - Max: ${settlement_df['estimate_amount_usd'].max():.2f}")
            print(f"  - Mean: ${settlement_df['estimate_amount_usd'].mean():.2f}")
            
            print(f"\nReconciliation Tags:")
            for tag, count in settlement_df['Reconcile_Tag'].value_counts().items():
                print(f"  - {tag}: {count}")
            
            # Save processed file
            output_path = output_dir / 'processed_settlement.csv'
            settlement_df.to_csv(output_path, index=False)
            print(f"\n✓ Saved to: {output_path}")
            
        except Exception as e:
            print(f"✗ Error processing settlement: {e}")
            settlement_df = None
    
    # Run Reconciliation if both files are provided
    if args.reconcile and statement_df is not None and settlement_df is not None:
        print(f"\n{'='*60}")
        print("Running Reconciliation...")
        print(f"{'='*60}")
        
        try:
            results = reconcile_data(statement_df, settlement_df)
            
            # Print report
            print(generate_reconciliation_report(results))
            
            # Save category files
            results['category_5'].to_csv(output_dir / 'category_5_matched.csv', index=False)
            results['category_6'].to_csv(output_dir / 'category_6_settlement_only.csv', index=False)
            results['category_7'].to_csv(output_dir / 'category_7_statement_only.csv', index=False)
            
            print(f"\n✓ Saved category files to: {output_dir}")
            print(f"  - category_5_matched.csv")
            print(f"  - category_6_settlement_only.csv")
            print(f"  - category_7_statement_only.csv")
            
        except Exception as e:
            print(f"✗ Error during reconciliation: {e}")
            import traceback
            traceback.print_exc()
    
    elif args.reconcile and (statement_df is None or settlement_df is None):
        print("\n⚠ Reconciliation requires both Statement and Settlement files.")
        print("  Use: python main.py -s statement.csv -t settlement.csv -r")
    
    if not args.statement and not args.settlement:
        print("No files specified. Use --help for usage information.")
        print("\nExample usage:")
        print("  python main.py --statement statement.csv")
        print("  python main.py --settlement settlement.xlsx")
        print("  python main.py -s statement.csv -t settlement.xlsx -o ./results")
        print("  python main.py -s statement.csv -t settlement.xlsx -r  # With reconciliation")


if __name__ == "__main__":
    main()
