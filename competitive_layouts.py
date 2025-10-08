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
            "name": "meritage_card",
            "isRequired": false,
            "defaultValue": "",
            "targets": [{"elementName": "Meritage_Card_Text", "fieldName": "text"}]
        },
        {
            "name": "dreamfinders_card",
            "isRequired": false,
            "defaultValue": "",
            "targets": [{"elementName": "DreamFinders_Card_Text", "fieldName": "text"}]
        },
        {
            "name": "drhorton_card",
            "isRequired": false,
            "defaultValue": "",
            "targets": [{"elementName": "DRHorton_Card_Text", "fieldName": "text"}]
        },
        {
            "name": "pulte_card",
            "isRequired": false,
            "defaultValue": "",
            "targets": [{"elementName": "Pulte_Card_Text", "fieldName": "text"}]
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
                "name": "CardsRow_Container",
                "type": "FlexContainer",
                "direction": "row",
                "minHeight": "calc(100vh - 120px)",
                "style": {
                    "padding": "0 32px 32px 32px",
                    "gap": "24px",
                    "flexWrap": "nowrap"
                }
            },
            {
                "name": "Lennar_Card",
                "type": "FlexContainer",
                "direction": "column",
                "minHeight": "100%",
                "style": {
                    "flex": "1",
                    "backgroundColor": "#ffffff",
                    "borderRadius": "12px",
                    "padding": "32px",
                    "boxShadow": "0 4px 12px rgba(0,0,0,0.15)",
                    "border": "2px solid #e0e0e0"
                },
                "parentId": "CardsRow_Container"
            },
            {
                "name": "Lennar_Card_Title",
                "type": "Header",
                "text": "Lennar",
                "style": {
                    "fontSize": "28px",
                    "fontWeight": "700",
                    "color": "#1a1a1a",
                    "margin": "0 0 8px 0",
                    "borderBottom": "3px solid #667eea",
                    "paddingBottom": "8px"
                },
                "parentId": "Lennar_Card"
            },
            {
                "name": "Lennar_Card_Text",
                "type": "Paragraph",
                "text": "{{lennar_card}}",
                "style": {
                    "fontSize": "18px",
                    "lineHeight": "1.8",
                    "color": "#333333",
                    "margin": "0",
                    "whiteSpace": "pre-wrap"
                },
                "parentId": "Lennar_Card"
            },
            {
                "name": "Meritage_Card",
                "type": "FlexContainer",
                "direction": "column",
                "minHeight": "100%",
                "style": {
                    "flex": "1",
                    "backgroundColor": "#ffffff",
                    "borderRadius": "12px",
                    "padding": "32px",
                    "boxShadow": "0 4px 12px rgba(0,0,0,0.15)",
                    "border": "2px solid #e0e0e0"
                },
                "parentId": "CardsRow_Container"
            },
            {
                "name": "Meritage_Card_Title",
                "type": "Header",
                "text": "Meritage",
                "style": {
                    "fontSize": "28px",
                    "fontWeight": "700",
                    "color": "#1a1a1a",
                    "margin": "0 0 8px 0",
                    "borderBottom": "3px solid #667eea",
                    "paddingBottom": "8px"
                },
                "parentId": "Meritage_Card"
            },
            {
                "name": "Meritage_Card_Text",
                "type": "Paragraph",
                "text": "{{meritage_card}}",
                "style": {
                    "fontSize": "18px",
                    "lineHeight": "1.8",
                    "color": "#333333",
                    "margin": "0",
                    "whiteSpace": "pre-wrap"
                },
                "parentId": "Meritage_Card"
            },
            {
                "name": "DreamFinders_Card",
                "type": "FlexContainer",
                "direction": "column",
                "minHeight": "100%",
                "style": {
                    "flex": "1",
                    "backgroundColor": "#ffffff",
                    "borderRadius": "12px",
                    "padding": "32px",
                    "boxShadow": "0 4px 12px rgba(0,0,0,0.15)",
                    "border": "2px solid #e0e0e0"
                },
                "parentId": "CardsRow_Container"
            },
            {
                "name": "DreamFinders_Card_Title",
                "type": "Header",
                "text": "Dream Finders",
                "style": {
                    "fontSize": "28px",
                    "fontWeight": "700",
                    "color": "#1a1a1a",
                    "margin": "0 0 8px 0",
                    "borderBottom": "3px solid #667eea",
                    "paddingBottom": "8px"
                },
                "parentId": "DreamFinders_Card"
            },
            {
                "name": "DreamFinders_Card_Text",
                "type": "Paragraph",
                "text": "{{dreamfinders_card}}",
                "style": {
                    "fontSize": "18px",
                    "lineHeight": "1.8",
                    "color": "#333333",
                    "margin": "0",
                    "whiteSpace": "pre-wrap"
                },
                "parentId": "DreamFinders_Card"
            },
            {
                "name": "DRHorton_Card",
                "type": "FlexContainer",
                "direction": "column",
                "minHeight": "100%",
                "style": {
                    "flex": "1",
                    "backgroundColor": "#ffffff",
                    "borderRadius": "12px",
                    "padding": "32px",
                    "boxShadow": "0 4px 12px rgba(0,0,0,0.15)",
                    "border": "2px solid #e0e0e0"
                },
                "parentId": "CardsRow_Container"
            },
            {
                "name": "DRHorton_Card_Title",
                "type": "Header",
                "text": "DR Horton",
                "style": {
                    "fontSize": "28px",
                    "fontWeight": "700",
                    "color": "#1a1a1a",
                    "margin": "0 0 8px 0",
                    "borderBottom": "3px solid #667eea",
                    "paddingBottom": "8px"
                },
                "parentId": "DRHorton_Card"
            },
            {
                "name": "DRHorton_Card_Text",
                "type": "Paragraph",
                "text": "{{drhorton_card}}",
                "style": {
                    "fontSize": "18px",
                    "lineHeight": "1.8",
                    "color": "#333333",
                    "margin": "0",
                    "whiteSpace": "pre-wrap"
                },
                "parentId": "DRHorton_Card"
            },
            {
                "name": "Pulte_Card",
                "type": "FlexContainer",
                "direction": "column",
                "minHeight": "100%",
                "style": {
                    "flex": "1",
                    "backgroundColor": "#ffffff",
                    "borderRadius": "12px",
                    "padding": "32px",
                    "boxShadow": "0 4px 12px rgba(0,0,0,0.15)",
                    "border": "2px solid #e0e0e0"
                },
                "parentId": "CardsRow_Container"
            },
            {
                "name": "Pulte_Card_Title",
                "type": "Header",
                "text": "Pulte",
                "style": {
                    "fontSize": "28px",
                    "fontWeight": "700",
                    "color": "#1a1a1a",
                    "margin": "0 0 8px 0",
                    "borderBottom": "3px solid #667eea",
                    "paddingBottom": "8px"
                },
                "parentId": "Pulte_Card"
            },
            {
                "name": "Pulte_Card_Text",
                "type": "Paragraph",
                "text": "{{pulte_card}}",
                "style": {
                    "fontSize": "18px",
                    "lineHeight": "1.8",
                    "color": "#333333",
                    "margin": "0",
                    "whiteSpace": "pre-wrap"
                },
                "parentId": "Pulte_Card"
            }
        ]
    }
}"""
