# OpenCode AI Coordinator - Examples

This document provides practical examples and use cases for the OpenCode AI Coordinator.

---

## Table of Contents
1. [Schnellstart Examples](#schnellstart-examples)
2. [Code Generation Examples](#code-generation-examples)
3. [Code Validation Examples](#code-validation-examples)
4. [Code Formatting Examples](#code-formatting-examples)
5. [Template Examples](#template-examples)
6. [Multi-Provider Examples](#multi-provider-examples)
7. [Batch Processing Examples](#batch-processing-examples)
8. [Webhook Integration Examples](#webhook-integration-examples)
9. [Advanced Use Cases](#advanced-use-cases)

---

## Schnellstart Examples

### CLI Usage

```bash
# Start the server
python main.py --debug --reload

# In another terminal, test the API
curl http://localhost:8000/health

# Generate code
curl -X POST http://localhost:8000/code/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Create a Python hello world", "language": "python"}'
```

### Docker Usage

```bash
# Build and run
docker-compose up -d

# Test
docker-compose exec coordinator curl http://localhost:8000/health
```

---

## Code Generation Examples

### Python Examples

#### Simple Function Generation

```python
import requests

url = "http://localhost:8000/code/generate"
headers = {"Content-Type": "application/json"}
data = {
    "prompt": "Create a Python function to calculate the factorial of a number",
    "language": "python",
    "temperature": 0.7,
    "max_tokens": 1000
}

response = requests.post(url, headers=headers, json=data)
task = response.json()

# Get the result
task_id = task["task_id"]
result = requests.get(f"http://localhost:8000/task/{task_id}").json()

print(result["result"])
```

**Expected Output:**
```python
def factorial(n: int) -> int:
    """Calculate the factorial of a number.
    
    Args:
        n: A non-negative integer
    
    Returns:
        The factorial of n
    
    Raises:
        ValueError: If n is negative
    """
    if n < 0:
        raise ValueError("n must be non-negative")
    if n <= 1:
        return 1
    return n * factorial(n - 1)
```

#### Class Generation

```python
import requests

url = "http://localhost:8000/code/generate"
data = {
    "prompt": "Create a Python class for a BankAccount with deposit, withdraw, and get_balance methods",
    "language": "python",
    "temperature": 0.5,
    "max_tokens": 2000
}

response = requests.post(url, json=data)
task = response.json()

# Wait and get result
import time
time.sleep(2)
result = requests.get(f"http://localhost:8000/task/{task['task_id']}").json()

print(result["result"])
```

**Expected Output:**
```python
class BankAccount:
    """A simple bank account class."""
    
    def __init__(self, account_number: str, initial_balance: float = 0.0):
        self.account_number = account_number
        self._balance = initial_balance
    
    def deposit(self, amount: float) -> None:
        """Deposit money into the account."""
        if amount <= 0:
            raise ValueError("Amount must be positive")
        self._balance += amount
    
    def withdraw(self, amount: float) -> None:
        """Withdraw money from the account."""
        if amount <= 0:
            raise ValueError("Amount must be positive")
        if amount > self._balance:
            raise ValueError("Insufficient funds")
        self._balance -= amount
    
    def get_balance(self) -> float:
        """Get the current balance."""
        return self._balance
    
    def __str__(self) -> str:
        return f"BankAccount({self.account_number}, balance={self._balance})"
```

#### REST API Generation

```python
import requests

url = "http://localhost:8000/code/generate"
data = {
    "prompt": "Create a FastAPI application with CRUD endpoints for a User model",
    "language": "python",
    "framework": "fastapi",
    "include_comments": True,
    "include_tests": True,
    "max_tokens": 4000
}

response = requests.post(url, json=data)
task = response.json()

# Get result
result = requests.get(f"http://localhost:8000/task/{task['task_id']}").json()
print(result["result"])
```

#### Database Model Generation

```python
import requests

url = "http://localhost:8000/code/generate"
data = {
    "prompt": "Create SQLAlchemy models for User, Post, and Comment with relationships",
    "language": "python",
    "max_tokens": 3000
}

response = requests.post(url, json=data)
result = requests.get(f"http://localhost:8000/task/{response.json()['task_id']}").json()

print(result["result"])
```

---

### JavaScript Examples

#### Express.js Endpoint

```javascript
const axios = require('axios');

async function generateExpressEndpoint() {
    const url = 'http://localhost:8000/code/generate';
    const data = {
        prompt: 'Create an Express.js endpoint for user authentication with JWT',
        language: 'javascript',
        framework: 'express',
        temperature: 0.7,
        max_tokens: 3000
    };
    
    const response = await axios.post(url, data);
    const taskId = response.data.task_id;
    
    // Poll for result
    let result = await axios.get(`http://localhost:8000/task/${taskId}`);
    while (result.data.status === 'pending' || result.data.status === 'processing') {
        await new Promise(resolve => setTimeout(resolve, 1000));
        result = await axios.get(`http://localhost:8000/task/${taskId}`);
    }
    
    console.log(result.data.result);
}

generateExpressEndpoint();
```

#### React Component

```javascript
const axios = require('axios');

async function generateReactComponent() {
    const url = 'http://localhost:8000/code/generate';
    const data = {
        prompt: 'Create a React functional component for a user profile card with TypeScript',
        language: 'typescript',
        framework: 'react',
        max_tokens: 2500
    };
    
    const response = await axios.post(url, data);
    const taskId = response.data.task_id;
    
    const result = await axios.get(`http://localhost:8000/task/${taskId}`);
    console.log(result.data.result);
}

generateReactComponent();
```

---

### TypeScript Examples

#### Interface and Class

```javascript
const axios = require('axios');

async function generateTypeScriptCode() {
    const url = 'http://localhost:8000/code/generate';
    const data = {
        prompt: 'Create TypeScript interfaces and classes for an e-commerce Product system',
        language: 'typescript',
        max_tokens: 3000
    };
    
    const response = await axios.post(url, data);
    const taskId = response.data.task_id;
    
    const result = await axios.get(`http://localhost:8000/task/${taskId}`);
    console.log(result.data.result);
}

generateTypeScriptCode();
```

---

### SQL Examples

#### Table Creation

```python
import requests

url = "http://localhost:8000/code/generate"
data = {
    "prompt": "Create SQL tables for users, posts, comments, and likes with proper relationships",
    "language": "sql",
    "max_tokens": 2000
}

response = requests.post(url, json=data)
result = requests.get(f"http://localhost:8000/task/{response.json()['task_id']}").json()

print(result["result"])
```

**Expected Output:**
```sql
-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Posts table
CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Comments table
CREATE TABLE comments (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    post_id INTEGER REFERENCES posts(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Likes table
CREATE TABLE likes (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    post_id INTEGER REFERENCES posts(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, post_id)
);

-- Indexes
CREATE INDEX idx_posts_user_id ON posts(user_id);
CREATE INDEX idx_comments_user_id ON comments(user_id);
CREATE INDEX idx_comments_post_id ON comments(post_id);
CREATE INDEX idx_likes_user_id ON likes(user_id);
CREATE INDEX idx_likes_post_id ON likes(post_id);
```

---

## Code Validation Examples

### Python Validation

```python
import requests

url = "http://localhost:8000/code/validate"
data = {
    "code": """
def calculate_average(numbers):
    total = sum(numbers)
    count = len(numbers)
    return total / count

result = calculate_average([1, 2, 3, 4, 5])
print(result)
""",
    "language": "python",
    "check_syntax": True,
    "check_semantics": True,
    "check_style": True
}

response = requests.post(url, json=data)
task = response.json()

# Get validation result
result = requests.get(f"http://localhost:8000/task/{task['task_id']}").json()
print(result["result"])
```

**Expected Output:**
```json
{
  "valid": true,
  "errors": [],
  "warnings": [
    "No type hints for function parameters",
    "No docstring for function",
    "Consider adding error handling for empty list"
  ],
  "suggestions": [
    "Add type hints: def calculate_average(numbers: List[float]) -> float:",
    "Add docstring explaining the function",
    "Add check for empty list: if not numbers: return 0"
  ]
}
```

### JavaScript Validation

```javascript
const axios = require('axios');

async function validateJavaScript() {
    const url = 'http://localhost:8000/code/validate';
    const data = {
        code: `
function calculateAverage(numbers) {
    let total = numbers.reduce((a, b) => a + b, 0);
    return total / numbers.length;
}

console.log(calculateAverage([1, 2, 3, 4, 5]));
        `,
        language: 'javascript',
        check_syntax: true,
        check_semantics: true
    };
    
    const response = await axios.post(url, data);
    const taskId = response.data.task_id;
    
    const result = await axios.get(`http://localhost:8000/task/${taskId}`);
    console.log(result.data.result);
}

validateJavaScript();
```

---

## Code Formatting Examples

### Python Formatting

```python
import requests

url = "http://localhost:8000/code/format"
data = {
    "code": "def hello(name):\n    print(f\"Hello {name}\")\n    return True",
    "language": "python",
    "style": "pep8",
    "indent_size": 4,
    "line_length": 88
}

response = requests.post(url, json=data)
task = response.json()

# Get formatted code
result = requests.get(f"http://localhost:8000/task/{task['task_id']}").json()
print(result["result"])
```

**Expected Output:**
```python
def hello(name):
    """Greet someone by name."""
    print(f"Hello {name}")
    return True
```

### JavaScript Formatting

```javascript
const axios = require('axios');

async function formatJavaScript() {
    const url = 'http://localhost:8000/code/format';
    const data = {
        code: `function hello(name){console.log("Hello " + name);return true;}`,
        language: 'javascript',
        style: 'prettier',
        indent_size: 2,
        line_length: 80
    };
    
    const response = await axios.post(url, data);
    const taskId = response.data.task_id;
    
    const result = await axios.get(`http://localhost:8000/task/${taskId}`);
    console.log(result.data.result);
}

formatJavaScript();
```

---

## Template Examples

### Using Built-in Templates

```python
import requests

# List available templates
response = requests.get("http://localhost:8000/code/templates")
print("Available templates:", response.json())

# Generate from template
url = "http://localhost:8000/code/generate-from-template"
data = {
    "template_name": "fastapi_endpoint",
    "variables": {
        "request_model": "UserCreate",
        "response_model": "User",
        "endpoint": "users",
        "function_name": "create_user",
        "description": "Create a new user"
    },
    "language": "python"
}

response = requests.post(url, json=data)
task = response.json()

# Get result
result = requests.get(f"http://localhost:8000/task/{task['task_id']}").json()
print(result["result"])
```

### Creating Custom Templates

```python
# Add a custom template
from open_coordinator.utils.code_templates import get_template_manager

template_manager = get_template_manager()
template_manager.add_template(
    language="python",
    template_name="my_template",
    template_content="""
def {{function_name}}({{params}}) -> {{return_type}}:
    '''{{description}}'''
    {{body}}
"""
)

# Use the template
url = "http://localhost:8000/code/generate-from-template"
data = {
    "template_name": "my_template",
    "variables": {
        "function_name": "add",
        "params": "a: int, b: int",
        "return_type": "int",
        "description": "Add two numbers",
        "body": "return a + b"
    },
    "language": "python"
}

response = requests.post(url, json=data)
result = requests.get(f"http://localhost:8000/task/{response.json()['task_id']}").json()
print(result["result"])
```

---

## Multi-Provider Examples

### Load Balancing

```python
import requests

# The coordinator automatically load balances between providers
# based on priority and availability

url = "http://localhost:8000/code/generate"
data = {
    "prompt": "Create a Python function for binary search",
    "language": "python",
    # Let the coordinator choose the best provider
    "temperature": 0.5
}

response = requests.post(url, json=data)
task = response.json()

# Get result
result = requests.get(f"http://localhost:8000/task/{task['task_id']}").json()
print(f"Provider used: {result['provider_used']}")
print(f"Model used: {result['model_used']}")
print(f"Result:\n{result['result']}")
```

### Provider Preference

```python
import requests

url = "http://localhost:8000/code/generate"
data = {
    "prompt": "Create a complex algorithm in Python",
    "language": "python",
    # Prefer OpenAI, fallback to Anthropic, then Mistral
    "provider_preference": ["openai", "anthropic", "mistral"],
    "model_preference": "gpt-4o",
    "temperature": 0.7
}

response = requests.post(url, json=data)
result = requests.get(f"http://localhost:8000/task/{response.json()['task_id']}").json()

print(f"Used provider: {result['provider_used']}")
print(f"Used model: {result['model_used']}")
```

### Fallback Handling

```python
import requests

# If the preferred provider fails, the coordinator will automatically
# try the next provider in the preference list

url = "http://localhost:8000/code/generate"
data = {
    "prompt": "Generate code that requires a very large context",
    "language": "python",
    "provider_preference": ["anthropic", "openai", "mistral"],
    "max_tokens": 8000
}

response = requests.post(url, json=data)
result = requests.get(f"http://localhost:8000/task/{response.json()['task_id']}").json()

# The coordinator will automatically retry with the next provider if one fails
print(f"Completed with provider: {result['provider_used']}")
```

---

## Batch Processing Examples

### Sequential Processing

```python
import requests
import time

def process_task(prompt):
    """Process a single task and wait for completion."""
    url = "http://localhost:8000/execute?wait=true&timeout=60"
    data = {
        "task_type": "code_generation",
        "prompt": prompt,
        "language": "python",
        "temperature": 0.7
    }
    
    response = requests.post(url, json=data)
    return response.json()

# Process multiple tasks sequentially
prompts = [
    "Create a Python function to sort a list",
    "Create a Python function to search a list",
    "Create a Python function to reverse a string",
    "Create a Python function to check if a number is prime",
    "Create a Python function to calculate factorial"
]

results = []
for prompt in prompts:
    result = process_task(prompt)
    results.append(result)
    print(f"Completed: {prompt[:50]}...")

# Print all results
for i, result in enumerate(results):
    print(f"\n--- Result {i+1} ---")
    print(result["result"])
```

### Parallel Processing

```python
import requests
import concurrent.futures
import time

def process_task_async(prompt):
    """Process a task asynchronously."""
    url = "http://localhost:8000/code/generate"
    data = {
        "prompt": prompt,
        "language": "python",
        "temperature": 0.7
    }
    
    response = requests.post(url, json=data)
    return response.json()["task_id"]

def get_result(task_id):
    """Get task result."""
    while True:
        result = requests.get(f"http://localhost:8000/task/{task_id}").json()
        if result["status"] in ["completed", "failed"]:
            return result
        time.sleep(0.5)

# Process multiple tasks in parallel
prompts = [
    "Create a Python function to sort a list",
    "Create a Python function to search a list",
    "Create a Python function to reverse a string",
    "Create a Python function to check if a number is prime",
    "Create a Python function to calculate factorial"
]

# Create tasks in parallel
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
    task_ids = list(executor.map(process_task_async, prompts))

# Get results
results = []
for task_id in task_ids:
    result = get_result(task_id)
    results.append(result)
    print(f"Completed task: {task_id}")

# Print all results
for i, result in enumerate(results):
    print(f"\n--- Result {i+1} ---")
    print(result["result"])
```

### Batch Endpoint (Future)

```python
# This will be available in future versions
import requests

url = "http://localhost:8000/batch"
data = {
    "tasks": [
        {"task_type": "code_generation", "prompt": "Task 1", "language": "python"},
        {"task_type": "code_generation", "prompt": "Task 2", "language": "python"},
        {"task_type": "code_generation", "prompt": "Task 3", "language": "python"}
    ],
    "wait": True,
    "timeout": 300
}

response = requests.post(url, json=data)
results = response.json()

for result in results:
    print(result["result"])
```

---

## Webhook Integration Examples

### Discord Webhook

```python
import requests

# Configure a task with webhook
url = "http://localhost:8000/task"
data = {
    "task_type": "code_generation",
    "prompt": "Create a Python script to parse CSV files",
    "language": "python",
    "metadata": {
        "webhook_url": "https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_WEBHOOK_TOKEN",
        "webhook_method": "POST",
        "webhook_headers": {"Content-Type": "application/json"}
    }
}

response = requests.post(url, json=data)
print(f"Task created: {response.json()['task_id']}")

# The coordinator will send a webhook when the task completes
```

### Slack Webhook

```python
import requests

url = "http://localhost:8000/task"
data = {
    "task_type": "code_generation",
    "prompt": "Create a Python class for a Slack bot",
    "language": "python",
    "metadata": {
        "webhook_url": "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK",
        "webhook_method": "POST",
        "webhook_headers": {"Content-Type": "application/json"},
        "webhook_payload_transform": "slack"  # Transform payload for Slack
    }
}

response = requests.post(url, json=data)
```

### Custom Webhook Server

```python
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle webhook from OpenCode Coordinator."""
    data = request.json
    
    # Process the webhook
    if data.get('event') == 'task.completed':
        task_data = data.get('data', {})
        print(f"Task {task_data.get('task_id')} completed!")
        print(f"Result: {task_data.get('result')[:100]}...")
        
        # Store in database, send notifications, etc.
        
    return jsonify({"status": "received"}), 200

if __name__ == '__main__':
    app.run(port=5000)

# Then create a task with this webhook
url = "http://localhost:8000/task"
data = {
    "task_type": "code_generation",
    "prompt": "Create a Python webhook handler",
    "language": "python",
    "metadata": {
        "webhook_url": "http://localhost:5000/webhook"
    }
}

response = requests.post(url, json=data)
```

---

## Advanced Use Cases

### Code Refactoring

```python
import requests

url = "http://localhost:8000/task"
data = {
    "task_type": "code_refactoring",
    "code": """
def calculate_total(items):
    total = 0
    for i in range(len(items)):
        total += items[i]['price'] * items[i]['quantity']
    return total

def process_order(order):
    items = order['items']
    total = calculate_total(items)
    tax = total * 0.08
    final_total = total + tax
    return {'total': total, 'tax': tax, 'final_total': final_total}
""",
    "language": "python",
    "temperature": 0.3  # Lower temperature for more deterministic refactoring
}

response = requests.post(url, json=data)
result = requests.get(f"http://localhost:8000/task/{response.json()['task_id']}").json()

print("Refactored code:")
print(result["result"])
```

**Expected Output:**
```python
from typing import List, Dict, Tuple

def calculate_total(items: List[Dict[str, float]]) -> float:
    """Calculate the total price of items.
    
    Args:
        items: List of items with 'price' and 'quantity' keys
    
    Returns:
        Total price
    """
    return sum(item['price'] * item['quantity'] for item in items)


def process_order(order: Dict[str, List[Dict[str, float]]]) -> Dict[str, float]:
    """Process an order and calculate totals.
    
    Args:
        order: Dictionary containing 'items' key
    
    Returns:
        Dictionary with total, tax, and final_total
    """
    items = order['items']
    total = calculate_total(items)
    tax = total * 0.08
    return {
        'total': total,
        'tax': tax,
        'final_total': total + tax
    }
```

### Code Documentation

```python
import requests

url = "http://localhost:8000/task"
data = {
    "task_type": "code_documentation",
    "code": """
class DataProcessor:
    def __init__(self, data):
        self.data = data
    
    def clean(self):
        return [x for x in self.data if x is not None]
    
    def normalize(self):
        cleaned = self.clean()
        return [x.strip().lower() for x in cleaned]
    
    def analyze(self):
        normalized = self.normalize()
        return {
            'count': len(normalized),
            'unique': len(set(normalized)),
            'average_length': sum(len(x) for x in normalized) / len(normalized) if normalized else 0
        }
""",
    "language": "python"
}

response = requests.post(url, json=data)
result = requests.get(f"http://localhost:8000/task/{response.json()['task_id']}").json()

print("Documentation:")
print(result["result"])
```

**Expected Output:**
```markdown
# DataProcessor Class Documentation

## Overview
The `DataProcessor` class provides methods for cleaning, normalizing, and analyzing data.

## Class: DataProcessor

### Constructor
```python
def __init__(self, data)
```
**Parameters:**
- `data` (list): The input data to be processed

### Methods

#### clean()
```python
def clean(self)
```
Removes `None` values from the data.

**Returns:**
- `list`: A new list with `None` values removed

**Example:**
```python
processor = DataProcessor([1, None, 2, None, 3])
cleaned = processor.clean()
# cleaned = [1, 2, 3]
```

#### normalize()
```python
def normalize(self)
```
Cleans the data and converts all strings to lowercase with whitespace removed.

**Returns:**
- `list`: A new list with cleaned, lowercase strings

**Example:**
```python
processor = DataProcessor(['  Hello  ', None, 'WORLD  '])
normalized = processor.normalize()
# normalized = ['hello', 'world']
```

#### analyze()
```python
def analyze(self)
```
Normalizes the data and returns statistics.

**Returns:**
- `dict`: Dictionary containing:
  - `count`: Number of items
  - `unique`: Number of unique items
  - `average_length`: Average string length

**Example:**
```python
processor = DataProcessor(['apple', 'banana', 'apple', 'cherry'])
analysis = processor.analyze()
# analysis = {'count': 3, 'unique': 3, 'average_length': 5.33}
```
```

### Code Optimization

```python
import requests

url = "http://localhost:8000/task"
data = {
    "task_type": "code_optimization",
    "code": """
def find_duplicates(numbers):
    result = []
    for i in range(len(numbers)):
        for j in range(i + 1, len(numbers)):
            if numbers[i] == numbers[j]:
                if numbers[i] not in result:
                    result.append(numbers[i])
    return result

def process_large_list(numbers):
    duplicates = find_duplicates(numbers)
    unique = [x for x in numbers if x not in duplicates]
    return {'duplicates': duplicates, 'unique': unique}
""",
    "language": "python"
}

response = requests.post(url, json=data)
result = requests.get(f"http://localhost:8000/task/{response.json()['task_id']}").json()

print("Optimized code:")
print(result["result"])
```

**Expected Output:**
```python
def find_duplicates(numbers):
    """Find duplicate values in a list.
    
    Args:
        numbers: List of values to check
    
    Returns:
        List of duplicate values (each appears only once in result)
    """
    seen = set()
    duplicates = set()
    
    for num in numbers:
        if num in seen:
            duplicates.add(num)
        else:
            seen.add(num)
    
    return list(duplicates)


def process_large_list(numbers):
    """Process a large list to find duplicates and unique values.
    
    Args:
        numbers: List of numbers to process
    
    Returns:
        Dictionary with 'duplicates' and 'unique' keys
    """
    duplicates = find_duplicates(numbers)
    unique = list(set(numbers) - set(duplicates))
    return {'duplicates': duplicates, 'unique': unique}
```

### Unit Test Generation

```python
import requests

url = "http://localhost:8000/task"
data = {
    "task_type": "unit_test_generation",
    "code": """
def calculate_discount(price, discount_percent):
    if discount_percent < 0 or discount_percent > 100:
        raise ValueError("Discount must be between 0 and 100")
    return price * (1 - discount_percent / 100)

class ShoppingCart:
    def __init__(self):
        self.items = []
    
    def add_item(self, name, price, quantity=1):
        self.items.append({'name': name, 'price': price, 'quantity': quantity})
    
    def get_total(self):
        return sum(item['price'] * item['quantity'] for item in self.items)
    
    def apply_discount(self, discount_percent):
        total = self.get_total()
        return calculate_discount(total, discount_percent)
""",
    "language": "python"
}

response = requests.post(url, json=data)
result = requests.get(f"http://localhost:8000/task/{response.json()['task_id']}").json()

print("Generated tests:")
print(result["result"])
```

**Expected Output:**
```python
import unittest
from io import StringIO
import sys


class TestCalculateDiscount(unittest.TestCase):
    
    def test_normal_discount(self):
        """Test normal discount calculation."""
        result = calculate_discount(100, 10)
        self.assertEqual(result, 90)
        
    def test_zero_discount(self):
        """Test zero discount."""
        result = calculate_discount(100, 0)
        self.assertEqual(result, 100)
        
    def test_full_discount(self):
        """Test 100% discount."""
        result = calculate_discount(100, 100)
        self.assertEqual(result, 0)
        
    def test_invalid_discount_negative(self):
        """Test negative discount raises error."""
        with self.assertRaises(ValueError):
            calculate_discount(100, -10)
            
    def test_invalid_discount_over_100(self):
        """Test discount over 100 raises error."""
        with self.assertRaises(ValueError):
            calculate_discount(100, 110)


class TestShoppingCart(unittest.TestCase):
    
    def setUp(self):
        """Set up test cart."""
        self.cart = ShoppingCart()
        
    def test_add_item(self):
        """Test adding items to cart."""
        self.cart.add_item("Apple", 1.0, 3)
        self.assertEqual(len(self.cart.items), 1)
        self.assertEqual(self.cart.items[0]['name'], "Apple")
        
    def test_get_total(self):
        """Test total calculation."""
        self.cart.add_item("Apple", 1.0, 3)
        self.cart.add_item("Banana", 0.5, 2)
        self.assertEqual(self.cart.get_total(), 4.0)
        
    def test_apply_discount(self):
        """Test discount application."""
        self.cart.add_item("Apple", 10.0)
        self.cart.add_item("Banana", 10.0)
        discounted_total = self.cart.apply_discount(10)
        self.assertEqual(discounted_total, 18.0)
        
    def test_empty_cart(self):
        """Test empty cart."""
        self.assertEqual(self.cart.get_total(), 0)
        self.assertEqual(self.cart.apply_discount(10), 0)


if __name__ == '__main__':
    unittest.main()
```

### Debugging

```python
import requests

url = "http://localhost:8000/task"
data = {
    "task_type": "debugging",
    "code": """
def calculate_average(numbers):
    total = sum(numbers)
    count = len(numbers)
    return total / count

result = calculate_average([])
print(result)
""",
    "prompt": "This code crashes when passed an empty list. Fix it.",
    "language": "python"
}

response = requests.post(url, json=data)
result = requests.get(f"http://localhost:8000/task/{response.json()['task_id']}").json()

print("Debug analysis and fix:")
print(result["result"])
```

**Expected Output:**
```markdown
# Debug Analysis: calculate_average Function

## Problem
The function `calculate_average` crashes with a `ZeroDivisionError` when passed an empty list because it attempts to divide by zero.

## Root Cause
```python
count = len(numbers)  # count = 0 for empty list
return total / count   # ZeroDivisionError: division by zero
```

## Fix
Add a check for empty list at the beginning of the function:

```python
def calculate_average(numbers):
    if not numbers:  # Check for empty list
        return 0.0    # Return 0 or raise an exception
    
    total = sum(numbers)
    count = len(numbers)
    return total / count
```

## Alternative Fix
You could also raise a more descriptive exception:

```python
def calculate_average(numbers):
    if not numbers:
        raise ValueError("Cannot calculate average of empty list")
    
    total = sum(numbers)
    count = len(numbers)
    return total / count
```

## Recommendations
1. Always validate inputs at the beginning of functions
2. Consider what the function should return for edge cases
3. Use type hints to make expected inputs clearer
4. Add docstrings to document behavior

## Improved Version
```python
from typing import List, Union

def calculate_average(numbers: List[Union[int, float]]) -> float:
    """Calculate the average of a list of numbers.
    
    Args:
        numbers: List of numbers to average
    
    Returns:
        The arithmetic mean of the numbers, or 0.0 for empty list
    
    Raises:
        TypeError: If numbers contains non-numeric values
    """
    if not numbers:
        return 0.0
    
    try:
        total = sum(numbers)
        count = len(numbers)
        return total / count
    except TypeError as e:
        raise TypeError("All elements must be numeric") from e
```
```

### Explanation

```python
import requests

url = "http://localhost:8000/task"
data = {
    "task_type": "explanation",
    "prompt": "Explain how Python decorators work with examples",
    "language": "markdown"
}

response = requests.post(url, json=data)
result = requests.get(f"http://localhost:8000/task/{response.json()['task_id']}").json()

print(result["result"])
```

---

## Integration Examples

### FastAPI Integration

```python
from fastapi import FastAPI, HTTPException
import httpx

app = FastAPI()

# Configure OpenCode client
OPENCODE_URL = "http://localhost:8000"
OPENCODE_API_KEY = "your-api-key"


@app.post("/generate")
async def generate_code(prompt: str, language: str = "python"):
    """Generate code using OpenCode Coordinator."""
    async with httpx.AsyncClient() as client:
        # Create task
        response = await client.post(
            f"{OPENCODE_URL}/code/generate",
            headers={"X-API-Key": OPENCODE_API_KEY},
            json={
                "prompt": prompt,
                "language": language,
                "temperature": 0.7
            }
        )
        
        task = response.json()
        task_id = task["task_id"]
        
        # Wait for completion
        while True:
            result = await client.get(
                f"{OPENCODE_URL}/task/{task_id}",
                headers={"X-API-Key": OPENCODE_API_KEY}
            )
            
            data = result.json()
            if data["status"] in ["completed", "failed"]:
                if data["status"] == "failed":
                    raise HTTPException(status_code=500, detail=data["error"])
                return {"result": data["result"]}
            
            await asyncio.sleep(0.5)


@app.post("/validate")
async def validate_code(code: str, language: str = "python"):
    """Validate code using OpenCode Coordinator."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{OPENCODE_URL}/code/validate",
            headers={"X-API-Key": OPENCODE_API_KEY},
            json={
                "code": code,
                "language": language
            }
        )
        
        task = response.json()
        task_id = task["task_id"]
        
        # Wait for validation result
        while True:
            result = await client.get(
                f"{OPENCODE_URL}/task/{task_id}",
                headers={"X-API-Key": OPENCODE_API_KEY}
            )
            
            data = result.json()
            if data["status"] in ["completed", "failed"]:
                if data["status"] == "failed":
                    raise HTTPException(status_code=500, detail=data["error"])
                return {"validation": data["result"]}
            
            await asyncio.sleep(0.5)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
```

### Flask Integration

```python
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

OPENCODE_URL = "http://localhost:8000"
OPENCODE_API_KEY = "your-api-key"


@app.route('/api/generate', methods=['POST'])
def generate():
    """Generate code."""
    data = request.json
    
    # Forward to OpenCode
    response = requests.post(
        f"{OPENCODE_URL}/code/generate",
        headers={"X-API-Key": OPENCODE_API_KEY},
        json=data
    )
    
    task = response.json()
    task_id = task["task_id"]
    
    # Wait for result
    result = requests.get(
        f"{OPENCODE_URL}/task/{task_id}",
        headers={"X-API-Key": OPENCODE_API_KEY}
    ).json()
    
    return jsonify(result)


@app.route('/api/validate', methods=['POST'])
def validate():
    """Validate code."""
    data = request.json
    
    response = requests.post(
        f"{OPENCODE_URL}/code/validate",
        headers={"X-API-Key": OPENCODE_API_KEY},
        json=data
    )
    
    task = response.json()
    task_id = task["task_id"]
    
    result = requests.get(
        f"{OPENCODE_URL}/task/{task_id}",
        headers={"X-API-Key": OPENCODE_API_KEY}
    ).json()
    
    return jsonify(result)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

---

## Best Practices

### Error Handling

```python
import requests
from requests.exceptions import RequestException, Timeout

url = "http://localhost:8000/code/generate"
data = {"prompt": "...", "language": "python"}

try:
    response = requests.post(url, json=data, timeout=30)
    response.raise_for_status()
    task = response.json()
    
    # Get result with retry logic
    max_retries = 5
    retry_delay = 1
    
    for attempt in range(max_retries):
        result = requests.get(
            f"http://localhost:8000/task/{task['task_id']}",
            timeout=30
        ).json()
        
        if result["status"] in ["completed", "failed"]:
            if result["status"] == "failed":
                print(f"Task failed: {result['error']}")
            else:
                print(f"Success: {result['result']}")
            break
        
        if attempt < max_retries - 1:
            time.sleep(retry_delay)
            retry_delay *= 2  # Exponential backoff
    else:
        print("Task timed out")
        
except Timeout:
    print("Request timed out")
except RequestException as e:
    print(f"Request failed: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Caching

```python
import requests
import functools
import time

# Simple cache decorator
cache = {}

def cached_request(timeout=300):
    """Cache request results."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            key = (func.__name__, args, frozenset(kwargs.items()))
            if key in cache:
                result, timestamp = cache[key]
                if time.time() - timestamp < timeout:
                    return result
            
            result = func(*args, **kwargs)
            cache[key] = (result, time.time())
            return result
        return wrapper
    return decorator


@cached_request(timeout=60)
def generate_code(prompt, language="python"):
    """Generate code with caching."""
    url = "http://localhost:8000/execute?wait=true"
    data = {
        "task_type": "code_generation",
        "prompt": prompt,
        "language": language
    }
    
    response = requests.post(url, json=data)
    return response.json()["result"]


# Usage
result1 = generate_code("Create a Python function")  # Makes API call
result2 = generate_code("Create a Python function")  # Returns cached result
```

### Rate Limiting

```python
import requests
import time
from collections import deque

# Rate limiter
class RateLimiter:
    def __init__(self, max_requests, period):
        self.max_requests = max_requests
        self.period = period
        self.requests = deque()
    
    def wait(self):
        """Wait if rate limit is reached."""
        now = time.time()
        
        # Remove old requests
        while self.requests and now - self.requests[0] > self.period:
            self.requests.popleft()
        
        # Check if we can make a request
        if len(self.requests) >= self.max_requests:
            oldest = self.requests[0]
            wait_time = self.period - (now - oldest)
            if wait_time > 0:
                time.sleep(wait_time)
                # Remove the oldest request
                self.requests.popleft()
        
        # Add current request
        self.requests.append(now)


# Create rate limiter: 10 requests per second
limiter = RateLimiter(max_requests=10, period=1)

# Usage
limiter.wait()
response = requests.post("http://localhost:8000/code/generate", json=data)
```

---

## Cost Optimization

### Provider Selection by Cost

```python
import requests

# Get all models and their pricing
models_response = requests.get(
    "http://localhost:8000/models",
    headers={"X-API-Key": "your-api-key"}
)
models = models_response.json()

# Sort by cost (input + output)
sorted_models = sorted(
    models,
    key=lambda m: m['pricing']['input'] + m['pricing']['output']
)

# Use the cheapest model
cheapest_model = sorted_models[0]['id']

# Generate code with cheapest model
url = "http://localhost:8000/code/generate"
data = {
    "prompt": "Create a Python function",
    "language": "python",
    "model_preference": cheapest_model
}

response = requests.post(url, json=data)
```

### Token Estimation

```python
import requests

# Estimate tokens for a prompt
def estimate_tokens(text):
    """Estimate number of tokens in text."""
    # Simple estimation: 4 characters per token
    return len(text) // 4

prompt = "Create a comprehensive REST API with authentication, database integration, and error handling"
estimated_tokens = estimate_tokens(prompt)

print(f"Estimated tokens: {estimated_tokens}")

# Calculate estimated cost
models_response = requests.get("http://localhost:8000/models")
models = models_response.json()

# Find a specific model
model = next(m for m in models if m['id'] == 'gpt-4o')
input_cost_per_1m = model['pricing']['input']
output_cost_per_1m = model['pricing']['output']

# Estimate cost (assuming prompt + response = 2x prompt tokens)
estimated_total_tokens = estimated_tokens * 2
estimated_cost = (estimated_total_tokens / 1_000_000) * (input_cost_per_1m + output_cost_per_1m)

print(f"Estimated cost: ${estimated_cost:.6f}")
```

---

## Monitoring Examples

### Get Statistics

```python
import requests

# Get overall statistics
stats = requests.get(
    "http://localhost:8000/stats",
    headers={"X-API-Key": "your-api-key"}
).json()

print(f"Total tasks: {stats['total_tasks']}")
print(f"Completed: {stats['completed_tasks']}")
print(f"Failed: {stats['failed_tasks']}")
print(f"Total tokens: {stats['total_tokens']}")
print(f"Total cost: ${stats['total_cost']:.2f}")
print(f"Average execution time: {stats['avg_execution_time_ms']:.1f}ms")

# Provider usage
print("\nProvider usage:")
for provider, count in stats['provider_usage'].items():
    print(f"  {provider}: {count} tasks")

# Model usage
print("\nModel usage:")
for model, count in stats['model_usage'].items():
    print(f"  {model}: {count} tasks")
```

### Track Usage Over Time

```python
import requests
import time
from datetime import datetime

# Track usage over time
def track_usage(duration_minutes=5):
    """Track usage over a period of time."""
    end_time = time.time() + duration_minutes * 60
    
    stats = []
    while time.time() < end_time:
        # Get current stats
        response = requests.get(
            "http://localhost:8000/stats",
            headers={"X-API-Key": "your-api-key"}
        )
        current_stats = response.json()
        
        # Record with timestamp
        stats.append({
            "timestamp": datetime.now().isoformat(),
            "total_tasks": current_stats['total_tasks'],
            "total_tokens": current_stats['total_tokens'],
            "total_cost": current_stats['total_cost']
        })
        
        time.sleep(10)  # Check every 10 seconds
    
    # Print results
    for stat in stats:
        print(f"{stat['timestamp']}: {stat['total_tasks']} tasks, "
              f"{stat['total_tokens']} tokens, ${stat['total_cost']:.4f}")


track_usage(5)  # Track for 5 minutes
```

---

## Command Line Tool

Create a simple CLI tool for the OpenCode Coordinator:

```python
#!/usr/bin/env python3
"""OpenCode CLI - A command line interface for the OpenCode Coordinator."""

import argparse
import json
import sys
import requests
from typing import Optional


class OpenCodeCLI:
    def __init__(self, base_url: str, api_key: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.headers = {"Content-Type": "application/json"}
        if api_key:
            self.headers["X-API-Key"] = api_key
    
    def generate(self, prompt: str, language: str = "python", **kwargs):
        """Generate code."""
        url = f"{self.base_url}/code/generate"
        data = {"prompt": prompt, "language": language, **kwargs}
        
        response = requests.post(url, headers=self.headers, json=data)
        response.raise_for_status()
        
        task = response.json()
        task_id = task["task_id"]
        
        # Wait for result
        return self._wait_for_task(task_id)
    
    def validate(self, code: str, language: str = "python", **kwargs):
        """Validate code."""
        url = f"{self.base_url}/code/validate"
        data = {"code": code, "language": language, **kwargs}
        
        response = requests.post(url, headers=self.headers, json=data)
        response.raise_for_status()
        
        task = response.json()
        return self._wait_for_task(task["task_id"])
    
    def format_code(self, code: str, language: str = "python", **kwargs):
        """Format code."""
        url = f"{self.base_url}/code/format"
        data = {"code": code, "language": language, **kwargs}
        
        response = requests.post(url, headers=self.headers, json=data)
        response.raise_for_status()
        
        task = response.json()
        return self._wait_for_task(task["task_id"])
    
    def _wait_for_task(self, task_id: str, timeout: int = 300):
        """Wait for task completion."""
        import time
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            response = requests.get(
                f"{self.base_url}/task/{task_id}",
                headers=self.headers
            )
            response.raise_for_status()
            
            task = response.json()
            if task["status"] in ["completed", "failed"]:
                if task["status"] == "failed":
                    print(f"Error: {task['error']}", file=sys.stderr)
                    sys.exit(1)
                return task["result"]
            
            time.sleep(0.5)
        
        print("Timeout waiting for task", file=sys.stderr)
        sys.exit(1)
    
    def stats(self):
        """Get statistics."""
        response = requests.get(
            f"{self.base_url}/stats",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def providers(self):
        """List providers."""
        response = requests.get(
            f"{self.base_url}/providers",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()


def main():
    parser = argparse.ArgumentParser(
        description="OpenCode CLI - Command line interface for OpenCode Coordinator"
    )
    parser.add_argument(
        "--url",
        default="http://localhost:8000",
        help="Base URL of OpenCode Coordinator"
    )
    parser.add_argument(
        "--api-key",
        default=None,
        help="API key for authentication"
    )
    
    subparsers = parser.add_subparsers(dest="command")
    
    # Generate command
    generate_parser = subparsers.add_parser("generate", help="Generate code")
    generate_parser.add_argument("prompt", help="Prompt for code generation")
    generate_parser.add_argument("--language", default="python", help="Programming language")
    generate_parser.add_argument("--temperature", type=float, default=0.7)
    generate_parser.add_argument("--max-tokens", type=int, default=2000)
    
    # Validate command
    validate_parser = subparsers.add_parser("validate", help="Validate code")
    validate_parser.add_argument("code", help="Code to validate")
    validate_parser.add_argument("--language", default="python", help="Programming language")
    
    # Format command
    format_parser = subparsers.add_parser("format", help="Format code")
    format_parser.add_argument("code", help="Code to format")
    format_parser.add_argument("--language", default="python", help="Programming language")
    
    # Stats command
    subparsers.add_parser("stats", help="Get statistics")
    
    # Providers command
    subparsers.add_parser("providers", help="List providers")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    cli = OpenCodeCLI(args.url, args.api_key)
    
    if args.command == "generate":
        result = cli.generate(
            args.prompt,
            language=args.language,
            temperature=args.temperature,
            max_tokens=args.max_tokens
        )
        print(result)
    elif args.command == "validate":
        result = cli.validate(args.code, language=args.language)
        print(result)
    elif args.command == "format":
        result = cli.format_code(args.code, language=args.language)
        print(result)
    elif args.command == "stats":
        stats = cli.stats()
        print(json.dumps(stats, indent=2))
    elif args.command == "providers":
        providers = cli.providers()
        print(json.dumps(providers, indent=2))


if __name__ == "__main__":
    main()
```

Save as `opencode-cli.py` and make executable:

```bash
chmod +x opencode-cli.py

# Usage examples
./opencode-cli.py --url http://localhost:8000 generate "Create a Python hello world"
./opencode-cli.py --url http://localhost:8000 --api-key your-key validate "def hello(): print('Hello')"
./opencode-cli.py --url http://localhost:8000 stats
./opencode-cli.py --url http://localhost:8000 providers
```

---

## Summary

This document provides comprehensive examples for using the OpenCode AI Coordinator, including:

- **Basic usage** with cURL, Python, JavaScript
- **Code generation** for various languages and use cases
- **Code validation** and formatting
- **Template usage** for consistent code patterns
- **Multi-provider** load balancing and fallback
- **Batch processing** for multiple tasks
- **Webhook integration** for async notifications
- **Advanced use cases** like refactoring, documentation, testing
- **Integration** with FastAPI, Flask, and other frameworks
- **Best practices** for error handling, caching, rate limiting
- **Cost optimization** strategies
- **Monitoring** and statistics tracking
- **Command line tool** for easy access

---

**Happy Coding!** 🎉

For more information, see:
- [QUICK_START.md](QUICK_START.md) - Get started in 5 minutes
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - Complete deployment guide
- [API_DOCUMENTATION.md](API_DOCUMENTATION.md) - Full API reference
