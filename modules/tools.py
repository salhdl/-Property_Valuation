from agno.tools import tool
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json


@tool(
    name="mls_integration",
    description="Access Multiple Listing Service data for property information and comparable sales",
    show_result=True,
)
def mls_integration(
    property_address: str,
    property_type: str = "residential",
    search_radius: float = 0.5,
    days_back: int = 365,
    min_sqft: Optional[int] = None,
    max_sqft: Optional[int] = None,
    min_bedrooms: Optional[int] = None,
    max_bedrooms: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Access MLS data for property information and comparable sales analysis.
    
    Args:
        property_address: Address of the subject property
        property_type: Type of property (residential/commercial/land)
        search_radius: Search radius in miles
        days_back: Number of days back to search for sales
        min_sqft: Minimum square footage filter
        max_sqft: Maximum square footage filter
        min_bedrooms: Minimum number of bedrooms
        max_bedrooms: Maximum number of bedrooms
        
    Returns:
        Dictionary containing MLS data and comparable sales
    """
    # Simulated MLS data - in production, this would connect to actual MLS API
    comparable_sales = [
        {
            "address": "123 Main St, Sample City, ST 12345",
            "sale_price": 450000,
            "sale_date": "2024-01-15",
            "sqft": 2200,
            "bedrooms": 3,
            "bathrooms": 2.5,
            "lot_size": 0.25,
            "year_built": 2010,
            "condition": "Good",
            "days_on_market": 45,
            "price_per_sqft": 204.55
        },
        {
            "address": "456 Oak Ave, Sample City, ST 12345",
            "sale_price": 485000,
            "sale_date": "2024-02-20",
            "sqft": 2400,
            "bedrooms": 4,
            "bathrooms": 3,
            "lot_size": 0.3,
            "year_built": 2015,
            "condition": "Excellent",
            "days_on_market": 28,
            "price_per_sqft": 202.08
        },
        {
            "address": "789 Pine Rd, Sample City, ST 12345",
            "sale_price": 420000,
            "sale_date": "2023-12-10",
            "sqft": 2000,
            "bedrooms": 3,
            "bathrooms": 2,
            "lot_size": 0.2,
            "year_built": 2008,
            "condition": "Fair",
            "days_on_market": 67,
            "price_per_sqft": 210.00
        }
    ]
    
    # Filter comparables based on criteria
    filtered_comps = []
    for comp in comparable_sales:
        if min_sqft and comp["sqft"] < min_sqft:
            continue
        if max_sqft and comp["sqft"] > max_sqft:
            continue
        if min_bedrooms and comp["bedrooms"] < min_bedrooms:
            continue
        if max_bedrooms and comp["bedrooms"] > max_bedrooms:
            continue
        filtered_comps.append(comp)
    
    # Calculate market statistics
    if filtered_comps:
        avg_price_per_sqft = sum(comp["price_per_sqft"] for comp in filtered_comps) / len(filtered_comps)
        avg_days_on_market = sum(comp["days_on_market"] for comp in filtered_comps) / len(filtered_comps)
        price_range = {
            "min": min(comp["sale_price"] for comp in filtered_comps),
            "max": max(comp["sale_price"] for comp in filtered_comps),
            "median": sorted([comp["sale_price"] for comp in filtered_comps])[len(filtered_comps)//2]
        }
    else:
        avg_price_per_sqft = 0
        avg_days_on_market = 0
        price_range = {"min": 0, "max": 0, "median": 0}
    
    return {
        "subject_property": {
            "address": property_address,
            "property_type": property_type,
            "search_criteria": {
                "radius_miles": search_radius,
                "days_back": days_back,
                "sqft_range": [min_sqft, max_sqft],
                "bedroom_range": [min_bedrooms, max_bedrooms]
            }
        },
        "comparable_sales": filtered_comps,
        "market_statistics": {
            "total_comparables": len(filtered_comps),
            "average_price_per_sqft": round(avg_price_per_sqft, 2),
            "average_days_on_market": round(avg_days_on_market, 1),
            "price_range": price_range
        },
        "analysis_date": datetime.now().isoformat()
    }


@tool(
    name="avm_engine",
    description="Automated Valuation Model for property pricing using multiple methodologies",
    show_result=True,
)
def avm_engine(
    property_address: str,
    property_sqft: int,
    bedrooms: int,
    bathrooms: float,
    lot_size: float,
    year_built: int,
    condition: str,
    comparable_sales: List[Dict[str, Any]],
    market_trend: float = 0.02,
) -> Dict[str, Any]:
    """
    Automated Valuation Model for property pricing using multiple methodologies.
    
    Args:
        property_address: Address of the subject property
        property_sqft: Square footage of the property
        bedrooms: Number of bedrooms
        bathrooms: Number of bathrooms
        lot_size: Lot size in acres
        year_built: Year the property was built
        condition: Property condition (Excellent/Good/Fair/Poor)
        comparable_sales: List of comparable sales data
        market_trend: Market appreciation rate (decimal)
        
    Returns:
        Dictionary containing AVM valuation results
    """
    if not comparable_sales:
        return {"error": "No comparable sales data provided"}
    
    # Extract comparable data with error handling
    try:
        comp_prices = [comp.get("sale_price", 0) for comp in comparable_sales]
        comp_sqft = [comp.get("sqft", 0) for comp in comparable_sales]
        
        # Handle sale dates with different formats
        comp_dates = []
        for comp in comparable_sales:
            sale_date = comp.get("sale_date")
            if sale_date:
                try:
                    if isinstance(sale_date, str):
                        comp_dates.append(datetime.strptime(sale_date, "%Y-%m-%d"))
                    else:
                        comp_dates.append(sale_date)
                except ValueError:
                    # Try alternative date format
                    try:
                        comp_dates.append(datetime.strptime(sale_date, "%m/%d/%Y"))
                    except ValueError:
                        comp_dates.append(datetime.now())  # Default to current date
            else:
                comp_dates.append(datetime.now())  # Default to current date
        
        # Method 1: Price per Square Foot
        price_per_sqft_values = []
        for comp in comparable_sales:
            if comp.get("price_per_sqft"):
                price_per_sqft_values.append(comp["price_per_sqft"])
            elif comp.get("sale_price") and comp.get("sqft"):
                price_per_sqft_values.append(comp["sale_price"] / comp["sqft"])
        
        if not price_per_sqft_values:
            return {"error": "No valid price per square foot data available"}
            
        avg_price_per_sqft = sum(price_per_sqft_values) / len(price_per_sqft_values)
        
    except Exception as e:
        return {"error": f"Error processing comparable sales data: {str(e)}"}
    
    # Adjust for condition
    condition_multipliers = {
        "Excellent": 1.1,
        "Good": 1.0,
        "Fair": 0.9,
        "Poor": 0.8
    }
    condition_adj = condition_multipliers.get(condition, 1.0)
    
    # Adjust for age
    current_year = datetime.now().year
    age = current_year - year_built
    age_adj = max(0.85, 1.0 - (age * 0.005))  # 0.5% depreciation per year, minimum 85%
    avg_days_since_sale = 0.0
    # Adjust for market trend with error handling
    if comp_dates:
        days_since_sale = [(datetime.now() - date).days for date in comp_dates]
        avg_days_since_sale = sum(days_since_sale) / len(days_since_sale)
        market_adj = (1 + market_trend) ** (avg_days_since_sale / 365)
    else:
        market_adj = 1.0  # No adjustment if no date data
    
    # Calculate price per sqft valuation
    price_per_sqft_valuation = property_sqft * avg_price_per_sqft * condition_adj * age_adj * market_adj
    
    # Method 2: Regression Analysis (simplified)
    # Create features matrix with error handling
    features = []
    for comp in comparable_sales:
        features.append([
            comp.get("sqft", 0),
            comp.get("bedrooms", 0),
            comp.get("bathrooms", 0),
            comp.get("lot_size", 0),
            current_year - comp.get("year_built", current_year)
        ])
    
    # Simple linear regression coefficients (in production, use sklearn)
    coefficients = [150, 5000, 10000, 20000, -500]  # [sqft, bedrooms, bathrooms, lot_size, age]
    intercept = 50000
    
    # Calculate regression valuation
    subject_features = [property_sqft, bedrooms, bathrooms, lot_size, age]
    regression_valuation = intercept + sum(coef * feature for coef, feature in zip(coefficients, subject_features))
    
    # Method 3: Comparable Sales Adjustment
    adjusted_comps = []
    for comp in comparable_sales:
        # Adjust for differences with error handling
        comp_sqft = comp.get("sqft", 0)
        comp_bedrooms = comp.get("bedrooms", 0)
        comp_bathrooms = comp.get("bathrooms", 0)
        comp_lot_size = comp.get("lot_size", 0)
        comp_year_built = comp.get("year_built", current_year)
        comp_sale_price = comp.get("sale_price", 0)
        
        sqft_diff = (property_sqft - comp_sqft) * avg_price_per_sqft
        bedroom_diff = (bedrooms - comp_bedrooms) * 5000
        bathroom_diff = (bathrooms - comp_bathrooms) * 10000
        lot_diff = (lot_size - comp_lot_size) * 20000
        age_diff = (age - (current_year - comp_year_built)) * -500
        
        adjusted_price = comp_sale_price + sqft_diff + bedroom_diff + bathroom_diff + lot_diff + age_diff
        adjusted_comps.append(adjusted_price)
    
    # Calculate adjusted sales valuation with error handling
    if adjusted_comps:
        adjusted_sales_valuation = sum(adjusted_comps) / len(adjusted_comps)
    else:
        adjusted_sales_valuation = price_per_sqft_valuation  # Fallback to price per sqft
    
    # Final valuation (weighted average)
    final_valuation = (
        price_per_sqft_valuation * 0.4 +
        regression_valuation * 0.3 +
        adjusted_sales_valuation * 0.3
    )
    
    # Confidence score based on data quality
    confidence_factors = []
    if len(comparable_sales) >= 3:
        confidence_factors.append(0.3)
    if avg_days_since_sale and avg_days_since_sale < 180:

        confidence_factors.append(0.2)
    if len([comp for comp in comparable_sales if abs(comp["sqft"] - property_sqft) / property_sqft < 0.2]) >= 2:
        confidence_factors.append(0.3)
    if len([comp for comp in comparable_sales if comp["bedrooms"] == bedrooms]) >= 1:
        confidence_factors.append(0.2)
    
    confidence_score = sum(confidence_factors)
    
    return {
        "subject_property": {
            "address": property_address,
            "sqft": property_sqft,
            "bedrooms": bedrooms,
            "bathrooms": bathrooms,
            "lot_size": lot_size,
            "year_built": year_built,
            "condition": condition
        },
        "valuation_methods": {
            "price_per_sqft": {
                "value": round(price_per_sqft_valuation, 2),
                "price_per_sqft": round(avg_price_per_sqft, 2),
                "adjustments": {
                    "condition": condition_adj,
                    "age": age_adj,
                    "market_trend": market_adj
                }
            },
            "regression_analysis": {
                "value": round(regression_valuation, 2),
                "coefficients": coefficients,
                "intercept": intercept
            },
            "adjusted_comparables": {
                "value": round(adjusted_sales_valuation, 2),
                "adjusted_prices": [round(price, 2) for price in adjusted_comps]
            }
        },
        "final_valuation": {
            "value": round(final_valuation, 2),
            "confidence_score": round(confidence_score, 2),
            "valuation_date": datetime.now().isoformat(),
            "methodology": "Weighted average of three methods"
        },
        "market_conditions": {
            "trend": market_trend,
            "avg_days_since_sale": round(avg_days_since_sale, 1),
            "comparable_count": len(comparable_sales)
        }
    }


from typing import Any, Dict, List, Optional
import numpy as np
from datetime import datetime, timedelta

def _to_py(obj: Any) -> Any:
    """Convertit récursivement numpy -> types Python (float/int/list/dict)."""
    if isinstance(obj, np.floating):
        return float(obj)
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, list):
        return [_to_py(x) for x in obj]
    if isinstance(obj, dict):
        return {str(k): _to_py(v) for k, v in obj.items()}
    return obj

@tool(
    name="market_trend_analyzer",
    description="Analyze market trends and seasonal patterns for property valuation",
    show_result=True,
)
def market_trend_analyzer(
    location: str,
    property_type: str = "residential",
    analysis_period: int = 24,
    include_seasonal: bool = True,
) -> Dict[str, Any]:
    current_date = datetime.now()

    # --- données simulées ---
    base_price = 400000
    price_data: List[Dict[str, Any]] = []
    seasonal_factors = [0.95, 0.92, 0.98, 1.05, 1.08, 1.10, 1.12, 1.08, 1.05, 1.02, 0.98, 0.95]

    for i in range(analysis_period):
        month_date = current_date - timedelta(days=30 * i)
        month_idx = month_date.month - 1

        trend_factor = (1.02) ** (i / 12.0)
        seasonal_factor = seasonal_factors[month_idx] if include_seasonal else 1.0
        random_factor = np.random.normal(1.0, 0.02)

        price = base_price * trend_factor * seasonal_factor * random_factor
        price_data.append({
            "date": month_date.strftime("%Y-%m"),
            "price": float(round(price, 2)),
            "price_index": float(round((price / base_price) * 100.0, 2)),
        })

    # — calculs linéaires
    prices = [p["price"] for p in price_data]
    x = np.arange(len(prices))
    y = np.array(prices, dtype=float)
    slope, intercept = np.polyfit(x, y, 1)

    monthly_growth = float(slope / float(np.mean(prices)))
    annual_growth = float(monthly_growth * 12.0)

    returns = [(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices))]
    volatility = float(np.std(returns) * np.sqrt(12.0)) if returns else 0.0

    seasonal_analysis: Dict[int, Dict[str, Any]] = {}
    if include_seasonal:
        monthly_avg: Dict[int, List[float]] = {}
        for d in price_data:
            m = int(datetime.strptime(d["date"], "%Y-%m").month)
            monthly_avg.setdefault(m, []).append(float(d["price_index"]))
        for m, indices in monthly_avg.items():
            seasonal_analysis[m] = {
                "month_name": datetime(2024, m, 1).strftime("%B"),
                "avg_index": float(round(np.mean(indices), 2)),
                "volatility": float(round(np.std(indices), 2)),
            }

    cycle_phase = "Expansion" if annual_growth > 0.03 else ("Stable" if annual_growth > 0 else "Contraction")

    result = {
        "location": location,
        "property_type": property_type,
        "analysis_period": f"{analysis_period} months",
        "analysis_date": current_date.isoformat(),
        "price_trend": {
            "slope": float(round(slope, 2)),
            "intercept": float(round(intercept, 2)),
            "monthly_growth_rate": float(round(monthly_growth * 100.0, 3)),
            "annual_growth_rate": float(round(annual_growth * 100.0, 2)),
            "volatility": float(round(volatility * 100.0, 2)),
        },
        "market_cycle": {
            "phase": cycle_phase,
            "growth_rate": float(round(annual_growth * 100.0, 2)),
            "volatility_level": "High" if volatility > 0.15 else ("Medium" if volatility > 0.10 else "Low"),
        },
        "price_data": price_data[-12:],
        "seasonal_analysis": seasonal_analysis,
        "forecast": {
            "next_3_months": float(round(prices[-1] * (1 + monthly_growth * 3), 2)),
            "next_6_months": float(round(prices[-1] * (1 + monthly_growth * 6), 2)),
            "next_12_months": float(round(prices[-1] * (1 + annual_growth), 2)),
        }
    }

    # <<< conversion finale JSON-safe >>>
    return _to_py(result)



@tool(
    name="market_monitor",
    description="Monitor real-time market developments and risk signals",
    show_result=True,
)
def market_monitor(
    location: str,
    monitor_types: List[str] = ["economic", "development", "regulatory"],
    alert_threshold: float = 0.05,
) -> Dict[str, Any]:
    """
    Monitor real-time market developments and risk signals.
    
    Args:
        location: Geographic location to monitor
        monitor_types: Types of monitoring (economic, development, regulatory, demographic)
        alert_threshold: Threshold for generating alerts (5% change)
        
    Returns:
        Dictionary containing market monitoring results and alerts
    """
    current_date = datetime.now()
    
    # Simulated monitoring data
    monitoring_results = {
        "economic": {
            "unemployment_rate": 3.8,
            "gdp_growth": 2.1,
            "inflation_rate": 2.5,
            "interest_rates": 5.25,
            "consumer_confidence": 108.5,
            "status": "Stable",
            "alerts": []
        },
        "development": {
            "new_construction_permits": 45,
            "commercial_development": 3,
            "infrastructure_projects": 2,
            "zoning_changes": 1,
            "status": "Active",
            "alerts": [
                {
                    "type": "New Development",
                    "description": "New shopping center approved in downtown area",
                    "impact": "Positive",
                    "date": "2024-01-15"
                }
            ]
        },
        "regulatory": {
            "property_tax_changes": 0.0,
            "zoning_updates": 1,
            "building_code_changes": 0,
            "environmental_regulations": 0,
            "status": "Stable",
            "alerts": []
        },
        "demographic": {
            "population_growth": 1.2,
            "median_income_change": 3.5,
            "age_demographics": "Aging",
            "migration_patterns": "Inbound",
            "status": "Growing",
            "alerts": []
        }
    }
    
    # Risk assessment
    risk_factors = []
    risk_score = 0
    
    # Economic risks
    if monitoring_results["economic"]["unemployment_rate"] > 5.0:
        risk_factors.append("High unemployment rate")
        risk_score += 0.3
    if monitoring_results["economic"]["interest_rates"] > 6.0:
        risk_factors.append("High interest rates")
        risk_score += 0.2
    
    # Development risks
    if monitoring_results["development"]["new_construction_permits"] > 50:
        risk_factors.append("High construction activity - potential oversupply")
        risk_score += 0.2
    
    # Regulatory risks
    if monitoring_results["regulatory"]["property_tax_changes"] > 0.05:
        risk_factors.append("Significant property tax increase")
        risk_score += 0.3
    
    # Market signals
    market_signals = {
        "inventory_levels": "Low",  # Low/Medium/High
        "days_on_market": 28,
        "price_reductions": 15,
        "new_listings": 120,
        "pending_sales": 95,
        "absorption_rate": 0.79  # Pending/New listings
    }
    
    # Generate alerts based on threshold
    alerts = []
    for monitor_type in monitor_types:
        if monitor_type in monitoring_results:
            for alert in monitoring_results[monitor_type].get("alerts", []):
                alerts.append({
                    "category": monitor_type.title(),
                    "type": alert["type"],
                    "description": alert["description"],
                    "impact": alert["impact"],
                    "date": alert["date"],
                    "severity": "High" if alert["impact"] == "Negative" else "Medium"
                })
    
    # Overall market health
    health_score = 100 - (risk_score * 100)
    if health_score >= 80:
        health_status = "Excellent"
    elif health_score >= 60:
        health_status = "Good"
    elif health_score >= 40:
        health_status = "Fair"
    else:
        health_status = "Poor"
    
    return {
        "location": location,
        "monitoring_date": current_date.isoformat(),
        "monitored_categories": monitor_types,
        "monitoring_results": {k: v for k, v in monitoring_results.items() if k in monitor_types},
        "risk_assessment": {
            "risk_score": round(risk_score, 2),
            "risk_factors": risk_factors,
            "overall_risk": "Low" if risk_score < 0.3 else "Medium" if risk_score < 0.6 else "High"
        },
        "market_signals": market_signals,
        "alerts": alerts,
        "market_health": {
            "score": round(health_score, 1),
            "status": health_status,
            "recommendation": "Monitor closely" if health_score < 60 else "Continue monitoring"
        }
    }


@tool(
    name="comps_analyzer",
    description="Analyze comparable sales and generate adjustment factors",
    show_result=True,
)
def comps_analyzer(
    subject_property: Dict[str, Any],
    comparable_sales: List[Dict[str, Any]],
    adjustment_factors: Optional[Dict[str, float]] = None,
) -> Dict[str, Any]:
    """
    Analyze comparable sales and generate adjustment factors for property valuation.
    
    Args:
        subject_property: Subject property characteristics
        comparable_sales: List of comparable sales data
        adjustment_factors: Custom adjustment factors (optional)
        
    Returns:
        Dictionary containing comparable sales analysis and adjustments
    """
    if not comparable_sales:
        return {"error": "No comparable sales provided"}
    
    # Default adjustment factors
    default_factors = {
        "sqft": 150,  # per sqft
        "bedroom": 5000,  # per bedroom
        "bathroom": 10000,  # per bathroom
        "lot_size": 20000,  # per acre
        "age": -500,  # per year
        "condition": {"Excellent": 0.1, "Good": 0.0, "Fair": -0.1, "Poor": -0.2},
        "garage": 5000,  # per garage space
        "pool": 15000,  # pool presence
        "view": 10000,  # view premium
    }
    
    factors = adjustment_factors or default_factors
    
    # Analyze each comparable
    analyzed_comps = []
    for comp in comparable_sales:
        # Calculate adjustments
        adjustments = {}
        total_adjustment = 0
        
        # Square footage adjustment
        if "sqft" in subject_property and "sqft" in comp:
            sqft_diff = subject_property["sqft"] - comp["sqft"]
            sqft_factor = factors.get("sqft", 150)  # Fallback to 150
            sqft_adj = sqft_diff * sqft_factor
            adjustments["sqft"] = sqft_adj
            total_adjustment += sqft_adj
        
        # Bedroom adjustment
        if "bedrooms" in subject_property and "bedrooms" in comp:
            bedroom_diff = subject_property["bedrooms"] - comp["bedrooms"]
            bedroom_factor = factors.get("bedroom", factors.get("bedrooms", 5000))  # Fallback to 5000
            bedroom_adj = bedroom_diff * bedroom_factor
            adjustments["bedrooms"] = bedroom_adj
            total_adjustment += bedroom_adj
        
        # Bathroom adjustment
        if "bathrooms" in subject_property and "bathrooms" in comp:
            bathroom_diff = subject_property["bathrooms"] - comp["bathrooms"]
            bathroom_factor = factors.get("bathroom", 10000)  # Fallback to 10000
            bathroom_adj = bathroom_diff * bathroom_factor
            adjustments["bathrooms"] = bathroom_adj
            total_adjustment += bathroom_adj
        
        # Lot size adjustment
        if "lot_size" in subject_property and "lot_size" in comp:
            lot_diff = subject_property["lot_size"] - comp["lot_size"]
            lot_factor = factors.get("lot_size", 20000)  # Fallback to 20000
            lot_adj = lot_diff * lot_factor
            adjustments["lot_size"] = lot_adj
            total_adjustment += lot_adj
        
        # Age adjustment
        if "year_built" in subject_property and "year_built" in comp:
            current_year = datetime.now().year
            subject_age = current_year - subject_property["year_built"]
            comp_age = current_year - comp["year_built"]
            age_diff = subject_age - comp_age
            age_factor = factors.get("age", -500)  # Fallback to -500
            age_adj = age_diff * age_factor
            adjustments["age"] = age_adj
            total_adjustment += age_adj
        
        # Condition adjustment
        if "condition" in subject_property and "condition" in comp:
            subject_cond = subject_property["condition"]
            comp_cond = comp["condition"]
            condition_factors = factors.get("condition", {"Excellent": 0.1, "Good": 0.0, "Fair": -0.1, "Poor": -0.2})
            if subject_cond in condition_factors and comp_cond in condition_factors:
                cond_adj = (condition_factors[subject_cond] - condition_factors[comp_cond]) * comp.get("sale_price", 0)
                adjustments["condition"] = cond_adj
                total_adjustment += cond_adj
        
        # Calculate adjusted sale price
        sale_price = comp.get("sale_price", 0)
        adjusted_price = sale_price + total_adjustment
        
        analyzed_comp = {
            "original_data": comp,
            "adjustments": adjustments,
            "total_adjustment": round(total_adjustment, 2),
            "adjusted_sale_price": round(adjusted_price, 2),
            "adjustment_percentage": round((total_adjustment / comp["sale_price"]) * 100, 2)
        }
        
        analyzed_comps.append(analyzed_comp)
    
    # Calculate final valuation
    adjusted_prices = [comp["adjusted_sale_price"] for comp in analyzed_comps]
    final_valuation = sum(adjusted_prices) / len(adjusted_prices)
    
    # Calculate confidence metrics
    price_variance = np.var(adjusted_prices)
    price_std = np.std(adjusted_prices)
    coefficient_of_variation = price_std / final_valuation
    
    # Quality assessment
    quality_factors = []
    if len(comparable_sales) >= 3:
        quality_factors.append("Sufficient comparables")
    if coefficient_of_variation < 0.1:
        quality_factors.append("Low price variance")
    if all(abs(comp["adjustment_percentage"]) < 20 for comp in analyzed_comps):
        quality_factors.append("Reasonable adjustments")
    
    confidence_score = len(quality_factors) / 3
    
    return {
        "subject_property": subject_property,
        "adjustment_factors": factors,
        "analyzed_comparables": analyzed_comps,
        "valuation_summary": {
            "final_valuation": round(final_valuation, 2),
            "price_range": {
                "min": round(min(adjusted_prices), 2),
                "max": round(max(adjusted_prices), 2),
                "median": round(np.median(adjusted_prices), 2)
            },
            "statistics": {
                "mean": round(np.mean(adjusted_prices), 2),
                "std_deviation": round(price_std, 2),
                "coefficient_of_variation": round(coefficient_of_variation, 3)
            }
        },
        "quality_assessment": {
            "confidence_score": round(confidence_score, 2),
            "quality_factors": quality_factors,
            "recommendation": "High confidence" if confidence_score > 0.7 else "Medium confidence" if confidence_score > 0.4 else "Low confidence"
        },
        "analysis_date": datetime.now().isoformat()
    }


@tool(
    name="property_condition_assessor",
    description="Assess property condition and identify maintenance needs",
    show_result=True,
)
def property_condition_assessor(
    property_address: str,
    property_age: int,
    property_type: str = "residential",
    last_inspection_date: Optional[str] = None,
    known_issues: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Assess property condition and identify maintenance needs.
    
    Args:
        property_address: Address of the property
        property_age: Age of the property in years
        property_type: Type of property (residential/commercial/industrial)
        last_inspection_date: Date of last inspection (YYYY-MM-DD format)
        known_issues: List of known issues or problems
        
    Returns:
        Dictionary containing property condition assessment
    """
    current_date = datetime.now()
    
    # Simulate property condition assessment based on age and type
    condition_scores = {
        "structural": 0,
        "electrical": 0,
        "plumbing": 0,
        "hvac": 0,
        "roofing": 0,
        "exterior": 0,
        "interior": 0,
        "appliances": 0
    }
    
    # Age-based condition scoring (0-100 scale)
    age_factor = max(0, 100 - (property_age * 2))  # 2 points deduction per year
    
    # System-specific condition assessment
    systems = {
        "structural": {"base_score": 95, "age_factor": 1.5, "lifespan": 100},
        "electrical": {"base_score": 90, "age_factor": 2.0, "lifespan": 30},
        "plumbing": {"base_score": 85, "age_factor": 2.5, "lifespan": 40},
        "hvac": {"base_score": 80, "age_factor": 3.0, "lifespan": 20},
        "roofing": {"base_score": 90, "age_factor": 2.5, "lifespan": 25},
        "exterior": {"base_score": 85, "age_factor": 2.0, "lifespan": 30},
        "interior": {"base_score": 80, "age_factor": 1.5, "lifespan": 20},
        "appliances": {"base_score": 75, "age_factor": 4.0, "lifespan": 15}
    }
    
    maintenance_items = []
    urgent_issues = []
    recommended_upgrades = []
    
    for system, config in systems.items():
        # Calculate condition score
        age_penalty = min(property_age * config["age_factor"], 50)
        condition_score = max(0, config["base_score"] - age_penalty)
        condition_scores[system] = round(condition_score, 1)
        
        # Determine maintenance needs
        if condition_score < 30:
            urgent_issues.append({
                "system": system,
                "issue": f"Critical {system} system failure",
                "priority": "Urgent",
                "estimated_cost": np.random.randint(5000, 25000)
            })
        elif condition_score < 60:
            maintenance_items.append({
                "system": system,
                "maintenance": f"{system.title()} system needs attention",
                "priority": "High",
                "estimated_cost": np.random.randint(1000, 8000)
            })
        elif condition_score < 80:
            maintenance_items.append({
                "system": system,
                "maintenance": f"{system.title()} system maintenance recommended",
                "priority": "Medium",
                "estimated_cost": np.random.randint(200, 2000)
            })
        
        # Check if system is near end of life
        if property_age > config["lifespan"] * 0.8:
            recommended_upgrades.append({
                "system": system,
                "upgrade": f"{system.title()} system replacement recommended",
                "reason": f"System age ({property_age} years) exceeds 80% of expected lifespan ({config['lifespan']} years)",
                "estimated_cost": np.random.randint(3000, 15000)
            })
    
    # Add known issues if provided
    if known_issues:
        for issue in known_issues:
            urgent_issues.append({
                "system": "General",
                "issue": issue,
                "priority": "High",
                "estimated_cost": np.random.randint(500, 5000)
            })
    
    # Calculate overall condition score
    overall_condition = round(sum(condition_scores.values()) / len(condition_scores), 1)
    
    # Determine overall condition rating
    if overall_condition >= 90:
        condition_rating = "Excellent"
    elif overall_condition >= 80:
        condition_rating = "Good"
    elif overall_condition >= 70:
        condition_rating = "Fair"
    elif overall_condition >= 60:
        condition_rating = "Poor"
    else:
        condition_rating = "Critical"
    
    # Calculate total maintenance costs
    total_urgent_cost = sum(item["estimated_cost"] for item in urgent_issues)
    total_maintenance_cost = sum(item["estimated_cost"] for item in maintenance_items)
    total_upgrade_cost = sum(item["estimated_cost"] for item in recommended_upgrades)
    
    return {
        "property_info": {
            "address": property_address,
            "age_years": property_age,
            "property_type": property_type,
            "assessment_date": current_date.isoformat(),
            "last_inspection": last_inspection_date
        },
        "condition_assessment": {
            "overall_condition_score": overall_condition,
            "condition_rating": condition_rating,
            "system_scores": condition_scores
        },
        "maintenance_analysis": {
            "urgent_issues": urgent_issues,
            "maintenance_items": maintenance_items,
            "recommended_upgrades": recommended_upgrades,
            "cost_summary": {
                "urgent_repairs": total_urgent_cost,
                "maintenance": total_maintenance_cost,
                "upgrades": total_upgrade_cost,
                "total_estimated_cost": total_urgent_cost + total_maintenance_cost + total_upgrade_cost
            }
        },
        "recommendations": {
    # Ne garder que les dicts et protéger l'accès aux clés
    "immediate_actions": [
        d.get("issue") for d in urgent_issues if isinstance(d, dict) and "issue" in d
    ],
    "maintenance_priority": sorted(
        [d for d in maintenance_items if isinstance(d, dict)],
        key=lambda d: d.get("priority", "")  # évite l'indexation sur un float
    ),
    "investment_opportunities": recommended_upgrades
}

    }


@tool(
    name="inspection_report_analyzer",
    description="Analyze property inspection reports and extract key findings",
    show_result=True,
)
def inspection_report_analyzer(
    inspection_report: str,
    property_address: str,
    inspection_date: str,
    inspector_company: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Analyze property inspection reports and extract key findings.
    
    Args:
        inspection_report: Text content of the inspection report
        property_address: Address of the inspected property
        inspection_date: Date of inspection (YYYY-MM-DD format)
        inspector_company: Name of the inspection company
        
    Returns:
        Dictionary containing analysis of inspection findings
    """
    # Simulate inspection report analysis
    # In production, this would use NLP to parse actual inspection reports
    
    # Common inspection categories and issues
    inspection_categories = {
        "structural": {
            "issues": ["Foundation cracks", "Settlement", "Structural damage"],
            "severity": ["Minor", "Moderate", "Major"]
        },
        "electrical": {
            "issues": ["Outdated wiring", "GFCI issues", "Panel problems"],
            "severity": ["Minor", "Moderate", "Major"]
        },
        "plumbing": {
            "issues": ["Leaks", "Water pressure", "Drainage problems"],
            "severity": ["Minor", "Moderate", "Major"]
        },
        "hvac": {
            "issues": ["System age", "Efficiency", "Ductwork"],
            "severity": ["Minor", "Moderate", "Major"]
        },
        "roofing": {
            "issues": ["Shingle condition", "Flashing", "Gutters"],
            "severity": ["Minor", "Moderate", "Major"]
        },
        "exterior": {
            "issues": ["Siding", "Windows", "Paint condition"],
            "severity": ["Minor", "Moderate", "Major"]
        },
        "interior": {
            "issues": ["Flooring", "Walls", "Ceilings"],
            "severity": ["Minor", "Moderate", "Major"]
        }
    }
    
    # Simulate findings based on report content analysis
    findings = []
    total_issues = 0
    critical_issues = 0
    estimated_costs = []
    
    for category, config in inspection_categories.items():
        # Simulate random findings for demonstration
        num_issues = np.random.randint(0, 3)
        for _ in range(num_issues):
            issue = np.random.choice(config["issues"])
            severity = np.random.choice(config["severity"])
            
            # Estimate cost based on severity
            if severity == "Minor":
                cost = np.random.randint(100, 1000)
            elif severity == "Moderate":
                cost = np.random.randint(1000, 5000)
            else:  # Major
                cost = np.random.randint(5000, 20000)
                critical_issues += 1
            
            finding = {
                "category": category,
                "issue": issue,
                "severity": severity,
                "estimated_cost": cost,
                "recommendation": f"Address {issue.lower()} in {category} system"
            }
            
            findings.append(finding)
            estimated_costs.append(cost)
            total_issues += 1
    
    # Calculate summary statistics
    total_estimated_cost = sum(estimated_costs)
    avg_cost_per_issue = total_estimated_cost / max(total_issues, 1)
    
    # Categorize findings by severity
    severity_counts = {"Minor": 0, "Moderate": 0, "Major": 0}
    for finding in findings:
        severity_counts[finding["severity"]] += 1
    
    # Generate recommendations
    recommendations = []
    if critical_issues > 0:
        recommendations.append("Address critical issues before closing")
    if total_estimated_cost > 10000:
        recommendations.append("Consider negotiating repair credits")
    if len(findings) > 10:
        recommendations.append("Property may need significant maintenance")
    
    return {
        "inspection_info": {
            "property_address": property_address,
            "inspection_date": inspection_date,
            "inspector_company": inspector_company,
            "analysis_date": datetime.now().isoformat()
        },
        "findings_summary": {
            "total_issues": total_issues,
            "critical_issues": critical_issues,
            "severity_breakdown": severity_counts,
            "total_estimated_cost": total_estimated_cost,
            "average_cost_per_issue": round(avg_cost_per_issue, 2)
        },
        "detailed_findings": findings,

        "recommendations": {
    "immediate_actions": recommendations,
    "negotiation_points": [
        f.get("issue") for f in findings
        if isinstance(f, dict) and f.get("severity") == "Major"
    ],
    "maintenance_plan": [
        f.get("recommendation") for f in findings
        if isinstance(f, dict) and f.get("severity") in ["Minor", "Moderate"]
    ]
},

        
        "risk_assessment": {
            "overall_risk": "High" if critical_issues > 2 else "Medium" if critical_issues > 0 else "Low",
            "cost_impact": "Significant" if total_estimated_cost > 15000 else "Moderate" if total_estimated_cost > 5000 else "Minimal",
            "timeline_impact": "Delayed closing recommended" if critical_issues > 1 else "Normal timeline"
        }
    }


@tool(
    name="maintenance_cost_estimator",
    description="Estimate maintenance and repair costs for property improvements",
    show_result=True,
)
def maintenance_cost_estimator(
    property_address: str,
    maintenance_items: List[str],
    property_sqft: int,
    property_age: int,
    location: str,
) -> Dict[str, Any]:
    """
    Estimate maintenance and repair costs for property improvements.
    
    Args:
        property_address: Address of the property
        maintenance_items: List of maintenance/repair items needed
        property_sqft: Square footage of the property
        property_age: Age of the property in years
        location: Geographic location for cost estimation
        
    Returns:
        Dictionary containing cost estimates and recommendations
    """
    # Base cost database for common maintenance items
    cost_database = {
        "roof_repair": {"base_cost": 300, "per_sqft": True, "complexity_factor": 1.2},
        "roof_replacement": {"base_cost": 500, "per_sqft": True, "complexity_factor": 1.5},
        "hvac_repair": {"base_cost": 800, "per_sqft": False, "complexity_factor": 1.0},
        "hvac_replacement": {"base_cost": 8000, "per_sqft": False, "complexity_factor": 1.3},
        "plumbing_repair": {"base_cost": 400, "per_sqft": False, "complexity_factor": 1.1},
        "electrical_repair": {"base_cost": 600, "per_sqft": False, "complexity_factor": 1.2},
        "flooring_repair": {"base_cost": 8, "per_sqft": True, "complexity_factor": 1.0},
        "flooring_replacement": {"base_cost": 12, "per_sqft": True, "complexity_factor": 1.1},
        "painting_interior": {"base_cost": 3, "per_sqft": True, "complexity_factor": 1.0},
        "painting_exterior": {"base_cost": 2, "per_sqft": True, "complexity_factor": 1.2},
        "window_replacement": {"base_cost": 500, "per_sqft": False, "complexity_factor": 1.0},
        "appliance_repair": {"base_cost": 300, "per_sqft": False, "complexity_factor": 1.0},
        "appliance_replacement": {"base_cost": 1200, "per_sqft": False, "complexity_factor": 1.0},
        "landscaping": {"base_cost": 5, "per_sqft": True, "complexity_factor": 1.0},
        "driveway_repair": {"base_cost": 8, "per_sqft": True, "complexity_factor": 1.1},
        "fence_repair": {"base_cost": 15, "per_sqft": True, "complexity_factor": 1.0},
        "deck_repair": {"base_cost": 20, "per_sqft": True, "complexity_factor": 1.2},
        "basement_waterproofing": {"base_cost": 10, "per_sqft": True, "complexity_factor": 1.5},
        "insulation_upgrade": {"base_cost": 2, "per_sqft": True, "complexity_factor": 1.0},
        "energy_efficiency": {"base_cost": 4, "per_sqft": True, "complexity_factor": 1.1}
    }
    
    # Location-based cost multipliers
    location_multipliers = {
        "urban": 1.3,
        "suburban": 1.0,
        "rural": 0.8,
        "high_cost_area": 1.5,
        "low_cost_area": 0.7
    }
    
    # Age-based complexity factors
    age_complexity = 1.0 + (property_age * 0.01)  # 1% increase per year
    
    # Estimate costs for each maintenance item
    cost_estimates = []
    total_estimated_cost = 0
    
    for item in maintenance_items:
        # Find matching cost data
        item_lower = item.lower().replace(" ", "_")
        cost_data = None
        
        # Try to match item with cost database
        for key, data in cost_database.items():
            if key in item_lower or any(word in item_lower for word in key.split("_")):
                cost_data = data
                break
        
        if not cost_data:
            # Default cost estimation for unknown items
            cost_data = {"base_cost": 500, "per_sqft": False, "complexity_factor": 1.0}
        
        # Calculate base cost
        if cost_data["per_sqft"]:
            base_cost = cost_data["base_cost"] * property_sqft
        else:
            base_cost = cost_data["base_cost"]
        
        # Apply complexity factors
        complexity_factor = cost_data["complexity_factor"] * age_complexity
        
        # Apply location multiplier (simplified - in production, use actual location data)
        location_multiplier = location_multipliers.get("suburban", 1.0)
        
        # Calculate final cost
        final_cost = base_cost * complexity_factor * location_multiplier
        
        # Add some variance for realism
        variance = np.random.uniform(0.8, 1.2)
        final_cost *= variance
        
        cost_estimate = {
            "item": item,
            "base_cost": round(base_cost, 2),
            "complexity_factor": round(complexity_factor, 2),
            "location_multiplier": location_multiplier,
            "estimated_cost": round(final_cost, 2),
            "cost_range": {
                "low": round(final_cost * 0.8, 2),
                "high": round(final_cost * 1.2, 2)
            }
        }
        
        cost_estimates.append(cost_estimate)
        total_estimated_cost += final_cost
    
    # Categorize by priority and timeline
    priority_items = []
    timeline_recommendations = []
    
    for estimate in cost_estimates:
        if estimate["estimated_cost"] > 5000:
            priority_items.append({
                "item": estimate["item"],
                "priority": "High",
                "timeline": "Immediate (0-3 months)",
                "reason": "High cost item requiring immediate attention"
            })
        elif estimate["estimated_cost"] > 2000:
            priority_items.append({
                "item": estimate["item"],
                "priority": "Medium",
                "timeline": "Short-term (3-6 months)",
                "reason": "Moderate cost item for near-term planning"
            })
        else:
            priority_items.append({
                "item": estimate["item"],
                "priority": "Low",
                "timeline": "Long-term (6-12 months)",
                "reason": "Lower cost item for future planning"
            })
    
    # Generate financing recommendations
    financing_options = []
    if total_estimated_cost > 10000:
        financing_options.append("Consider home equity loan for major repairs")
    if total_estimated_cost > 5000:
        financing_options.append("Personal loan or credit line for moderate repairs")
    if total_estimated_cost < 5000:
        financing_options.append("Cash payment or credit card for minor repairs")
    
    return {
        "property_info": {
            "address": property_address,
            "sqft": property_sqft,
            "age_years": property_age,
            "location": location,
            "estimation_date": datetime.now().isoformat()
        },
        "cost_estimates": cost_estimates,
        "summary": {
            "total_estimated_cost": round(total_estimated_cost, 2),
            "cost_range": {
                "low": round(total_estimated_cost * 0.8, 2),
                "high": round(total_estimated_cost * 1.2, 2)
            },
            "number_of_items": len(maintenance_items),
            "average_cost_per_item": round(total_estimated_cost / len(maintenance_items), 2)
        },
        "prioritization": {
            "high_priority": [item for item in priority_items if item["priority"] == "High"],
            "medium_priority": [item for item in priority_items if item["priority"] == "Medium"],
            "low_priority": [item for item in priority_items if item["priority"] == "Low"]
        },
        "recommendations": {
            "financing_options": financing_options,
            "timeline": timeline_recommendations,
            "cost_saving_tips": [
                "Get multiple quotes for major repairs",
                "Consider DIY for minor maintenance items",
                "Plan repairs during off-season for better pricing",
                "Bundle related repairs for contractor discounts"
            ]
        }
    }