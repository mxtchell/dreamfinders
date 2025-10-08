"""
Layout templates for competitive analysis dashboard
"""

competitive_dashboard_layout = """{
    "inputVariables": [
        {
            "name": "dashboard_content",
            "isRequired": false,
            "defaultValue": "",
            "targets": [
                {
                    "elementName": "Content_Para",
                    "fieldName": "text"
                }
            ]
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
                "minHeight": "60px",
                "style": {
                    "background": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                    "padding": "30px",
                    "marginBottom": "0px"
                }
            },
            {
                "name": "Header_Title",
                "type": "Header",
                "text": "Competitive Intelligence Dashboard",
                "style": {
                    "fontSize": "28px",
                    "fontWeight": "700",
                    "color": "#ffffff",
                    "margin": "0"
                },
                "parentId": "Header_Container"
            },
            {
                "name": "Header_Subtitle",
                "type": "Paragraph",
                "text": "Real-time analysis of Atlanta homebuilder market",
                "style": {
                    "fontSize": "14px",
                    "color": "#ffffff",
                    "opacity": "0.9",
                    "margin": "5px 0 0 0"
                },
                "parentId": "Header_Container"
            },
            {
                "name": "Content_Container",
                "type": "FlexContainer",
                "direction": "column",
                "style": {
                    "padding": "30px",
                    "backgroundColor": "#ffffff",
                    "margin": "20px"
                }
            },
            {
                "name": "Content_Para",
                "type": "Paragraph",
                "text": "{{dashboard_content}}",
                "style": {
                    "fontSize": "13px",
                    "lineHeight": "1.5",
                    "whiteSpace": "pre-wrap",
                    "fontFamily": "Consolas, Monaco, 'Courier New', monospace",
                    "margin": "0",
                    "padding": "0",
                    "color": "#2d3748"
                },
                "parentId": "Content_Container"
            }
        ]
    }
}"""
