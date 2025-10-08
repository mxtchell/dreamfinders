"""
Layout templates for competitive analysis dashboard
"""

competitive_dashboard_layout = """{
    "inputVariables": [
        {
            "name": "financing_cards_html",
            "isRequired": false,
            "defaultValue": "",
            "targets": [
                {
                    "elementName": "Financing_Cards",
                    "fieldName": "text"
                }
            ]
        },
        {
            "name": "comparison_table_html",
            "isRequired": false,
            "defaultValue": "",
            "targets": [
                {
                    "elementName": "Comparison_Table",
                    "fieldName": "text"
                }
            ]
        },
        {
            "name": "inventory_stats_html",
            "isRequired": false,
            "defaultValue": "",
            "targets": [
                {
                    "elementName": "Inventory_Stats",
                    "fieldName": "text"
                }
            ]
        }
    ],
    "layoutJson": {
        "type": "Document",
        "gap": "0px",
        "style": {
            "backgroundColor": "#f5f7fa",
            "width": "100%",
            "height": "max-content",
            "padding": "0px"
        },
        "children": [
            {
                "name": "Header_Container",
                "type": "FlexContainer",
                "direction": "column",
                "style": {
                    "background": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                    "padding": "40px",
                    "marginBottom": "0px"
                }
            },
            {
                "name": "Header_Title",
                "type": "Header",
                "text": "Competitive Intelligence Dashboard",
                "style": {
                    "fontSize": "32px",
                    "fontWeight": "700",
                    "color": "#ffffff",
                    "margin": "0 0 10px 0"
                },
                "parentId": "Header_Container"
            },
            {
                "name": "Header_Subtitle",
                "type": "Paragraph",
                "text": "Real-time analysis of Atlanta homebuilder market",
                "style": {
                    "fontSize": "16px",
                    "color": "#ffffff",
                    "opacity": "0.9",
                    "margin": "0"
                },
                "parentId": "Header_Container"
            },
            {
                "name": "Financing_Section",
                "type": "FlexContainer",
                "direction": "column",
                "style": {
                    "padding": "40px 40px 20px 40px"
                }
            },
            {
                "name": "Financing_Title",
                "type": "Header",
                "text": "Current Special Financing Offers",
                "style": {
                    "fontSize": "24px",
                    "fontWeight": "600",
                    "color": "#2D3748",
                    "marginBottom": "10px"
                },
                "parentId": "Financing_Section"
            },
            {
                "name": "Financing_Cards",
                "type": "Markdown",
                "text": "{{financing_cards_html}}",
                "style": {
                    "margin": "0",
                    "padding": "0"
                },
                "parentId": "Financing_Section"
            },
            {
                "name": "Table_Section",
                "type": "FlexContainer",
                "direction": "column",
                "style": {
                    "padding": "0 40px 20px 40px"
                }
            },
            {
                "name": "Table_Title",
                "type": "Header",
                "text": "Builder Comparison Matrix",
                "style": {
                    "fontSize": "24px",
                    "fontWeight": "600",
                    "color": "#2D3748",
                    "marginBottom": "10px"
                },
                "parentId": "Table_Section"
            },
            {
                "name": "Comparison_Table",
                "type": "Markdown",
                "text": "{{comparison_table_html}}",
                "style": {
                    "margin": "0",
                    "padding": "0"
                },
                "parentId": "Table_Section"
            },
            {
                "name": "Inventory_Section",
                "type": "FlexContainer",
                "direction": "column",
                "style": {
                    "padding": "0 40px 40px 40px"
                }
            },
            {
                "name": "Inventory_Title",
                "type": "Header",
                "text": "Inventory Breakdown",
                "style": {
                    "fontSize": "24px",
                    "fontWeight": "600",
                    "color": "#2D3748",
                    "marginBottom": "10px"
                },
                "parentId": "Inventory_Section"
            },
            {
                "name": "Inventory_Stats",
                "type": "Markdown",
                "text": "{{inventory_stats_html}}",
                "style": {
                    "margin": "0",
                    "padding": "0"
                },
                "parentId": "Inventory_Section"
            }
        ]
    }
}"""
