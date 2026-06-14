import pandas as pd
from prophet import Prophet
import os, warnings
warnings.filterwarnings("ignore")

def run_forecast(periods: int = 90) -> pd.DataFrame:
    df = pd.read_csv("data/processed/kpi_summary.csv")
    df["ds"] = pd.to_datetime(df["month"] + "-01")

    results = {}
    for metric in ["occupancy_rate", "adr", "revpar"]:
        ts = df[["ds", metric]].rename(columns={metric: "y"}).dropna()
        m = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=False,
            daily_seasonality=False,
            changepoint_prior_scale=0.1
        )
        m.fit(ts)
        future = m.make_future_dataframe(periods=periods, freq="MS")
        forecast = m.predict(future)
        results[metric] = forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].rename(
            columns={"yhat": metric, "yhat_lower": f"{metric}_low", "yhat_upper": f"{metric}_high"}
        )

    # Merge all forecasts on date
    merged = results["occupancy_rate"]
    for key in ["adr", "revpar"]:
        merged = merged.merge(results[key], on="ds")

    merged.rename(columns={"ds": "date"}, inplace=True)
    os.makedirs("data/processed", exist_ok=True)
    merged.to_csv("data/processed/forecast_output.csv", index=False)
    print(f"✓ Forecast saved ({len(merged)} rows, {periods}-day horizon)")
    return merged

if __name__ == "__main__":
    df = run_forecast(periods=90)
    print(df.tail(6).to_string(index=False))