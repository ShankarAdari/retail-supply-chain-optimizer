"""
Machine Learning Forecasting Module for Supply Chain Optimization

This module provides demand forecasting, inventory optimization, and anomaly detection
using scikit-learn and statistical methods.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import json
import mysql.connector
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import warnings

warnings.filterwarnings('ignore')


class DemandForecaster:
    """Forecasts future demand using machine learning models."""

    def __init__(self, db_config: Dict):
        """Initialize forecaster with database configuration."""
        self.db_config = db_config
        self.models = {}
        self.scalers = {}
        self.feature_importance = {}

    def get_db_connection(self):
        """Create database connection."""
        return mysql.connector.connect(**self.db_config)

    def get_historical_sales(self, store_id: Optional[int] = None, days: int = 365) -> pd.DataFrame:
        """
        Retrieve historical sales data from database.

        Args:
            store_id: Optional store ID to filter by
            days: Number of days of historical data to retrieve

        Returns:
            DataFrame with sales data including date, quantity, price
        """
        conn = self.get_db_connection()
        cursor = conn.cursor(dictionary=True)

        start_date = datetime.now() - timedelta(days=days)

        if store_id:
            query = """
                SELECT s.saleDate, s.quantity, s.salePrice, s.totalRevenue, p.category, st.storeCode
                FROM sales s
                JOIN products p ON s.productId = p.id
                JOIN stores st ON s.storeId = st.id
                WHERE s.storeId = %s AND s.saleDate >= %s
                ORDER BY s.saleDate
            """
            cursor.execute(query, (store_id, start_date))
        else:
            query = """
                SELECT s.saleDate, s.quantity, s.salePrice, s.totalRevenue, p.category, st.storeCode
                FROM sales s
                JOIN products p ON s.productId = p.id
                JOIN stores st ON s.storeId = st.id
                WHERE s.saleDate >= %s
                ORDER BY s.saleDate
            """
            cursor.execute(query, (start_date,))

        data = cursor.fetchall()
        cursor.close()
        conn.close()

        df = pd.DataFrame(data)
        if df.empty:
            return df

        df['saleDate'] = pd.to_datetime(df['saleDate'])
        df = df.sort_values('saleDate')

        return df

    def create_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create time-series features for ML model.

        Features include:
        - Day of week, month, quarter, year
        - Lag features (previous day, week, month sales)
        - Rolling averages and standard deviations
        - Seasonal indicators
        """
        df = df.copy()
        df['date'] = pd.to_datetime(df['saleDate'])

        # Temporal features
        df['day_of_week'] = df['date'].dt.dayofweek
        df['month'] = df['date'].dt.month
        df['quarter'] = df['date'].dt.quarter
        df['day_of_month'] = df['date'].dt.day
        df['week_of_year'] = df['date'].dt.isocalendar().week

        # Aggregate daily sales
        daily_sales = df.groupby('date').agg({
            'quantity': 'sum',
            'totalRevenue': 'sum'
        }).reset_index()

        # Lag features
        daily_sales['quantity_lag1'] = daily_sales['quantity'].shift(1)
        daily_sales['quantity_lag7'] = daily_sales['quantity'].shift(7)
        daily_sales['quantity_lag30'] = daily_sales['quantity'].shift(30)

        # Rolling statistics
        daily_sales['quantity_rolling_mean_7'] = daily_sales['quantity'].rolling(window=7).mean()
        daily_sales['quantity_rolling_std_7'] = daily_sales['quantity'].rolling(window=7).std()
        daily_sales['quantity_rolling_mean_30'] = daily_sales['quantity'].rolling(window=30).mean()

        # Seasonal decomposition
        daily_sales['day_of_week'] = daily_sales['date'].dt.dayofweek
        daily_sales['month'] = daily_sales['date'].dt.month
        daily_sales['quarter'] = daily_sales['date'].dt.quarter

        # Fill NaN values
        daily_sales = daily_sales.fillna(method='bfill').fillna(method='ffill')

        return daily_sales

    def train_model(self, df: pd.DataFrame, model_type: str = 'gradient_boosting') -> Tuple[object, float]:
        """
        Train demand forecasting model.

        Args:
            df: DataFrame with features and target
            model_type: Type of model ('gradient_boosting' or 'random_forest')

        Returns:
            Tuple of (trained model, R2 score)
        """
        # Prepare features and target
        feature_cols = [
            'quantity_lag1', 'quantity_lag7', 'quantity_lag30',
            'quantity_rolling_mean_7', 'quantity_rolling_std_7',
            'quantity_rolling_mean_30', 'day_of_week', 'month', 'quarter'
        ]

        X = df[feature_cols].fillna(0)
        y = df['quantity']

        # Remove rows with NaN
        mask = ~(X.isna().any(axis=1) | y.isna())
        X = X[mask]
        y = y[mask]

        if len(X) < 100:
            raise ValueError("Insufficient data for model training")

        # Split data
        train_size = int(len(X) * 0.8)
        X_train, X_test = X[:train_size], X[train_size:]
        y_train, y_test = y[:train_size], y[train_size:]

        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        # Train model
        if model_type == 'gradient_boosting':
            model = GradientBoostingRegressor(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=5,
                random_state=42
            )
        else:
            model = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42
            )

        model.fit(X_train_scaled, y_train)

        # Evaluate
        y_pred = model.predict(X_test_scaled)
        r2 = r2_score(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))

        self.scalers['demand'] = scaler
        self.feature_importance['demand'] = dict(zip(feature_cols, model.feature_importances_))

        return model, {'r2': r2, 'mae': mae, 'rmse': rmse}

    def forecast_demand(self, model: object, df: pd.DataFrame, days_ahead: int = 30) -> List[Dict]:
        """
        Generate demand forecast for future days.

        Args:
            model: Trained forecasting model
            df: Historical data with features
            days_ahead: Number of days to forecast

        Returns:
            List of forecast dictionaries with date and predicted quantity
        """
        forecasts = []
        current_data = df.tail(30).copy()

        feature_cols = [
            'quantity_lag1', 'quantity_lag7', 'quantity_lag30',
            'quantity_rolling_mean_7', 'quantity_rolling_std_7',
            'quantity_rolling_mean_30', 'day_of_week', 'month', 'quarter'
        ]

        for i in range(days_ahead):
            # Prepare features for next day
            next_date = current_data['date'].max() + timedelta(days=1)

            features = {
                'quantity_lag1': current_data['quantity'].iloc[-1],
                'quantity_lag7': current_data['quantity'].iloc[-7] if len(current_data) >= 7 else current_data['quantity'].mean(),
                'quantity_lag30': current_data['quantity'].iloc[-30] if len(current_data) >= 30 else current_data['quantity'].mean(),
                'quantity_rolling_mean_7': current_data['quantity'].tail(7).mean(),
                'quantity_rolling_std_7': current_data['quantity'].tail(7).std(),
                'quantity_rolling_mean_30': current_data['quantity'].tail(30).mean(),
                'day_of_week': next_date.dayofweek,
                'month': next_date.month,
                'quarter': next_date.quarter
            }

            X_new = np.array([features[col] for col in feature_cols]).reshape(1, -1)
            X_new_scaled = self.scalers['demand'].transform(X_new)

            predicted_quantity = model.predict(X_new_scaled)[0]
            predicted_quantity = max(0, predicted_quantity)  # Ensure non-negative

            forecasts.append({
                'date': next_date.isoformat(),
                'predicted_quantity': float(predicted_quantity),
                'confidence_interval_lower': float(predicted_quantity * 0.8),
                'confidence_interval_upper': float(predicted_quantity * 1.2)
            })

            # Update current data with prediction
            new_row = pd.DataFrame([{
                'date': next_date,
                'quantity': predicted_quantity,
                'quantity_lag1': current_data['quantity'].iloc[-1],
                'quantity_lag7': current_data['quantity'].iloc[-7] if len(current_data) >= 7 else current_data['quantity'].mean(),
                'quantity_lag30': current_data['quantity'].iloc[-30] if len(current_data) >= 30 else current_data['quantity'].mean(),
                'quantity_rolling_mean_7': current_data['quantity'].tail(7).mean(),
                'quantity_rolling_std_7': current_data['quantity'].tail(7).std(),
                'quantity_rolling_mean_30': current_data['quantity'].tail(30).mean(),
                'day_of_week': next_date.dayofweek,
                'month': next_date.month,
                'quarter': next_date.quarter
            }])

            current_data = pd.concat([current_data, new_row], ignore_index=True)

        return forecasts

    def detect_anomalies(self, df: pd.DataFrame, threshold: float = 2.5) -> List[Dict]:
        """
        Detect anomalies in sales data using statistical methods.

        Args:
            df: Historical sales data
            threshold: Standard deviation threshold for anomaly detection

        Returns:
            List of anomalies with dates and details
        """
        daily_sales = df.groupby('date')['quantity'].sum().reset_index()
        daily_sales['date'] = pd.to_datetime(daily_sales['date'])

        # Calculate rolling statistics
        daily_sales['mean'] = daily_sales['quantity'].rolling(window=30).mean()
        daily_sales['std'] = daily_sales['quantity'].rolling(window=30).std()

        # Detect anomalies
        daily_sales['z_score'] = np.abs((daily_sales['quantity'] - daily_sales['mean']) / daily_sales['std'])
        anomalies = daily_sales[daily_sales['z_score'] > threshold].copy()

        anomaly_list = []
        for _, row in anomalies.iterrows():
            anomaly_list.append({
                'date': row['date'].isoformat(),
                'quantity': float(row['quantity']),
                'expected_quantity': float(row['mean']),
                'deviation': float(row['quantity'] - row['mean']),
                'z_score': float(row['z_score']),
                'severity': 'high' if row['z_score'] > 3 else 'medium'
            })

        return anomaly_list

    def optimize_inventory(self, df: pd.DataFrame, holding_cost: float = 0.1, stockout_cost: float = 50) -> Dict:
        """
        Calculate optimal inventory levels using economic order quantity (EOQ).

        Args:
            df: Historical sales data
            holding_cost: Cost to hold one unit per day
            stockout_cost: Cost of stockout per unit

        Returns:
            Dictionary with optimal inventory parameters
        """
        daily_sales = df.groupby('date')['quantity'].sum()
        daily_demand = daily_sales.mean()
        demand_std = daily_sales.std()

        # Lead time (assuming 7 days)
        lead_time = 7
        lead_time_demand = daily_demand * lead_time
        lead_time_std = demand_std * np.sqrt(lead_time)

        # Safety stock (95% service level = 1.645 * std)
        safety_stock = 1.645 * lead_time_std

        # Reorder point
        reorder_point = lead_time_demand + safety_stock

        # Economic Order Quantity (EOQ)
        # Simplified: EOQ = sqrt(2 * D * S / H)
        # D = annual demand, S = ordering cost, H = holding cost
        annual_demand = daily_demand * 365
        ordering_cost = 100  # Fixed ordering cost
        eoq = np.sqrt(2 * annual_demand * ordering_cost / (holding_cost * 365))

        return {
            'daily_demand': float(daily_demand),
            'demand_std': float(demand_std),
            'reorder_point': float(reorder_point),
            'safety_stock': float(safety_stock),
            'economic_order_quantity': float(eoq),
            'lead_time_days': lead_time,
            'service_level': 0.95
        }

    def save_forecasts_to_db(self, store_id: int, forecasts: List[Dict]):
        """Save forecasts to database."""
        conn = self.get_db_connection()
        cursor = conn.cursor()

        for forecast in forecasts:
            query = """
                INSERT INTO forecasts (storeId, productId, forecastDate, predictedDemand, confidence, forecastMethod)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    predictedDemand = VALUES(predictedDemand),
                    confidence = VALUES(confidence)
            """
            cursor.execute(query, (
                store_id,
                None,  # Product ID (can be extended)
                forecast['date'],
                forecast['predicted_quantity'],
                0.85,  # Confidence level
                'gradient_boosting'
            ))

        conn.commit()
        cursor.close()
        conn.close()

    def generate_recommendations(self, store_id: int, forecasts: List[Dict], inventory_params: Dict) -> List[Dict]:
        """
        Generate actionable recommendations based on forecasts and inventory optimization.

        Args:
            store_id: Store ID
            forecasts: Demand forecasts
            inventory_params: Inventory optimization parameters

        Returns:
            List of recommendations
        """
        recommendations = []

        # Check for high demand periods
        avg_forecast = np.mean([f['predicted_quantity'] for f in forecasts])
        max_forecast = max([f['predicted_quantity'] for f in forecasts])

        if max_forecast > avg_forecast * 1.5:
            recommendations.append({
                'type': 'high_demand_alert',
                'severity': 'high',
                'message': f'High demand period detected. Increase inventory by {int((max_forecast - avg_forecast) / avg_forecast * 100)}%',
                'action': 'Increase orders to suppliers',
                'priority': 1
            })

        # Check for low demand periods
        min_forecast = min([f['predicted_quantity'] for f in forecasts])
        if min_forecast < avg_forecast * 0.5:
            recommendations.append({
                'type': 'low_demand_alert',
                'severity': 'medium',
                'message': f'Low demand period detected. Consider promotional activities.',
                'action': 'Plan promotional campaigns',
                'priority': 2
            })

        # Inventory optimization recommendations
        recommendations.append({
            'type': 'inventory_optimization',
            'severity': 'info',
            'message': f'Optimal reorder point: {int(inventory_params["reorder_point"])} units',
            'action': f'Maintain safety stock of {int(inventory_params["safety_stock"])} units',
            'priority': 3
        })

        return recommendations


def run_forecasting_pipeline(db_config: Dict):
    """
    Run complete forecasting pipeline for all stores.

    Args:
        db_config: Database configuration dictionary
    """
    print("Starting forecasting pipeline...")

    forecaster = DemandForecaster(db_config)

    # Get all stores
    conn = forecaster.get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, storeName FROM stores LIMIT 10")
    stores = cursor.fetchall()
    cursor.close()
    conn.close()

    for store in stores:
        store_id = store['id']
        store_name = store['storeName']

        print(f"\nProcessing store: {store_name} (ID: {store_id})")

        try:
            # Get historical data
            df = forecaster.get_historical_sales(store_id=store_id, days=365)

            if df.empty or len(df) < 100:
                print(f"  Insufficient data for store {store_id}")
                continue

            # Create features
            df_features = forecaster.create_features(df)

            # Train model
            model, metrics = forecaster.train_model(df_features)
            print(f"  Model trained - R2: {metrics['r2']:.3f}, MAE: {metrics['mae']:.2f}, RMSE: {metrics['rmse']:.2f}")

            # Generate forecasts
            forecasts = forecaster.forecast_demand(model, df_features, days_ahead=30)
            print(f"  Generated {len(forecasts)} day forecasts")

            # Detect anomalies
            anomalies = forecaster.detect_anomalies(df)
            print(f"  Detected {len(anomalies)} anomalies")

            # Optimize inventory
            inventory_params = forecaster.optimize_inventory(df)
            print(f"  Inventory optimization - Reorder point: {inventory_params['reorder_point']:.0f} units")

            # Generate recommendations
            recommendations = forecaster.generate_recommendations(store_id, forecasts, inventory_params)
            print(f"  Generated {len(recommendations)} recommendations")

            # Save forecasts to database
            forecaster.save_forecasts_to_db(store_id, forecasts)

        except Exception as e:
            print(f"  Error processing store {store_id}: {str(e)}")

    print("\nForecasting pipeline completed!")


if __name__ == "__main__":
    db_config = {
        'host': 'localhost',
        'user': 'root',
        'password': '',
        'database': 'retail_supply_chain'
    }

    run_forecasting_pipeline(db_config)
