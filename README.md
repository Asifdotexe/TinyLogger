<div align="center">
<img src="./demo/artifacts/tinylogger-logo.png" alt="TinyLogger Logo">
</div>
A lightweight, zero-setup decorator for logging ML experiments to a JSONL file.

This tool is for the solo data scientist, student, or hobbyist in a Jupyter Notebook who just wants to keep track of their experiments without setting up a database or heavy framework.

### See it in Action

Want to see how it works? Check out the [Demo Notebook](demo/demo.ipynb) to see a real-world example of logging experiments from different models into one file.

### The Problem
You're tuning a model and your notebook looks like this:
```python
# metrics = train_model(max_depth=5, n_estimators=100) # f1: 0.82
# metrics = train_model(max_depth=7, n_estimators=100) # f1: 0.81
metrics = train_model(max_depth=5, n_estimators=200) # f1: 0.83
print(metrics)
```
A day later, you've lost track of your best run.

### The Solution
Wrap your function with the @log_run decorator.
```python
from tinylogger import log_run

@log_run(log_file="experiment_log.jsonl")
def train_model(max_depth, n_estimators):
    # ... your training logic ...
    f1_score = 0.83 # Your metric
    return {"f1": f1_score}

# Run your experiments
train_model(max_depth=5, n_estimators=100)
train_model(max_depth=7, n_estimators=100)
train_model(max_depth=5, n_estimators=200)
```

This will create a `experiment_log.jsonl` file with one line per experiment:
```python
{"timestamp": "2025-11-01T16:30:00...", "runtime_seconds": 12.3, "params": {"max_depth": 5, "n_estimators": 100}, "metrics": {"f1": 0.82}}
{"timestamp": "2025-11-01T16:32:12...", "runtime_seconds": 14.1, "params": {"max_depth": 7, "n_estimators": 100}, "metrics": {"f1": 0.81}}
{"timestamp": "2025-11-01T16:34:45...", "runtime_seconds": 23.5, "params": {"max_depth": 5, "n_estimators": 200}, "metrics": {"f1": 0.83}}
```

### ⚠️ Important Limitations

This tool is built for simplicity and has intentional trade-offs:

1. Not Thread-Safe: This logger is NOT designed for concurrency. If you run functions in parallel (using multiprocessing or threading), you will corrupt your log file.

2. JSON-Serializable Data Only: The decorator assumes your function arguments and return values are "JSON-serializable" (strings, ints, floats, lists, dicts).
