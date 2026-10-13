FROM python:3.12-slim
WORKDIR \python_project
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "data_cleaning_ion.py","EDA_jan.py","revenue_masha.py", "RFM_calculation.py", "rfm_churn_model_quintiles.py","visualization.py", "hourly_rev_ion.py" ]
