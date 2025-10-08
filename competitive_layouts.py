"""
Layout templates for competitive analysis dashboard
"""

competitive_dashboard_layout = """{
    "inputVariables": [
        {
            "name": "lennar_card",
            "isRequired": false,
            "defaultValue": "",
            "targets": [{"elementName": "Lennar_Card_Text", "fieldName": "text"}]
        },
        {
            "name": "lennar_sources",
            "isRequired": false,
            "defaultValue": "",
            "targets": [{"elementName": "Lennar_Sources_HTML", "fieldName": "html"}]
        },
        {
            "name": "meritage_card",
            "isRequired": false,
            "defaultValue": "",
            "targets": [{"elementName": "Meritage_Card_Text", "fieldName": "text"}]
        },
        {
            "name": "meritage_sources",
            "isRequired": false,
            "defaultValue": "",
            "targets": [{"elementName": "Meritage_Sources_HTML", "fieldName": "html"}]
        },
        {
            "name": "dreamfinders_card",
            "isRequired": false,
            "defaultValue": "",
            "targets": [{"elementName": "DreamFinders_Card_Text", "fieldName": "text"}]
        },
        {
            "name": "dreamfinders_sources",
            "isRequired": false,
            "defaultValue": "",
            "targets": [{"elementName": "DreamFinders_Sources_HTML", "fieldName": "html"}]
        },
        {
            "name": "pulte_card",
            "isRequired": false,
            "defaultValue": "",
            "targets": [{"elementName": "Pulte_Card_Text", "fieldName": "text"}]
        },
        {
            "name": "pulte_sources",
            "isRequired": false,
            "defaultValue": "",
            "targets": [{"elementName": "Pulte_Sources_HTML", "fieldName": "html"}]
        },
        {
            "name": "mortgage_chart",
            "isRequired": false,
            "defaultValue": "{}",
            "targets": [{"elementName": "MortgageChart", "fieldName": "options"}]
        }
    ],
    "layoutJson": {
        "type": "Document",
        "style": {
            "backgroundColor": "#f5f7fa",
            "width": "100%",
            "padding": "0px"
        },
        "children": [
            {
                "name": "Header_Container",
                "type": "FlexContainer",
                "direction": "column",
                "minHeight": "70px",
                "style": {
                    "background": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                    "padding": "20px 24px",
                    "marginBottom": "20px"
                }
            },
            {
                "name": "Header_Title",
                "type": "Header",
                "text": "Atlanta Homebuilder Competitive Analysis",
                "style": {
                    "fontSize": "26px",
                    "fontWeight": "600",
                    "color": "#ffffff",
                    "margin": "0"
                },
                "parentId": "Header_Container"
            },
            {
                "name": "Header_Subtitle",
                "type": "Paragraph",
                "text": "Special Financing, Inventory & Pricing Comparison",
                "style": {
                    "fontSize": "14px",
                    "color": "#ffffff",
                    "opacity": "0.9",
                    "margin": "6px 0 0 0"
                },
                "parentId": "Header_Container"
            },
            {
                "name": "ChartSection_Container",
                "type": "FlexContainer",
                "direction": "column",
                "style": {
                    "backgroundColor": "#ffffff",
                    "borderRadius": "8px",
                    "padding": "20px",
                    "margin": "0 32px 24px 32px",
                    "boxShadow": "0 2px 6px rgba(0,0,0,0.1)",
                    "border": "1px solid #e0e0e0"
                }
            },
            {
                "name": "MortgageChart",
                "type": "HighchartsChart",
                "options": {},
                "parentId": "ChartSection_Container"
            },
            {
                "name": "CardsRow_Container",
                "type": "FlexContainer",
                "direction": "row",
                "style": {
                    "padding": "0 32px 32px 32px",
                    "gap": "24px",
                    "flexWrap": "nowrap",
                    "alignItems": "flex-start"
                }
            },
            {
                "name": "Lennar_Card",
                "type": "FlexContainer",
                "direction": "column",
                "style": {
                    "flex": "1",
                    "backgroundColor": "#ffffff",
                    "borderRadius": "8px",
                    "padding": "20px",
                    "boxShadow": "0 2px 6px rgba(0,0,0,0.1)",
                    "border": "1px solid #e0e0e0"
                },
                "parentId": "CardsRow_Container"
            },
            {
                "name": "Lennar_Card_Title",
                "type": "Header",
                "text": "Lennar",
                "style": {
                    "fontSize": "20px",
                    "fontWeight": "700",
                    "color": "#1a1a1a",
                    "margin": "0 0 8px 0",
                    "borderBottom": "2px solid #667eea",
                    "paddingBottom": "6px"
                },
                "parentId": "Lennar_Card"
            },
            {
                "name": "Lennar_Card_Text",
                "type": "Paragraph",
                "text": "{{lennar_card}}",
                "style": {
                    "fontSize": "14px",
                    "lineHeight": "1.6",
                    "color": "#333333",
                    "margin": "0 0 12px 0",
                    "whiteSpace": "pre-wrap"
                },
                "parentId": "Lennar_Card"
            },
            {
                "name": "Lennar_Sources_HTML",
                "type": "Paragraph",
                "text": "{{lennar_sources}}",
                "parentId": "Lennar_Card"
            },
            {
                "name": "Meritage_Card",
                "type": "FlexContainer",
                "direction": "column",
                "style": {
                    "flex": "1",
                    "backgroundColor": "#ffffff",
                    "borderRadius": "8px",
                    "padding": "20px",
                    "boxShadow": "0 2px 6px rgba(0,0,0,0.1)",
                    "border": "1px solid #e0e0e0"
                },
                "parentId": "CardsRow_Container"
            },
            {
                "name": "Meritage_Card_Title",
                "type": "Header",
                "text": "Meritage",
                "style": {
                    "fontSize": "20px",
                    "fontWeight": "700",
                    "color": "#1a1a1a",
                    "margin": "0 0 8px 0",
                    "borderBottom": "2px solid #667eea",
                    "paddingBottom": "6px"
                },
                "parentId": "Meritage_Card"
            },
            {
                "name": "Meritage_Card_Text",
                "type": "Paragraph",
                "text": "{{meritage_card}}",
                "style": {
                    "fontSize": "14px",
                    "lineHeight": "1.6",
                    "color": "#333333",
                    "margin": "0 0 12px 0",
                    "whiteSpace": "pre-wrap"
                },
                "parentId": "Meritage_Card"
            },
            {
                "name": "Meritage_Sources_HTML",
                "type": "Paragraph",
                "text": "{{meritage_sources}}",
                "parentId": "Meritage_Card"
            },
            {
                "name": "DreamFinders_Card",
                "type": "FlexContainer",
                "direction": "column",
                "style": {
                    "flex": "1",
                    "backgroundColor": "#ffffff",
                    "borderRadius": "8px",
                    "padding": "20px",
                    "boxShadow": "0 2px 6px rgba(0,0,0,0.1)",
                    "border": "1px solid #e0e0e0"
                },
                "parentId": "CardsRow_Container"
            },
            {
                "name": "DreamFinders_Card_Title",
                "type": "Header",
                "text": "Dream Finders",
                "style": {
                    "fontSize": "20px",
                    "fontWeight": "700",
                    "color": "#1a1a1a",
                    "margin": "0 0 8px 0",
                    "borderBottom": "2px solid #667eea",
                    "paddingBottom": "6px"
                },
                "parentId": "DreamFinders_Card"
            },
            {
                "name": "DreamFinders_Card_Text",
                "type": "Paragraph",
                "text": "{{dreamfinders_card}}",
                "style": {
                    "fontSize": "14px",
                    "lineHeight": "1.6",
                    "color": "#333333",
                    "margin": "0 0 12px 0",
                    "whiteSpace": "pre-wrap"
                },
                "parentId": "DreamFinders_Card"
            },
            {
                "name": "DreamFinders_Sources_HTML",
                "type": "Paragraph",
                "text": "{{dreamfinders_sources}}",
                "parentId": "DreamFinders_Card"
            },
            {
                "name": "Pulte_Card",
                "type": "FlexContainer",
                "direction": "column",
                "style": {
                    "flex": "1",
                    "backgroundColor": "#ffffff",
                    "borderRadius": "8px",
                    "padding": "20px",
                    "boxShadow": "0 2px 6px rgba(0,0,0,0.1)",
                    "border": "1px solid #e0e0e0"
                },
                "parentId": "CardsRow_Container"
            },
            {
                "name": "Pulte_Card_Title",
                "type": "Header",
                "text": "Pulte",
                "style": {
                    "fontSize": "20px",
                    "fontWeight": "700",
                    "color": "#1a1a1a",
                    "margin": "0 0 8px 0",
                    "borderBottom": "2px solid #667eea",
                    "paddingBottom": "6px"
                },
                "parentId": "Pulte_Card"
            },
            {
                "name": "Pulte_Card_Text",
                "type": "Paragraph",
                "text": "{{pulte_card}}",
                "style": {
                    "fontSize": "14px",
                    "lineHeight": "1.6",
                    "color": "#333333",
                    "margin": "0 0 12px 0",
                    "whiteSpace": "pre-wrap"
                },
                "parentId": "Pulte_Card"
            },
            {
                "name": "Pulte_Sources_HTML",
                "type": "Paragraph",
                "text": "{{pulte_sources}}",
                "parentId": "Pulte_Card"
            }
        ]
    }
}"""
