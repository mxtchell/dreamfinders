"""
Layout templates for competitive analysis dashboard
"""

competitive_dashboard_layout = """{
    "inputVariables": [
        {
            "name": "market_leader",
            "isRequired": false,
            "defaultValue": "N/A",
            "targets": [{"elementName": "MarketLeader_Value", "fieldName": "text"}]
        },
        {
            "name": "best_rate",
            "isRequired": false,
            "defaultValue": "N/A",
            "targets": [{"elementName": "BestRate_Value", "fieldName": "text"}]
        },
        {
            "name": "total_homes",
            "isRequired": false,
            "defaultValue": "0",
            "targets": [{"elementName": "TotalHomes_Value", "fieldName": "text"}]
        },
        {
            "name": "avg_incentive",
            "isRequired": false,
            "defaultValue": "$0",
            "targets": [{"elementName": "AvgIncentive_Value", "fieldName": "text"}]
        },
        {
            "name": "financing_details",
            "isRequired": false,
            "defaultValue": "",
            "targets": [{"elementName": "FinancingDetails_Text", "fieldName": "text"}]
        },
        {
            "name": "comparison_table",
            "isRequired": false,
            "defaultValue": "",
            "targets": [{"elementName": "ComparisonTable_Text", "fieldName": "text"}]
        },
        {
            "name": "inventory_details",
            "isRequired": false,
            "defaultValue": "",
            "targets": [{"elementName": "InventoryDetails_Text", "fieldName": "text"}]
        }
    ],
    "layoutJson": {
        "type": "Document",
        "style": {
            "backgroundColor": "#f8f9fa",
            "width": "100%",
            "padding": "0px"
        },
        "children": [
            {
                "name": "Header_Container",
                "type": "FlexContainer",
                "direction": "column",
                "minHeight": "80px",
                "style": {
                    "background": "linear-gradient(135deg, #4A90E2 0%, #357ABD 100%)",
                    "padding": "24px 32px",
                    "marginBottom": "24px",
                    "boxShadow": "0 2px 4px rgba(0,0,0,0.1)"
                }
            },
            {
                "name": "Header_Title",
                "type": "Header",
                "text": "Competitive Intelligence Dashboard",
                "style": {
                    "fontSize": "32px",
                    "fontWeight": "600",
                    "color": "#ffffff",
                    "margin": "0",
                    "letterSpacing": "-0.5px"
                },
                "parentId": "Header_Container"
            },
            {
                "name": "Header_Subtitle",
                "type": "Paragraph",
                "text": "Atlanta Homebuilder Market Analysis",
                "style": {
                    "fontSize": "16px",
                    "color": "#ffffff",
                    "opacity": "0.95",
                    "margin": "8px 0 0 0",
                    "fontWeight": "400"
                },
                "parentId": "Header_Container"
            },
            {
                "name": "MetricsRow_Container",
                "type": "FlexContainer",
                "direction": "row",
                "minHeight": "120px",
                "style": {
                    "padding": "0 32px",
                    "gap": "16px",
                    "marginBottom": "24px"
                }
            },
            {
                "name": "MarketLeader_Card",
                "type": "FlexContainer",
                "direction": "column",
                "minHeight": "100px",
                "style": {
                    "flex": "1",
                    "backgroundColor": "#E3F2FD",
                    "borderRadius": "8px",
                    "padding": "20px",
                    "borderLeft": "4px solid #2196F3",
                    "boxShadow": "0 1px 3px rgba(0,0,0,0.1)"
                },
                "parentId": "MetricsRow_Container"
            },
            {
                "name": "MarketLeader_Label",
                "type": "Paragraph",
                "text": "Market Leader",
                "style": {
                    "fontSize": "13px",
                    "fontWeight": "600",
                    "color": "#546e7a",
                    "margin": "0 0 8px 0",
                    "textTransform": "uppercase",
                    "letterSpacing": "0.5px"
                },
                "parentId": "MarketLeader_Card"
            },
            {
                "name": "MarketLeader_Value",
                "type": "Paragraph",
                "text": "{{market_leader}}",
                "style": {
                    "fontSize": "28px",
                    "fontWeight": "700",
                    "color": "#1565C0",
                    "margin": "0"
                },
                "parentId": "MarketLeader_Card"
            },
            {
                "name": "BestRate_Card",
                "type": "FlexContainer",
                "direction": "column",
                "minHeight": "100px",
                "style": {
                    "flex": "1",
                    "backgroundColor": "#E8F5E9",
                    "borderRadius": "8px",
                    "padding": "20px",
                    "borderLeft": "4px solid #4CAF50",
                    "boxShadow": "0 1px 3px rgba(0,0,0,0.1)"
                },
                "parentId": "MetricsRow_Container"
            },
            {
                "name": "BestRate_Label",
                "type": "Paragraph",
                "text": "Best Rate",
                "style": {
                    "fontSize": "13px",
                    "fontWeight": "600",
                    "color": "#546e7a",
                    "margin": "0 0 8px 0",
                    "textTransform": "uppercase",
                    "letterSpacing": "0.5px"
                },
                "parentId": "BestRate_Card"
            },
            {
                "name": "BestRate_Value",
                "type": "Paragraph",
                "text": "{{best_rate}}",
                "style": {
                    "fontSize": "28px",
                    "fontWeight": "700",
                    "color": "#2E7D32",
                    "margin": "0"
                },
                "parentId": "BestRate_Card"
            },
            {
                "name": "TotalHomes_Card",
                "type": "FlexContainer",
                "direction": "column",
                "minHeight": "100px",
                "style": {
                    "flex": "1",
                    "backgroundColor": "#FFF3E0",
                    "borderRadius": "8px",
                    "padding": "20px",
                    "borderLeft": "4px solid #FF9800",
                    "boxShadow": "0 1px 3px rgba(0,0,0,0.1)"
                },
                "parentId": "MetricsRow_Container"
            },
            {
                "name": "TotalHomes_Label",
                "type": "Paragraph",
                "text": "Total Homes",
                "style": {
                    "fontSize": "13px",
                    "fontWeight": "600",
                    "color": "#546e7a",
                    "margin": "0 0 8px 0",
                    "textTransform": "uppercase",
                    "letterSpacing": "0.5px"
                },
                "parentId": "TotalHomes_Card"
            },
            {
                "name": "TotalHomes_Value",
                "type": "Paragraph",
                "text": "{{total_homes}}",
                "style": {
                    "fontSize": "28px",
                    "fontWeight": "700",
                    "color": "#E65100",
                    "margin": "0"
                },
                "parentId": "TotalHomes_Card"
            },
            {
                "name": "AvgIncentive_Card",
                "type": "FlexContainer",
                "direction": "column",
                "minHeight": "100px",
                "style": {
                    "flex": "1",
                    "backgroundColor": "#F3E5F5",
                    "borderRadius": "8px",
                    "padding": "20px",
                    "borderLeft": "4px solid #9C27B0",
                    "boxShadow": "0 1px 3px rgba(0,0,0,0.1)"
                },
                "parentId": "MetricsRow_Container"
            },
            {
                "name": "AvgIncentive_Label",
                "type": "Paragraph",
                "text": "Best Incentive",
                "style": {
                    "fontSize": "13px",
                    "fontWeight": "600",
                    "color": "#546e7a",
                    "margin": "0 0 8px 0",
                    "textTransform": "uppercase",
                    "letterSpacing": "0.5px"
                },
                "parentId": "AvgIncentive_Card"
            },
            {
                "name": "AvgIncentive_Value",
                "type": "Paragraph",
                "text": "{{avg_incentive}}",
                "style": {
                    "fontSize": "28px",
                    "fontWeight": "700",
                    "color": "#6A1B9A",
                    "margin": "0"
                },
                "parentId": "AvgIncentive_Card"
            },
            {
                "name": "FinancingSection_Container",
                "type": "FlexContainer",
                "direction": "column",
                "minHeight": "100px",
                "style": {
                    "backgroundColor": "#ffffff",
                    "borderRadius": "8px",
                    "padding": "24px",
                    "margin": "0 32px 24px 32px",
                    "boxShadow": "0 1px 3px rgba(0,0,0,0.1)"
                }
            },
            {
                "name": "FinancingSection_Header",
                "type": "Header",
                "text": "Current Special Financing Offers",
                "style": {
                    "fontSize": "20px",
                    "fontWeight": "600",
                    "color": "#212121",
                    "margin": "0 0 16px 0"
                },
                "parentId": "FinancingSection_Container"
            },
            {
                "name": "FinancingDetails_Text",
                "type": "Paragraph",
                "text": "{{financing_details}}",
                "style": {
                    "fontSize": "14px",
                    "lineHeight": "1.8",
                    "color": "#424242",
                    "margin": "0",
                    "whiteSpace": "pre-wrap",
                    "fontFamily": "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
                },
                "parentId": "FinancingSection_Container"
            },
            {
                "name": "ComparisonSection_Container",
                "type": "FlexContainer",
                "direction": "column",
                "minHeight": "100px",
                "style": {
                    "backgroundColor": "#ffffff",
                    "borderRadius": "8px",
                    "padding": "24px",
                    "margin": "0 32px 24px 32px",
                    "boxShadow": "0 1px 3px rgba(0,0,0,0.1)"
                }
            },
            {
                "name": "ComparisonSection_Header",
                "type": "Header",
                "text": "Builder Comparison Matrix",
                "style": {
                    "fontSize": "20px",
                    "fontWeight": "600",
                    "color": "#212121",
                    "margin": "0 0 16px 0"
                },
                "parentId": "ComparisonSection_Container"
            },
            {
                "name": "ComparisonTable_Text",
                "type": "Paragraph",
                "text": "{{comparison_table}}",
                "style": {
                    "fontSize": "13px",
                    "lineHeight": "1.6",
                    "color": "#424242",
                    "margin": "0",
                    "whiteSpace": "pre-wrap",
                    "fontFamily": "Consolas, Monaco, 'Courier New', monospace"
                },
                "parentId": "ComparisonSection_Container"
            },
            {
                "name": "InventorySection_Container",
                "type": "FlexContainer",
                "direction": "column",
                "minHeight": "100px",
                "style": {
                    "backgroundColor": "#ffffff",
                    "borderRadius": "8px",
                    "padding": "24px",
                    "margin": "0 32px 32px 32px",
                    "boxShadow": "0 1px 3px rgba(0,0,0,0.1)"
                }
            },
            {
                "name": "InventorySection_Header",
                "type": "Header",
                "text": "Inventory Breakdown",
                "style": {
                    "fontSize": "20px",
                    "fontWeight": "600",
                    "color": "#212121",
                    "margin": "0 0 16px 0"
                },
                "parentId": "InventorySection_Container"
            },
            {
                "name": "InventoryDetails_Text",
                "type": "Paragraph",
                "text": "{{inventory_details}}",
                "style": {
                    "fontSize": "14px",
                    "lineHeight": "1.8",
                    "color": "#424242",
                    "margin": "0",
                    "whiteSpace": "pre-wrap",
                    "fontFamily": "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
                },
                "parentId": "InventorySection_Container"
            }
        ]
    }
}"""
