# Customer segmentation with RFM

This project groups retail customers by recency, order frequency and revenue. It produces four descriptive customer segments and a chart for a business-facing review.

## Run it

The repository can be evaluated without the original dataset:

```bash
cd project
python -m pip install -r requirements.txt
python pipeline.py --generate-demo --output reports
```

For a permitted dataset, supply a CSV containing `CustomerID`, `DAYSSINCELASTORDER`, `TOTAL_ORDERS` and `REVENUE`:

```bash
python pipeline.py --input path/to/sales.csv --output reports
```

Outputs are `customer_segments.csv`, `segment_summary.csv` and `segments.png`. The synthetic dataset is deterministic, so the demonstration is reproducible. Docker starts the same demo pipeline with `docker build -t customer-segmentation project` and `docker run --rm -v ${PWD}/reports:/app/reports customer-segmentation`.

## Scope and interpretation

The original transaction data cannot be published. The included demo is synthetic and exists only to demonstrate the pipeline. The segments are descriptive RFM clusters, not validated churn predictions. A historical churn target and a time-based holdout set would be required before reporting prediction quality.
