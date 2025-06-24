import requests
import json
import time

def test_financial_advisor():
    # API endpoint
    url = "http://localhost:8001/api/v1/chat"
    
    # Test message
    message = {
        "message": "I'm a 30-year-old with a $100,000 annual income and moderate risk tolerance. What investment portfolio would you recommend for me?",
        "chat_history": []
    }
    
    # Wait for server to be ready
    max_retries = 5
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            # Send request
            print(f"\nAttempt {attempt + 1} of {max_retries}")
            response = requests.post(url, json=message, timeout=30)
            
            # Check if request was successful
            response.raise_for_status()
            
            # Print response
            print("\nResponse from Financial Advisor:")
            print(json.dumps(response.json(), indent=2))
            return
            
        except requests.exceptions.ConnectionError:
            print(f"Connection error. Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
        except requests.exceptions.Timeout:
            print(f"Request timed out. Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return
    
    print("Failed to connect to the server after multiple attempts.")

if __name__ == "__main__":
    test_financial_advisor() 