<div align="center">
<img src="./demo/artifacts/littlelogger-logo.png" alt="LittleLogger Logo">
</div>
A lightweight, zero-setup decorator for logging ML experiments to a JSONL file.

This tool is for the solo data scientist, student, or hobbyist in a Jupyter Notebook who just wants to keep track of their experiments without setting up a database or heavy framework.

### Quick Setup
Get started in 30 seconds.

**1. Install from PyPI:**
```bash
pip install littlelogger
```
**2. Import and use the decorator:**
```python
from littlelogger import log_run

# NOTE: for this to work, we need the training function to input the parameters that need to be logged
# and output the performance metric e.g., f1_score, accuracy_score, etc.
@log_run(log_file="my_experiments.jsonl")
def train_model(learning_rate, n_estimators):
    # Your training logic...
    f1 = 0.80
    return {"f1_score": f1}

# Just run your function as normal
train_model(0.1, 100)
train_model(0.05, 200)
```
**3. Check your results:**
A `my_experiments.jsonl` file will be created, logging every run.

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
from littlelogger import log_run

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

### Analyzing Your Results
You can easily load your results back into pandas to find your best run. The key is using `load_log()` from littlelogger
```python
from littlelogger import load_log

log_df = load_log(PATH_TO_LOG_FILE)

# Find your best run!
log_df.sort_values(by="metric_f1_score", ascending=False)
```

### API Reference
`@log_run(log_file="experiment_log.jsonl")`

This is the main decorator. You place it above your function definition.

**Parameters:**
- `log_file` (str): The path to the `.jsonl` file where logs will be written.
    - Default: `"experiment_log.jsonl"`
    - Behavior: The decorator will append to this file. It does not overwrite.

**What is Logged?**

The decorator will write a single JSON line to the file for each function call, containing:
- `timestamp`: An ISO 8601 formatted UTC timestamp.
- `function_name`: The name of the function that was run (e.g., `train_model`).
- `runtime_seconds`: The execution time of the function (in seconds).
- `params`: A dictionary of all arguments (including defaults) passed to your function.
- `metrics`: The value returned by your function. This is expected to be a dictionary (e.g., `{"f1": 0.8, "accuracy": 0.9}`)

### ⚠️ Important Limitations

This tool is built for simplicity and has intentional trade-offs:

1. Not Thread-Safe: This logger is NOT designed for concurrency. If you run functions in parallel (using `multiprocessing` or `threading` from the same script), they will try to write to the log file at the same time, which will corrupt the file. It is for single-process, iterative experiments only.
2. JSON-Serializable Data Only: The decorator assumes your function arguments and return values are "JSON-serializable" (strings, ints, floats, lists, dicts). If you return a complex object (like a scikit-learn model), the logger will fail to serialize it.
3. Best-Effort Logging (No Retries): If logging fails (due to a non-serializable object or a file permission error), `littlelogger` will not crash your script. It will print a `UserWarning` to your console and let your function return its value, prioritizing your main script's execution over logging.

License & Contributing

-  License: This project is licensed under the MIT License. See the `LICENSE` file for details.
- Contributing: Feel free to open an issue or submit a pull request!
