"""
Smart Banking Dataset Generation Script
Generates synthetic banking customer data for EDA and model training
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path

np.random.seed(42)

def generate_banking_dataset(n_samples: int = 5000) -> pd.DataFrame:
    """Generate synthetic banking customer dataset."""
    
    # Numerical features
    age = np.random.normal(45, 15, n_samples).clip(18, 90).astype(int)
    monthly_income = np.random.exponential(5000, n_samples).clip(1000, 50000).astype(float)
    account_balance = (monthly_income * np.random.uniform(2, 24, n_samples)).astype(float)
    savings_balance = (account_balance * np.random.uniform(0, 0.8, n_samples)).astype(float)
    tenure_months = np.random.exponential(36, n_samples).clip(1, 360).astype(int)
    num_products = np.random.poisson(2, n_samples).clip(1, 8)
    credit_score = np.random.normal(700, 100, n_samples).clip(300, 850).astype(int)
    total_debt = (monthly_income * np.random.exponential(0.3, n_samples)).astype(float)
    credit_limit = (monthly_income * np.random.uniform(3, 15, n_samples)).astype(float)
    credit_utilization = (np.random.beta(2, 3, n_samples) * 100).astype(float)
    num_loans = np.random.poisson(1, n_samples)
    num_late_payments = np.random.poisson(0.5, n_samples)
    num_defaults = np.random.poisson(0.1, n_samples)
    monthly_transactions = np.random.poisson(8, n_samples)
    avg_transaction_amount = np.random.exponential(200, n_samples).astype(float)
    num_atm_withdrawals = np.random.poisson(4, n_samples)
    international_transactions = np.random.binomial(1, 0.3, n_samples)
    has_investment_account = np.random.binomial(1, 0.35, n_samples)
    investment_balance = (has_investment_account * np.random.exponential(20000, n_samples)).astype(float)
    has_insurance = np.random.binomial(1, 0.6, n_samples)
    has_mortgage = np.random.binomial(1, 0.4, n_samples)
    mortgage_amount = (has_mortgage * np.random.exponential(150000, n_samples)).astype(float)
    days_since_last_activity = np.random.exponential(10, n_samples).clip(0, 365).astype(int)
    complaint_count = np.random.poisson(0.3, n_samples)
    overdraft_count = np.random.poisson(0.2, n_samples)
    suspicious_activity_flag = np.random.binomial(1, 0.05, n_samples)
    
    # Categorical features
    gender = np.random.choice(["Male", "Female"], n_samples)
    marital_status = np.random.choice(["Single", "Married", "Divorced", "Widowed"], n_samples)
    education_level = np.random.choice(["High School", "Bachelor", "Master", "PhD"], n_samples)
    region = np.random.choice(["North", "South", "East", "West", "Central"], n_samples)
    employment_status = np.random.choice(["Employed", "Self-employed", "Retired", "Unemployed"], n_samples)
    online_banking_usage = np.random.choice(["Low", "Medium", "High"], n_samples)
    
    # Create DataFrame
    df = pd.DataFrame({
        'age': age,
        'monthly_income': monthly_income,
        'account_balance': account_balance,
        'savings_balance': savings_balance,
        'tenure_months': tenure_months,
        'num_products': num_products,
        'credit_score': credit_score,
        'total_debt': total_debt,
        'credit_limit': credit_limit,
        'credit_utilization': credit_utilization,
        'num_loans': num_loans,
        'num_late_payments': num_late_payments,
        'num_defaults': num_defaults,
        'monthly_transactions': monthly_transactions,
        'avg_transaction_amount': avg_transaction_amount,
        'num_atm_withdrawals': num_atm_withdrawals,
        'international_transactions': international_transactions,
        'has_investment_account': has_investment_account,
        'investment_balance': investment_balance,
        'has_insurance': has_insurance,
        'has_mortgage': has_mortgage,
        'mortgage_amount': mortgage_amount,
        'days_since_last_activity': days_since_last_activity,
        'complaint_count': complaint_count,
        'overdraft_count': overdraft_count,
        'suspicious_activity_flag': suspicious_activity_flag,
        'gender': gender,
        'marital_status': marital_status,
        'education_level': education_level,
        'region': region,
        'employment_status': employment_status,
        'online_banking_usage': online_banking_usage,
    })
    
    # Generate target variable (churn) based on features
    churn_prob = (
        0.05 +
        (days_since_last_activity / 365) * 0.3 +
        (complaint_count / 5) * 0.2 +
        (num_defaults / 2) * 0.15 +
        0.1 * (credit_utilization > 80)
    ).clip(0, 1)
    
    churn = np.random.binomial(1, churn_prob)
    df['churn'] = churn
    
    # Add customer segments
    def assign_segment(row):
        if row['account_balance'] > row['monthly_income'] * 12:
            return 'VIP'
        elif row['account_balance'] > row['monthly_income'] * 6:
            return 'Premium'
        elif row['num_products'] >= 3:
            return 'Active'
        else:
            return 'Standard'
    
    df['client_segment'] = df.apply(assign_segment, axis=1)
    
    # Risk classification
    risk_score = (
        0.3 * (credit_utilization / 100) +
        0.2 * (num_late_payments / 3) +
        0.3 * (num_defaults / 1) +
        0.2 * (days_since_last_activity / 365)
    ).clip(0, 1)
    
    df['risk_class'] = pd.cut(
        risk_score,
        bins=[0, 0.33, 0.66, 1.0],
        labels=['Low', 'Medium', 'High'],
        include_lowest=True
    )
    
    return df

def save_dataset(df: pd.DataFrame, output_path: str = "bank_customer_dataset.xlsx"):
    """Save dataset to Excel file."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with pd.ExcelWriter(output_path) as writer:
        df.to_excel(writer, sheet_name="customers", index=False)
        
        # Add summary statistics sheet
        summary_stats = pd.DataFrame({
            'Feature': df.describe().columns,
            'Count': df.describe().loc['count'].values,
            'Mean': df.describe().loc['mean'].values,
            'Std': df.describe().loc['std'].values,
            'Min': df.describe().loc['min'].values,
            'Max': df.describe().loc['max'].values,
        })
        summary_stats.to_excel(writer, sheet_name="summary", index=False)
    
    print(f"Dataset saved to {output_path}")
    return df

if __name__ == "__main__":
    # Generate and save dataset
    print("Generating banking customer dataset...")
    df = generate_banking_dataset(n_samples=5000)
    print(f"Generated {len(df)} records with {len(df.columns)} features")
    
    # Save to data directory
    data_dir = Path(__file__).parent / "data"
    save_dataset(df, data_dir / "bank_customer_dataset.xlsx")
    
    print("\nDataset Overview:")
    print(df.head())
    print(f"\nShape: {df.shape}")
    print(f"\nChurn Rate: {df['churn'].mean():.2%}")
    print(f"Client Segments: {df['client_segment'].value_counts().to_dict()}")
    print(f"Risk Classes: {df['risk_class'].value_counts().to_dict()}")
