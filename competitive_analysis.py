"""
Competitive Analysis Skill for Dream Finders Homes

Analyzes competitor data (Lennar, Meritage, DR Horton, Pulte) to provide
executive-level insights on special financing, inventory, and pricing.
"""

from __future__ import annotations
from types import SimpleNamespace
from typing import List, Optional, Dict, Any
import json
import re
from collections import defaultdict

from skill_framework import SkillInput, SkillVisualization, skill, SkillParameter, SkillOutput
from skill_framework.layouts import wire_layout
from competitive_layouts import competitive_dashboard_layout

# List of target competitors
COMPETITORS = ["lennar", "meritage", "dr horton", "pulte", "dreamfinders", "dream finders"]

@skill(
    name="Competitive Analysis",
    description="Analyze competitor data on special financing, inventory, and pricing for Dream Finders Homes executive insights",
    capabilities="Extracts and analyzes competitor special financing rates, inventory counts, pricing data from Lennar, Meritage, DR Horton, and Pulte. Generates executive dashboard with comparison tables and insights.",
    limitations="Limited to data available in pack.json knowledge base",
    parameters=[
        SkillParameter(
            name="builder_names",
            description="Comma-separated list of builders to analyze (e.g., 'Lennar, Meritage'). Leave empty for all competitors.",
            default_value="Lennar, Meritage, Dream Finders, Pulte"
        ),
        SkillParameter(
            name="analysis_type",
            description="Type of analysis: 'financing', 'inventory', 'pricing', or 'all'",
            default_value="all"
        ),
        SkillParameter(
            name="region",
            description="Geographic region to focus on",
            default_value="Atlanta"
        )
    ]
)
def competitive_analysis(parameters: SkillInput) -> SkillOutput:
    """
    Main competitive analysis skill entry point
    """

    # Extract parameters
    builder_names = parameters.arguments.builder_names or "Lennar, Meritage, Dream Finders, Pulte"
    analysis_type = parameters.arguments.analysis_type or "all"
    region = parameters.arguments.region or "Atlanta"

    # Parse builder names
    builders = [b.strip().lower() for b in builder_names.split(",")]

    print(f"DEBUG: Analyzing builders: {builders}")
    print(f"DEBUG: Analysis type: {analysis_type}")
    print(f"DEBUG: Region: {region}")

    # Extract competitive data from pack
    competitive_data = extract_competitive_data(builders, region)

    if not competitive_data:
        return SkillOutput(
            final_prompt="No competitive data found. Please ensure competitor documents are loaded in the pack.",
            warnings=["No data available"]
        )

    # Generate insights based on analysis type
    insights = generate_insights(competitive_data, analysis_type)

    # Create visualization
    viz = create_competitive_dashboard(competitive_data, analysis_type)

    # Generate narrative
    narrative = format_narrative(competitive_data, insights, analysis_type)

    # Generate insights for narrative
    insights_narrative = generate_insights_narrative(competitive_data, insights)

    return SkillOutput(
        final_prompt=narrative,
        narrative=insights_narrative,
        visualizations=[viz] if viz else None
    )


def extract_competitive_data(builders: List[str], region: str) -> Dict[str, Any]:
    """
    Extract structured competitive data from pack documents
    """
    data = {
        "financing": {},
        "inventory": {},
        "pricing": {},
        "metadata": {}
    }

    # Query pack for each builder
    for builder in builders:
        print(f"DEBUG: Extracting data for {builder}")

        # Extract financing offers
        financing = extract_financing_data(builder, region)
        if financing:
            data["financing"][builder] = financing

        # Extract inventory stats
        inventory = extract_inventory_data(builder, region)
        if inventory:
            data["inventory"][builder] = inventory

        # Extract pricing data
        pricing = extract_pricing_data(builder, region)
        if pricing:
            data["pricing"][builder] = pricing

    return data


def extract_financing_data(builder: str, region: str) -> Optional[Dict[str, Any]]:
    """
    Extract special financing offers from documents
    """
    # Search for financing-related keywords
    keywords = [
        f"{builder} special financing",
        f"{builder} interest rate",
        f"{builder} promotional rate",
        f"{builder} closing costs",
        f"{builder} incentives"
    ]

    financing_info = {
        "rates": [],
        "incentives": [],
        "terms": [],
        "expiration": None
    }

    # Use simple keyword matching on pack documents
    # This is a placeholder - will use the pack.json data directly

    # Parse known data from pack.json structure
    if "lennar" in builder.lower():
        financing_info["rates"].append({
            "type": "5/1 ARM",
            "rate": "3.75%",
            "apr": "5.791%"
        })
        financing_info["rates"].append({
            "type": "Conventional Fixed",
            "rate": "4.99%",
            "apr": "6.065%"
        })
        financing_info["incentives"].append("Up to $7,500 in Closing Costs")
        financing_info["expiration"] = "09/30/25"

    elif "meritage" in builder.lower():
        financing_info["rates"].append({
            "type": "2/1 Buydown",
            "rate": "2.99%",
            "apr": "5.572%"
        })
        financing_info["terms"].append("Monthly payments as low as $1,700")
        financing_info["expiration"] = "September 6-21"

    elif "dream" in builder.lower():
        financing_info["rates"].append({
            "type": "2/1 Buydown",
            "rate": "2.99%",
            "apr": "5.955%"
        })
        financing_info["rates"].append({
            "type": "Fixed Rate",
            "rate": "4.99%",
            "apr": "5.959%"
        })
        financing_info["incentives"].append("Save up to $21,000 on select homes")
        financing_info["terms"].append("Monthly payments starting as low as $913")

    elif "pulte" in builder.lower():
        financing_info["rates"].append({
            "type": "7/6 ARM",
            "rate": "3.99%",
            "apr": "5.979%"
        })
        financing_info["incentives"].append("Fixed for First 7 Years")
        financing_info["terms"].append("On Select Move-In Ready Homes")

    return financing_info if financing_info["rates"] else None


def extract_inventory_data(builder: str, region: str) -> Optional[Dict[str, Any]]:
    """
    Extract inventory counts and stats
    """
    inventory_info = {
        "move_in_ready": 0,
        "under_construction": 0,
        "total_homes": 0,
        "communities": 0,
        "spec_homes": 0
    }

    # Parse from pack.json data
    if "lennar" in builder.lower():
        inventory_info["total_homes"] = 43
        inventory_info["communities"] = 26
        inventory_info["move_in_ready"] = 30  # Approximate from "move-in ready" tags
        inventory_info["under_construction"] = 10

    elif "meritage" in builder.lower():
        inventory_info["total_homes"] = 114
        inventory_info["communities"] = 23
        inventory_info["move_in_ready"] = 114  # "Quick Move-In Homes"

    elif "dream" in builder.lower():
        inventory_info["total_homes"] = 25
        inventory_info["move_in_ready"] = 25

    elif "pulte" in builder.lower():
        inventory_info["total_homes"] = 47
        inventory_info["communities"] = 47  # "47 Communities in your search"

    return inventory_info if inventory_info["total_homes"] > 0 else None


def extract_pricing_data(builder: str, region: str) -> Optional[Dict[str, Any]]:
    """
    Extract pricing information and reductions
    """
    pricing_info = {
        "avg_price": None,
        "price_range": {"min": None, "max": None},
        "price_reductions": [],
        "avg_sqft": None
    }

    # Would parse price data from pack documents
    # For now, using sample data structure

    if "lennar" in builder.lower():
        pricing_info["price_range"] = {"min": 353705, "max": 733440}
        pricing_info["avg_price"] = 450000  # Approximate
        pricing_info["price_reductions"] = [
            {"amount": 36000, "original": 447665},
            {"amount": 30000, "original": 499375},
            {"amount": 74000, "original": 699365}
        ]

    elif "meritage" in builder.lower():
        pricing_info["price_range"] = {"min": 384990, "max": 519980}
        pricing_info["avg_price"] = 450000

    elif "dream" in builder.lower():
        pricing_info["avg_price"] = 400000  # Sample

    elif "pulte" in builder.lower():
        pricing_info["price_range"] = {"min": 362990, "max": 529990}
        pricing_info["avg_price"] = 440000  # Average of range

    return pricing_info


def generate_insights(data: Dict[str, Any], analysis_type: str) -> Dict[str, Any]:
    """
    Generate executive-level insights from competitive data
    """
    insights = {
        "best_rate": None,
        "best_incentive": None,
        "market_leader": None,
        "recommendations": []
    }

    # Find best financing rate
    best_rate = float('inf')
    best_rate_builder = None

    for builder, financing in data["financing"].items():
        for rate_offer in financing.get("rates", []):
            rate_val = float(rate_offer["rate"].replace("%", ""))
            if rate_val < best_rate:
                best_rate = rate_val
                best_rate_builder = builder

    insights["best_rate"] = {
        "builder": best_rate_builder,
        "rate": f"{best_rate}%"
    }

    # Find best incentive
    max_incentive = 0
    best_incentive_builder = None

    for builder, financing in data["financing"].items():
        for incentive in financing.get("incentives", []):
            # Extract dollar amounts
            amounts = re.findall(r'\$?(\d{1,3}(?:,\d{3})*(?:K)?)', incentive)
            for amount in amounts:
                val = parse_dollar_amount(amount)
                if val > max_incentive:
                    max_incentive = val
                    best_incentive_builder = builder

    insights["best_incentive"] = {
        "builder": best_incentive_builder,
        "amount": f"${max_incentive:,.0f}"
    }

    # Determine market leader by inventory
    max_inventory = 0
    market_leader = None

    for builder, inventory in data["inventory"].items():
        total = inventory.get("total_homes", 0)
        if total > max_inventory:
            max_inventory = total
            market_leader = builder

    insights["market_leader"] = {
        "builder": market_leader,
        "homes": max_inventory
    }

    # Generate recommendations
    insights["recommendations"] = [
        f"Competitive rate positioning: DreamFinders' 2.99% matches {best_rate_builder}'s best offer",
        f"Incentive advantage: DreamFinders' $21K incentive exceeds Lennar's $7.5K by 180%",
        f"Inventory opportunity: {market_leader} has {max_inventory} homes available - consider expanding inventory to compete"
    ]

    return insights


def parse_dollar_amount(amount_str: str) -> float:
    """
    Parse dollar amount string to float
    """
    # Remove commas and handle K for thousands
    cleaned = amount_str.replace(",", "")
    if "K" in cleaned or "k" in cleaned:
        return float(cleaned.replace("K", "").replace("k", "")) * 1000
    return float(cleaned)


def create_mortgage_rate_chart() -> Dict[str, Any]:
    """
    Create mortgage rate trend chart with builder offers plotted
    """
    # Hardcoded Freddie Mac mortgage rates (Oct 2024 onwards)
    mortgage_30yr = [
        {"date": "Oct 2024", "rate": 6.45}, {"date": "Oct 2024", "rate": 6.39},
        {"date": "Nov 2024", "rate": 6.32}, {"date": "Nov 2024", "rate": 6.28},
        {"date": "Dec 2024", "rate": 6.24}, {"date": "Dec 2024", "rate": 6.21},
        {"date": "Jan 2025", "rate": 6.98}, {"date": "Jan 2025", "rate": 6.96},
        {"date": "Feb 2025", "rate": 6.95}, {"date": "Feb 2025", "rate": 6.88},
        {"date": "Mar 2025", "rate": 6.86}, {"date": "Mar 2025", "rate": 6.89},
        {"date": "Apr 2025", "rate": 6.94}, {"date": "Apr 2025", "rate": 6.98},
        {"date": "May 2025", "rate": 6.91}, {"date": "May 2025", "rate": 6.86},
        {"date": "Jun 2025", "rate": 6.84}, {"date": "Jun 2025", "rate": 6.77},
        {"date": "Jul 2025", "rate": 6.72}, {"date": "Jul 2025", "rate": 6.74},
        {"date": "Aug 2025", "rate": 6.63}, {"date": "Aug 2025", "rate": 6.56},
        {"date": "Sep 2025", "rate": 6.50}, {"date": "Sep 2025", "rate": 6.35},
        {"date": "Sep 2025", "rate": 6.26}, {"date": "Sep 2025", "rate": 6.30},
        {"date": "Oct 2025", "rate": 6.34}
    ]

    mortgage_15yr = [
        {"date": "Oct 2024", "rate": 5.76}, {"date": "Oct 2024", "rate": 5.71},
        {"date": "Nov 2024", "rate": 5.64}, {"date": "Nov 2024", "rate": 5.61},
        {"date": "Dec 2024", "rate": 5.57}, {"date": "Dec 2024", "rate": 5.53},
        {"date": "Jan 2025", "rate": 6.17}, {"date": "Jan 2025", "rate": 6.14},
        {"date": "Feb 2025", "rate": 6.11}, {"date": "Feb 2025", "rate": 6.06},
        {"date": "Mar 2025", "rate": 6.04}, {"date": "Mar 2025", "rate": 6.08},
        {"date": "Apr 2025", "rate": 6.15}, {"date": "Apr 2025", "rate": 6.18},
        {"date": "May 2025", "rate": 6.01}, {"date": "May 2025", "rate": 6.03},
        {"date": "Jun 2025", "rate": 5.99}, {"date": "Jun 2025", "rate": 5.89},
        {"date": "Jul 2025", "rate": 5.86}, {"date": "Jul 2025", "rate": 5.87},
        {"date": "Aug 2025", "rate": 5.75}, {"date": "Aug 2025", "rate": 5.69},
        {"date": "Sep 2025", "rate": 5.60}, {"date": "Sep 2025", "rate": 5.50},
        {"date": "Sep 2025", "rate": 5.41}, {"date": "Sep 2025", "rate": 5.49},
        {"date": "Oct 2025", "rate": 5.55}
    ]

    categories = [d["date"] for d in mortgage_30yr]
    rates_30yr = [d["rate"] for d in mortgage_30yr]
    rates_15yr = [d["rate"] for d in mortgage_15yr]

    print(f"DEBUG: Mortgage chart - created {len(categories)} data points")
    print(f"DEBUG: First category: {categories[0]}, Last category: {categories[-1]}")

    # Create Highcharts configuration with builder offer points
    chart_config = {
        "chart": {"type": "line", "height": 450, "backgroundColor": "#FAFAFA"},
        "title": {
            "text": "US Weekly Avg Mortgage Rates",
            "style": {"fontSize": "20px", "fontWeight": "700", "color": "#2C3E50"}
        },
        "subtitle": {
            "text": "Source: Freddie Mac | Builder special offers plotted at Sep 2025",
            "style": {"fontSize": "13px", "color": "#7F8C8D"}
        },
        "xAxis": {
            "categories": categories,
            "title": {"text": ""},
            "labels": {"rotation": -45, "style": {"fontSize": "10px"}},
            "gridLineWidth": 1,
            "gridLineColor": "#e8e8e8"
        },
        "yAxis": {
            "title": {"text": "Interest Rate (%)", "style": {"fontWeight": "600", "fontSize": "13px"}},
            "labels": {"format": "{value}%"},
            "gridLineColor": "#e8e8e8",
            "min": 2.5
        },
        "tooltip": {
            "shared": False,
            "crosshairs": True,
            "backgroundColor": "#ffffff",
            "borderColor": "#cccccc",
            "borderRadius": 8,
            "style": {"fontSize": "12px"},
            "pointFormat": "<span style=\"color:{series.color}\">\u25CF</span> <b>{series.name}</b>: {point.y}%<br/>"
        },
        "legend": {
            "enabled": True,
            "align": "center",
            "verticalAlign": "bottom",
            "itemStyle": {"fontSize": "12px", "fontWeight": "500"}
        },
        "plotOptions": {
            "line": {"lineWidth": 2.5},
            "scatter": {"marker": {"radius": 10}}
        },
        "series": [
            {
                "name": "30-Year Fixed",
                "data": rates_30yr,
                "color": "#2ecc71",
                "lineWidth": 2.5,
                "marker": {"enabled": False},
                "zIndex": 1
            },
            {
                "name": "15-Year Fixed",
                "data": rates_15yr,
                "color": "#f39c12",
                "lineWidth": 2.5,
                "dashStyle": "ShortDash",
                "marker": {"enabled": False},
                "zIndex": 1
            },
            {
                "name": "Lennar (3.75%)",
                "type": "scatter",
                "data": [[25, 3.75]],  # Sep 2025 center
                "color": "#3498db",
                "marker": {"radius": 11, "symbol": "circle", "lineWidth": 2, "lineColor": "#ffffff"},
                "zIndex": 10
            },
            {
                "name": "Meritage (2.99%)",
                "type": "scatter",
                "data": [[24.7, 2.99]],  # Slightly left to avoid overlap
                "color": "#e74c3c",
                "marker": {"radius": 11, "symbol": "diamond", "lineWidth": 2, "lineColor": "#ffffff"},
                "zIndex": 10
            },
            {
                "name": "Dream Finders (2.99%)",
                "type": "scatter",
                "data": [[25.3, 2.99]],  # Slightly right to avoid overlap
                "color": "#9b59b6",
                "marker": {"radius": 11, "symbol": "square", "lineWidth": 2, "lineColor": "#ffffff"},
                "zIndex": 10
            }
        ],
        "credits": {"enabled": False}
    }

    print(f"DEBUG: Chart config created with {len(chart_config['series'])} series")
    return chart_config


def create_competitive_dashboard(data: Dict[str, Any], analysis_type: str) -> SkillVisualization:
    """
    Create competitive dashboard with individual builder cards
    """
    print(f"DEBUG: Creating dashboard visualization")
    print(f"DEBUG: Data keys - financing: {list(data['financing'].keys())}, inventory: {list(data['inventory'].keys())}, pricing: {list(data['pricing'].keys())}")

    # Create individual builder cards
    builder_cards = {}

    for builder in ["lennar", "meritage", "dream finders", "pulte"]:
        card_content = create_builder_card(builder, data)
        print(f"DEBUG: Created card for {builder}: {card_content[:100] if len(card_content) > 100 else card_content}")

        # Map to variable names
        if "lennar" in builder.lower():
            builder_cards["lennar_card"] = card_content
        elif "meritage" in builder.lower():
            builder_cards["meritage_card"] = card_content
        elif "dream" in builder.lower():
            builder_cards["dreamfinders_card"] = card_content
        elif "pulte" in builder.lower():
            builder_cards["pulte_card"] = card_content
            print(f"DEBUG: Pulte card set to: {card_content}")

    # Generate mortgage rate chart
    mortgage_chart_dict = create_mortgage_rate_chart()
    print(f"DEBUG: Mortgage chart dict created, type: {type(mortgage_chart_dict)}")
    print(f"DEBUG: Mortgage chart keys: {list(mortgage_chart_dict.keys())}")

    # Ensure all cards have values
    variables = {
        "lennar_card": builder_cards.get("lennar_card", "No data available"),
        "meritage_card": builder_cards.get("meritage_card", "No data available"),
        "dreamfinders_card": builder_cards.get("dreamfinders_card", "No data available"),
        "pulte_card": builder_cards.get("pulte_card", "No data available"),
        "mortgage_chart": mortgage_chart_dict
    }

    print(f"DEBUG: Variables created: {list(variables.keys())}")
    print(f"DEBUG: mortgage_chart type in variables: {type(variables['mortgage_chart'])}")

    # Parse layout JSON
    import json
    layout_dict = json.loads(competitive_dashboard_layout)
    print(f"DEBUG: Layout parsed successfully")

    # Render using wire_layout
    rendered = wire_layout(layout_dict, variables)
    print(f"DEBUG: Layout rendered successfully")

    return SkillVisualization(
        title="Competitive Analysis",
        layout=rendered
    )


def generate_insights_narrative(data: Dict[str, Any], insights: Dict[str, Any]) -> str:
    """
    Generate recovery-focused insights for Dream Finders
    """
    narrative_parts = []

    # Get Dream Finders data
    df_financing = data["financing"].get("dream finders", {})
    df_inventory = data["inventory"].get("dream finders", {})
    df_pricing = data["pricing"].get("dream finders", {})

    # Competitive threats
    narrative_parts.append("## Market Threats\n")
    threats = []

    if insights.get("best_rate") and df_financing.get("rates"):
        best_rate = float(insights["best_rate"]["rate"].replace("%", ""))
        df_rate = float(df_financing["rates"][0]["rate"].replace("%", ""))
        rate_diff = df_rate - best_rate

        if rate_diff > 0:
            threats.append(f"**Rate disadvantage:** {insights['best_rate']['builder'].title()} undercuts Dream Finders by {rate_diff:.2f}%, making their financing more attractive to price-sensitive buyers")
        else:
            threats.append(f"**Rate parity achieved:** Dream Finders matches the market-leading {df_rate}% rate")

    if insights.get("market_leader") and df_inventory.get("total_homes"):
        leader = insights["market_leader"]
        df_homes = df_inventory["total_homes"]
        inventory_ratio = df_homes / leader["homes"]
        threats.append(f"**Inventory gap:** {leader['builder'].title()} has {leader['homes']} homes vs. Dream Finders' {df_homes} ({inventory_ratio:.0%} of leader's inventory), limiting buyer choice and market presence")

    narrative_parts.append("\n".join([f"- {t}" for t in threats]))

    # Recovery opportunities
    narrative_parts.append("\n\n## Recovery Opportunities\n")
    opportunities = []

    # Rate-based opportunities
    if insights.get("best_rate") and df_financing.get("rates"):
        best_rate_val = float(insights["best_rate"]["rate"].replace("%", ""))
        if df_rate > best_rate_val:
            savings_needed = int((df_rate - best_rate_val) * 100 * 2500)  # Rough monthly payment impact
            opportunities.append(f"**Match or beat leading rate:** Lowering to {best_rate_val}% could save buyers ~${savings_needed}/month, improving conversion rates")

    # Incentive opportunities
    if insights.get("best_incentive"):
        best_incentive = insights["best_incentive"]
        df_incentive_amount = 21000 if df_financing.get("incentives") else 0
        if df_incentive_amount < 25000:
            opportunities.append(f"**Increase closing cost assistance:** {best_incentive['builder'].title()} offers {best_incentive['amount']}. Consider matching or exceeding to win buyers on the fence")

    # Inventory opportunities
    opportunities.append("**Accelerate move-in ready inventory:** Fast-track spec homes to capture buyers who can't wait for new construction timelines")
    opportunities.append("**Target underserved price points:** Analyze competitor pricing gaps and develop offerings in underserved segments")

    narrative_parts.append("\n".join([f"- {o}" for o in opportunities]))

    # Action plan
    narrative_parts.append("\n\n## Recommended Actions\n")
    actions = []

    if df_rate > best_rate_val:
        actions.append("**Immediate:** Negotiate lender rate buydown to match {:.2f}% within 30 days".format(best_rate_val))

    actions.append("**Short-term:** Launch aggressive Q4 promotion combining rate incentives + closing cost assistance ($25K+)")
    actions.append("**Medium-term:** Increase spec home production by 40% to close inventory gap with market leaders")
    actions.append("**Long-term:** Differentiate on value-adds (smart home tech, upgraded finishes, energy efficiency) if rate parity isn't achievable")

    narrative_parts.append("\n".join([f"- {a}" for a in actions]))

    return "\n".join(narrative_parts)


def generate_insights_summary(data: Dict[str, Any]) -> str:
    """
    Generate key insights summary from competitive data
    """
    insights = []

    # Best rate comparison
    best_rate = float('inf')
    best_rate_builder = None
    for builder, financing in data["financing"].items():
        if financing.get("rates"):
            rate_val = float(financing["rates"][0]["rate"].replace("%", ""))
            if rate_val < best_rate:
                best_rate = rate_val
                best_rate_builder = builder.replace("dreamfinders", "Dream Finders").title()

    if best_rate_builder:
        insights.append(f"BEST RATE: {best_rate_builder} offers the most competitive financing at {best_rate}%")

    # Inventory leader
    max_inventory = 0
    inventory_leader = None
    for builder, inventory in data["inventory"].items():
        total = inventory.get("total_homes", 0)
        if total > max_inventory:
            max_inventory = total
            inventory_leader = builder.replace("dreamfinders", "Dream Finders").title()

    if inventory_leader:
        insights.append(f"INVENTORY LEADER: {inventory_leader} has {max_inventory} homes available, the largest inventory in the market")

    # Dream Finders competitive position
    df_financing = data["financing"].get("dreamfinders") or data["financing"].get("dream finders")
    if df_financing and df_financing.get("rates"):
        df_rate = float(df_financing["rates"][0]["rate"].replace("%", ""))
        rate_diff = df_rate - best_rate
        if rate_diff == 0:
            insights.append(f"COMPETITIVE POSITION: Dream Finders matches the market-leading rate")
        elif rate_diff < 1:
            insights.append(f"COMPETITIVE POSITION: Dream Finders is within {rate_diff:.2f}% of the best market rate")
        else:
            insights.append(f"OPPORTUNITY: Dream Finders rate is {rate_diff:.2f}% above the market leader")

    # Incentive comparison
    max_incentive = 0
    max_incentive_builder = None
    for builder, financing in data["financing"].items():
        for incentive_text in financing.get("incentives", []):
            amounts = re.findall(r'\$?(\d{1,3}(?:,\d{3})*(?:K)?)', incentive_text)
            for amount in amounts:
                val = parse_dollar_amount(amount)
                if val > max_incentive:
                    max_incentive = val
                    max_incentive_builder = builder.replace("dreamfinders", "Dream Finders").title()

    if max_incentive_builder:
        insights.append(f"TOP INCENTIVE: {max_incentive_builder} offers up to ${max_incentive:,.0f} in savings/incentives")

    return "\n\n".join(insights) if insights else "Insufficient data for insights"


def create_builder_card(builder: str, data: Dict[str, Any]) -> str:
    """
    Create card content for a single builder
    """
    financing = data["financing"].get(builder, {})
    inventory = data["inventory"].get(builder, {})
    pricing = data["pricing"].get(builder, {})

    card_text = ""

    # Financing section
    if financing.get("rates"):
        rate_info = financing["rates"][0]
        card_text += f"FINANCING\n"
        card_text += f"{rate_info.get('rate', 'N/A')} {rate_info.get('type', '')}\n"

        if financing.get("incentives"):
            card_text += f"{financing['incentives'][0]}\n"

        if financing.get("expiration"):
            card_text += f"Expires: {financing['expiration']}\n"

        card_text += "\n"

    # Inventory section
    if inventory.get("total_homes"):
        card_text += f"INVENTORY\n"
        card_text += f"{inventory['total_homes']} homes available\n"

        if inventory.get("move_in_ready"):
            card_text += f"{inventory['move_in_ready']} move-in ready\n"

        if inventory.get("communities"):
            card_text += f"{inventory['communities']} communities\n"

        card_text += "\n"

    # Pricing section
    if pricing.get("avg_price"):
        card_text += f"PRICING\n"
        card_text += f"Avg: ${pricing['avg_price']:,.0f}\n"

        if pricing.get("price_range"):
            pr = pricing["price_range"]
            if pr.get("min") and pr.get("max"):
                card_text += f"Range: ${pr['min']:,.0f} - ${pr['max']:,.0f}\n"

    return card_text.strip() if card_text else "No data available"


def create_financing_cards(financing_data: Dict[str, Any]) -> str:
    """
    Create formatted financing offer details
    """
    cards_text = ""

    for builder, financing in financing_data.items():
        builder_display = builder.replace("dreamfinders", "Dream Finders").title()

        # Get best rate
        best_rate = "N/A"
        rate_type = ""
        if financing.get("rates"):
            rate_info = financing["rates"][0]
            best_rate = rate_info.get("rate", "N/A")
            rate_type = rate_info.get("type", "")

        # Get incentive
        incentive = financing.get("incentives", ["No current incentives"])[0] if financing.get("incentives") else "No current incentives"

        # Get expiration
        expiration = financing.get("expiration", "Ongoing")

        cards_text += f"{builder_display}\n"
        cards_text += f"  {best_rate} {rate_type}\n"
        cards_text += f"  {incentive}\n"
        cards_text += f"  Expires: {expiration}\n\n"

    return cards_text.strip()


def create_comparison_table(data: Dict[str, Any]) -> str:
    """
    Create simple text comparison table
    """
    builders = list(data["financing"].keys())
    builder_displays = [b.replace("dreamfinders", "Dream Finders").title() for b in builders]

    # Calculate column widths
    col_width = 25
    metric_width = 20

    table_text = ""

    # Header
    header = "Metric".ljust(metric_width)
    for builder_name in builder_displays:
        header += builder_name[:col_width-1].ljust(col_width)
    table_text += header + "\n"
    table_text += "-" * (metric_width + col_width * len(builders)) + "\n"

    # Best Rate Row
    row = "Best Rate".ljust(metric_width)
    for builder in builders:
        rate = data["financing"][builder]["rates"][0]["rate"] if data["financing"][builder].get("rates") else "N/A"
        row += rate.ljust(col_width)
    table_text += row + "\n"

    # Total Homes Row
    row = "Available Homes".ljust(metric_width)
    for builder in builders:
        total = data["inventory"].get(builder, {}).get("total_homes", 0)
        row += str(total).ljust(col_width)
    table_text += row + "\n"

    # Communities Row
    row = "Communities".ljust(metric_width)
    for builder in builders:
        communities = data["inventory"].get(builder, {}).get("communities", 0)
        row += str(communities).ljust(col_width)
    table_text += row + "\n"

    # Avg Price Row
    row = "Avg Price".ljust(metric_width)
    for builder in builders:
        avg_price = data["pricing"].get(builder, {}).get("avg_price", 0)
        price_display = f"${avg_price:,.0f}" if avg_price else "N/A"
        row += price_display.ljust(col_width)
    table_text += row + "\n"

    return table_text


def create_inventory_stats(inventory_data: Dict[str, Any]) -> str:
    """
    Create formatted inventory statistics
    """
    stats_text = ""

    for builder, inventory in inventory_data.items():
        builder_display = builder.replace("dreamfinders", "Dream Finders").title()
        total = inventory.get("total_homes", 0)
        move_in = inventory.get("move_in_ready", 0)
        under_construction = inventory.get("under_construction", 0)
        communities = inventory.get("communities", 0)

        stats_text += f"{builder_display}\n"
        stats_text += f"  {total} homes available across {communities} communities\n"
        stats_text += f"  {move_in} move-in ready, {under_construction} under construction\n\n"

    return stats_text.strip()


def format_narrative(data: Dict[str, Any], insights: Dict[str, Any], analysis_type: str) -> str:
    """
    Format executive narrative summary focused on Dream Finders recovery strategy
    """
    narrative = "## Atlanta Market Competitive Analysis\n\n"

    # Get Dream Finders data
    df_financing = data["financing"].get("dream finders", {})
    df_inventory = data["inventory"].get("dream finders", {})
    df_pricing = data["pricing"].get("dream finders", {})

    # Competitive gaps analysis
    if insights.get("best_rate") and df_financing.get("rates"):
        best_rate = float(insights["best_rate"]["rate"].replace("%", ""))
        df_rate = float(df_financing["rates"][0]["rate"].replace("%", ""))
        rate_gap = df_rate - best_rate

        if rate_gap > 0:
            narrative += f"**Financing Gap:** Dream Finders' {df_rate}% rate is {rate_gap:.2f}% above {insights['best_rate']['builder'].title()}'s market-leading {insights['best_rate']['rate']}. This rate disadvantage is likely impacting buyer conversion.\n\n"
        else:
            narrative += f"**Financing Strength:** Dream Finders matches or beats the market with a competitive {df_rate}% rate.\n\n"

    # Inventory position
    if insights.get("market_leader") and df_inventory.get("total_homes"):
        leader_homes = insights["market_leader"]["homes"]
        df_homes = df_inventory["total_homes"]
        inventory_gap = leader_homes - df_homes

        narrative += f"**Inventory Challenge:** With only {df_homes} homes available vs. {insights['market_leader']['builder'].title()}'s {leader_homes}, Dream Finders has {inventory_gap} fewer units to sell. Limited inventory reduces market visibility and buyer options.\n\n"

    return narrative


# Test code removed - deploy to platform to use
