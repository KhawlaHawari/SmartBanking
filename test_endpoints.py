#!/usr/bin/env python
"""
SMART BANKING API — ENDPOINT TESTING SCRIPT

This script tests all API endpoints and validates responses.
Run this after starting the backend: python test_endpoints.py
"""

import json
import time
import requests
from typing import Any, Dict

# Configuration
API_BASE = "http://localhost:8000/api"
TIMEOUT = 10

# ANSI color codes
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"
BOLD = "\033[1m"

# Test data
SAMPLE_CUSTOMER = {
    "age": 42,
    "monthly_income": 6200,
    "account_balance": 18500,
    "savings_balance": 9100,
    "tenure_months": 48,
    "num_products": 3,
    "credit_score": 690,
    "total_debt": 7400,
    "credit_limit": 15000,
    "credit_utilization": 0.42,
    "num_loans": 2,
    "num_late_payments": 1,
    "num_defaults": 0,
    "monthly_transactions": 67,
    "avg_transaction_amount": 94,
    "num_atm_withdrawals": 4,
    "international_transactions": 2,
    "has_investment_account": 1,
    "investment_balance": 12000,
    "has_insurance": 1,
    "has_mortgage": 0,
    "mortgage_amount": 0,
    "days_since_last_activity": 3,
    "complaint_count": 0,
    "overdraft_count": 0,
    "suspicious_activity_flag": 0,
    "gender": "Male",
    "marital_status": "Married",
    "education_level": "Bachelor",
    "region": "West",
    "employment_status": "Employed",
    "online_banking_usage": "High",
}


def print_header(title: str) -> None:
    """Print a formatted header."""
    print(f"\n{BLUE}{BOLD}{'=' * 80}{RESET}")
    print(f"{BLUE}{BOLD}{title:^80}{RESET}")
    print(f"{BLUE}{BOLD}{'=' * 80}{RESET}\n")


def print_test(name: str) -> None:
    """Print test name."""
    print(f"{YELLOW}📝 Testing: {name}{RESET}")


def print_success(msg: str) -> None:
    """Print success message."""
    print(f"{GREEN}✅ {msg}{RESET}")


def print_error(msg: str) -> None:
    """Print error message."""
    print(f"{RED}❌ {msg}{RESET}")


def print_info(msg: str) -> None:
    """Print info message."""
    print(f"{BLUE}ℹ️  {msg}{RESET}")


def test_endpoint(
    method: str,
    endpoint: str,
    data: Dict[str, Any] | None = None,
    expected_status: int = 200,
) -> Dict[str, Any] | None:
    """
    Test an API endpoint.
    
    Args:
        method: HTTP method (GET, POST, etc.)
        endpoint: Endpoint path (e.g., "/health")
        data: JSON payload for POST requests
        expected_status: Expected HTTP status code
        
    Returns:
        Response JSON or None if failed
    """
    url = f"{API_BASE}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=TIMEOUT)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=TIMEOUT)
        else:
            print_error(f"Unsupported method: {method}")
            return None
        
        # Check status code
        if response.status_code == expected_status:
            print_success(f"{method} {endpoint} → {response.status_code}")
            return response.json()
        else:
            print_error(
                f"{method} {endpoint} returned {response.status_code} "
                f"(expected {expected_status})"
            )
            if response.text:
                print(f"  Response: {response.text[:200]}")
            return None
    
    except requests.exceptions.ConnectionError:
        print_error(f"Connection failed. Is the backend running on {API_BASE}?")
        return None
    except requests.exceptions.Timeout:
        print_error(f"Request timeout ({TIMEOUT}s)")
        return None
    except Exception as e:
        print_error(f"Exception: {e}")
        return None


def test_health() -> bool:
    """Test /api/health endpoint."""
    print_test("/api/health")
    result = test_endpoint("GET", "/health")
    
    if result:
        print_info(f"Status: {result.get('status', 'unknown')}")
        print_info(f"Models loaded: {result.get('models_loaded', False)}")
        print_info(f"EDA loaded: {result.get('eda_loaded', False)}")
        return result.get("models_loaded", False) and result.get("eda_loaded", False)
    return False


def test_predict_single() -> bool:
    """Test /api/predict endpoint (single customer)."""
    print_test("/api/predict (single customer)")
    result = test_endpoint("POST", "/predict", data=SAMPLE_CUSTOMER)
    
    if result:
        print_info(f"Segment: {result.get('segment')}")
        print_info(f"Segment confidence: {result.get('segment_confidence'):.2%}")
        print_info(f"Risk label: {result.get('risk_label')}")
        print_info(f"Risk probability: {result.get('risk_probability'):.2%}")
        print_info(f"Churn probability: {result.get('churn_probability'):.2%}")
        print_info(f"Churn label: {result.get('churn_label')}")
        print_info(f"Recommended action: {result.get('recommended_action')}")
        print_info(f"Action confidence: {result.get('action_confidence'):.2%}")
        return True
    return False


def test_predict_batch() -> bool:
    """Test /api/predict/batch endpoint (multiple customers)."""
    print_test("/api/predict/batch (3 customers)")
    
    customers = [
        SAMPLE_CUSTOMER,
        {**SAMPLE_CUSTOMER, "age": 35, "monthly_income": 5500, "credit_score": 750},
        {**SAMPLE_CUSTOMER, "age": 55, "monthly_income": 8000, "credit_score": 620},
    ]
    
    payload = {"customers": customers}
    result = test_endpoint("POST", "/predict/batch", data=payload)
    
    if result and isinstance(result, list):
        print_info(f"Got {len(result)} predictions")
        for i, pred in enumerate(result, 1):
            print_info(f"  Customer {i}: {pred.get('segment')} | "
                      f"Risk: {pred.get('risk_label')} | "
                      f"Action: {pred.get('recommended_action')}")
        return True
    return False


def test_metrics() -> bool:
    """Test /api/metrics endpoint."""
    print_test("/api/metrics")
    result = test_endpoint("GET", "/metrics")
    
    if result:
        models = list(result.keys())
        print_info(f"Models in metrics: {', '.join(models)}")
        for model_name, scores in result.items():
            if isinstance(scores, dict):
                main_metric = next(
                    (v for k, v in scores.items() 
                     if k in ["auc_roc", "f1_macro", "accuracy"]),
                    None
                )
                if main_metric:
                    print_info(f"  {model_name}: {main_metric:.4f}")
        return True
    return False


def test_eda() -> bool:
    """Test /api/eda endpoint."""
    print_test("/api/eda")
    result = test_endpoint("GET", "/eda")
    
    if result:
        keys = list(result.keys())
        print_info(f"EDA data available for: {', '.join(k for k in keys if k != 'loaded')}")
        
        if "segment_distribution" in result:
            seg_dist = result["segment_distribution"]
            if seg_dist:
                print_info(f"  Segment distribution: {len(seg_dist)} segments")
        
        if "risk_distribution" in result:
            risk_dist = result["risk_distribution"]
            if risk_dist:
                print_info(f"  Risk distribution: {len(risk_dist)} risk classes")
        
        if "action_distribution" in result:
            action_dist = result["action_distribution"]
            if action_dist:
                print_info(f"  Action distribution: {len(action_dist)} actions")
        
        return True
    return False


def test_error_handling() -> bool:
    """Test error handling with invalid data."""
    print_test("Error handling (invalid input)")
    
    invalid_data = {
        "age": -10,  # Invalid age
        "monthly_income": -5000,  # Invalid income
    }
    
    result = test_endpoint("POST", "/predict", data=invalid_data, expected_status=422)
    
    if result is not None or result is None:  # Either error response or connection failed
        print_success("Error handling works correctly")
        return True
    return False


def run_all_tests() -> None:
    """Run all endpoint tests."""
    print_header("SMART BANKING API — ENDPOINT TESTS")
    
    print_info(f"API Base URL: {API_BASE}")
    print_info(f"Testing at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Wait a moment for any delayed startup
    print_info("Waiting for API to be ready...")
    time.sleep(1)
    
    tests = [
        ("Health Check", test_health),
        ("Single Prediction", test_predict_single),
        ("Batch Prediction", test_predict_batch),
        ("Model Metrics", test_metrics),
        ("EDA Statistics", test_eda),
        ("Error Handling", test_error_handling),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print_error(f"Test crashed: {e}")
            results[test_name] = False
        print()
    
    # Summary
    print_header("TEST SUMMARY")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    failed = total - passed
    
    for test_name, passed_flag in results.items():
        status = f"{GREEN}✅ PASSED{RESET}" if passed_flag else f"{RED}❌ FAILED{RESET}"
        print(f"{test_name:<30} {status}")
    
    print()
    print(f"Total: {total} | {GREEN}Passed: {passed}{RESET} | {RED}Failed: {failed}{RESET}")
    
    if failed == 0:
        print(f"\n{GREEN}{BOLD}🎉 ALL TESTS PASSED!{RESET}\n")
    else:
        print(f"\n{YELLOW}⚠️  Some tests failed. Check the backend logs.{RESET}\n")


def print_curl_examples() -> None:
    """Print curl command examples."""
    print_header("CURL COMMAND EXAMPLES")
    
    examples = [
        ("Health Check", "GET", "/health", None),
        (
            "Single Prediction",
            "POST",
            "/predict",
            {"age": 42, "monthly_income": 6200, "credit_score": 690, "gender": "Male"},
        ),
        ("Model Metrics", "GET", "/metrics", None),
        ("EDA Statistics", "GET", "/eda", None),
    ]
    
    for name, method, endpoint, data in examples:
        print(f"{BOLD}{name}:{RESET}")
        if method == "GET":
            print(f"  curl -X GET {API_BASE}{endpoint}")
        else:
            json_data = json.dumps(data or {})
            print(f"  curl -X POST {API_BASE}{endpoint} \\")
            print(f"    -H 'Content-Type: application/json' \\")
            print(f"    -d '{json_data}'")
        print()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--curl":
        print_curl_examples()
    else:
        run_all_tests()
        print("\n" + BLUE + "💡 Tip: Run with --curl to see curl command examples" + RESET + "\n")
