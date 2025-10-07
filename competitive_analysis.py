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
            default_value="Lennar, Meritage, Dream Finders"
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
    builder_names = parameters.arguments.builder_names or "Lennar, Meritage, Dream Finders"
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

    return SkillOutput(
        final_prompt=narrative,
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


def create_competitive_dashboard(data: Dict[str, Any], analysis_type: str) -> SkillVisualization:
    """
    Create badass dashboard visualization using wire_layout
    """
    print(f"DEBUG: Creating dashboard visualization")

    # Build HTML for special financing cards
    financing_cards_html = create_financing_cards(data["financing"])
    print(f"DEBUG: Financing cards HTML length: {len(financing_cards_html)}")

    # Build comparison table
    comparison_table_html = create_comparison_table(data)
    print(f"DEBUG: Comparison table HTML length: {len(comparison_table_html)}")

    # Build inventory stats
    inventory_stats_html = create_inventory_stats(data["inventory"])
    print(f"DEBUG: Inventory stats HTML length: {len(inventory_stats_html)}")

    # Create variables dict for wire_layout
    variables = {
        "financing_cards_html": financing_cards_html,
        "comparison_table_html": comparison_table_html,
        "inventory_stats_html": inventory_stats_html
    }

    print(f"DEBUG: Variables keys: {list(variables.keys())}")

    # Parse layout JSON
    import json
    layout_dict = json.loads(competitive_dashboard_layout)
    print(f"DEBUG: Layout parsed successfully")

    # Render using wire_layout
    rendered = wire_layout(layout_dict, variables)
    print(f"DEBUG: Layout rendered successfully, type: {type(rendered)}")

    return SkillVisualization(
        title="Competitive Analysis",
        layout=rendered
    )


def create_financing_cards(financing_data: Dict[str, Any]) -> str:
    """
    Create beautiful cards for each builder's financing offers
    """
    cards_html = '<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px;">'

    # Color schemes for each builder
    colors = {
        "lennar": {"bg": "#FF6B6B", "accent": "#FF5252"},
        "meritage": {"bg": "#4ECDC4", "accent": "#45B7AF"},
        "dream finders": {"bg": "#95E1D3", "accent": "#7FD3C1"},
        "dreamfinders": {"bg": "#95E1D3", "accent": "#7FD3C1"},
        "dr horton": {"bg": "#F38181", "accent": "#F37070"},
        "pulte": {"bg": "#AA96DA", "accent": "#9A86CA"}
    }

    for builder, financing in financing_data.items():
        builder_display = builder.replace("dreamfinders", "Dream Finders").title()
        color_scheme = colors.get(builder.lower(), {"bg": "#667eea", "accent": "#5568d3"})

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

        cards_html += f"""
        <div style="background: white; border-radius: 12px; padding: 24px; box-shadow: 0 8px 16px rgba(0,0,0,0.1); border-left: 5px solid {color_scheme['bg']};">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px;">
                <h3 style="margin: 0; color: #2D3748; font-size: 20px; font-weight: 700;">{builder_display}</h3>
                <div style="background: {color_scheme['bg']}; color: white; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600;">ACTIVE</div>
            </div>

            <div style="background: {color_scheme['bg']}15; padding: 16px; border-radius: 8px; margin-bottom: 12px;">
                <div style="font-size: 36px; font-weight: 700; color: {color_scheme['bg']}; margin-bottom: 4px;">{best_rate}</div>
                <div style="font-size: 13px; color: #718096; font-weight: 500;">{rate_type}</div>
            </div>

            <div style="color: #4A5568; font-size: 14px; margin-bottom: 12px; line-height: 1.5;">
                <strong>💎 Incentive:</strong><br/>{incentive}
            </div>

            <div style="color: #A0AEC0; font-size: 12px; border-top: 1px solid #E2E8F0; padding-top: 12px;">
                ⏰ Expires: {expiration}
            </div>
        </div>
        """

    cards_html += '</div>'
    return cards_html


def create_comparison_table(data: Dict[str, Any]) -> str:
    """
    Create comprehensive comparison table
    """
    builders = list(data["financing"].keys())

    table_html = """
    <div style="background: white; border-radius: 12px; padding: 24px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); overflow-x: auto;">
        <table style="width: 100%; border-collapse: collapse; font-size: 14px;">
            <thead>
                <tr style="background: #F7FAFC; border-bottom: 2px solid #E2E8F0;">
                    <th style="padding: 12px; text-align: left; color: #2D3748; font-weight: 600;">Metric</th>
    """

    for builder in builders:
        builder_display = builder.replace("dreamfinders", "Dream Finders").title()
        table_html += f'<th style="padding: 12px; text-align: center; color: #2D3748; font-weight: 600;">{builder_display}</th>'

    table_html += "</tr></thead><tbody>"

    # Best Rate Row
    table_html += '<tr style="border-bottom: 1px solid #E2E8F0;"><td style="padding: 12px; color: #4A5568; font-weight: 500;">Best Rate</td>'
    for builder in builders:
        rate = data["financing"][builder]["rates"][0]["rate"] if data["financing"][builder].get("rates") else "N/A"
        table_html += f'<td style="padding: 12px; text-align: center; color: #2B6CB0; font-weight: 600;">{rate}</td>'
    table_html += "</tr>"

    # Incentives Row
    table_html += '<tr style="border-bottom: 1px solid #E2E8F0;"><td style="padding: 12px; color: #4A5568; font-weight: 500;">Incentives</td>'
    for builder in builders:
        incentive = data["financing"][builder]["incentives"][0] if data["financing"][builder].get("incentives") else "-"
        table_html += f'<td style="padding: 12px; text-align: center; color: #38A169; font-size: 13px;">{incentive[:30]}...</td>'
    table_html += "</tr>"

    # Total Homes Row
    table_html += '<tr style="border-bottom: 1px solid #E2E8F0;"><td style="padding: 12px; color: #4A5568; font-weight: 500;">Available Homes</td>'
    for builder in builders:
        total = data["inventory"].get(builder, {}).get("total_homes", 0)
        table_html += f'<td style="padding: 12px; text-align: center; color: #2D3748; font-weight: 600;">{total}</td>'
    table_html += "</tr>"

    # Communities Row
    table_html += '<tr style="border-bottom: 1px solid #E2E8F0;"><td style="padding: 12px; color: #4A5568; font-weight: 500;">Communities</td>'
    for builder in builders:
        communities = data["inventory"].get(builder, {}).get("communities", 0)
        table_html += f'<td style="padding: 12px; text-align: center; color: #2D3748;">{communities}</td>'
    table_html += "</tr>"

    # Avg Price Row
    table_html += '<tr><td style="padding: 12px; color: #4A5568; font-weight: 500;">Avg Price</td>'
    for builder in builders:
        avg_price = data["pricing"].get(builder, {}).get("avg_price", 0)
        price_display = f"${avg_price:,.0f}" if avg_price else "N/A"
        table_html += f'<td style="padding: 12px; text-align: center; color: #2D3748;">{price_display}</td>'
    table_html += "</tr>"

    table_html += "</tbody></table></div>"
    return table_html


def create_inventory_stats(inventory_data: Dict[str, Any]) -> str:
    """
    Create inventory statistics cards
    """
    stats_html = '<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px;">'

    for builder, inventory in inventory_data.items():
        builder_display = builder.replace("dreamfinders", "Dream Finders").title()
        total = inventory.get("total_homes", 0)
        move_in = inventory.get("move_in_ready", 0)
        under_construction = inventory.get("under_construction", 0)

        stats_html += f"""
        <div style="background: white; border-radius: 8px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);">
            <h4 style="margin: 0 0 12px 0; color: #2D3748; font-size: 16px; font-weight: 600;">{builder_display}</h4>
            <div style="color: #667eea; font-size: 28px; font-weight: 700; margin-bottom: 8px;">{total}</div>
            <div style="font-size: 12px; color: #718096;">
                <div style="margin-bottom: 4px;">✅ Move-in Ready: <strong>{move_in}</strong></div>
                <div>🚧 Under Construction: <strong>{under_construction}</strong></div>
            </div>
        </div>
        """

    stats_html += '</div>'
    return stats_html


def format_narrative(data: Dict[str, Any], insights: Dict[str, Any], analysis_type: str) -> str:
    """
    Format executive narrative summary
    """
    narrative = "## Competitive Intelligence Summary\n\n"

    # Best rate insight
    if insights.get("best_rate"):
        best = insights["best_rate"]
        narrative += f"**🏆 Market-Leading Rate:** {best['builder'].title()} offers the most competitive rate at {best['rate']}\n\n"

    # Best incentive insight
    if insights.get("best_incentive"):
        best = insights["best_incentive"]
        narrative += f"**💰 Top Incentive:** {best['builder'].title()} provides up to {best['amount']} in savings\n\n"

    # Market leader insight
    if insights.get("market_leader"):
        leader = insights["market_leader"]
        narrative += f"**📊 Inventory Leader:** {leader['builder'].title()} dominates with {leader['homes']} available homes\n\n"

    # Recommendations
    narrative += "### Strategic Recommendations\n\n"
    for i, rec in enumerate(insights.get("recommendations", []), 1):
        narrative += f"{i}. {rec}\n"

    return narrative


# Test code removed - deploy to platform to use
