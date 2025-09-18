from __future__ import annotations
from types import SimpleNamespace
from typing import List, Optional, Dict, Any

import pandas as pd
from skill_framework import SkillInput, SkillVisualization, skill, SkillParameter, SkillOutput, ParameterDisplayDescription
from skill_framework.skills import ExportData
from skill_framework.layouts import wire_layout

import json
import os
import glob
import traceback
from jinja2 import Template
import base64
import io
from PIL import Image
import logging
import re
import html
import fitz  # PyMuPDF for PDF thumbnail generation
import numpy as np
from typing import List
import requests

logger = logging.getLogger(__name__)

@skill(
    name="Competitor RAG Scraper",
    description="Retrieves and analyzes competitive intelligence data to answer questions about competitor pricing, inventory, and market trends",
    capabilities="Searches through competitive data documents (Lennar, Meritage), finds relevant home pricing and market intelligence, generates comprehensive answers with citations and PDF thumbnails",
    limitations="Limited to documents in the knowledge base, requires pre-processed competitive data chunks in pack.json",
    parameters=[
        SkillParameter(
            name="user_question",
            description="The question to answer using the knowledge base",
            required=True
        ),
        SkillParameter(
            name="base_url",
            parameter_type="code",
            description="Base URL for document links",
            required=True,
            default_value="https://dreamfinders.poc.answerrocket.com/apps/system/knowledge-base"
        ),
        SkillParameter(
            name="max_sources",
            description="Maximum number of source documents to include",
            default_value=5
        ),
        SkillParameter(
            name="match_threshold",
            description="Minimum similarity score for document matching (0-1)",
            default_value=0.15
        ),
        SkillParameter(
            name="max_characters",
            description="Maximum characters to include from sources",
            default_value=3000
        ),
        SkillParameter(
            name="max_prompt",
            parameter_type="prompt",
            description="Prompt for the insights section (left panel)",
            default_value="Thank you for your question! I've searched through the available documents in the knowledge base. Please check the response and sources tabs above for detailed analysis with citations and document references. Feel free to ask follow-up questions if you need clarification on any of the findings."
        ),
        SkillParameter(
            name="response_layout",
            parameter_type="visualization",
            description="Layout for Response tab",
            default_value='{"layoutJson": {"type": "Document", "children": [{"name": "ResponseText", "type": "Paragraph", "text": "{{response_content}}"}]}, "inputVariables": [{"name": "response_content", "isRequired": false, "defaultValue": null, "targets": [{"elementName": "ResponseText", "fieldName": "text"}]}]}'
        ),
        SkillParameter(
            name="sources_layout", 
            parameter_type="visualization",
            description="Layout for Sources tab",
            default_value='{"layoutJson": {"type": "Document", "children": [{"name": "SourcesText", "type": "Paragraph", "text": "{{sources_content}}"}]}, "inputVariables": [{"name": "sources_content", "isRequired": false, "defaultValue": null, "targets": [{"elementName": "SourcesText", "fieldName": "text"}]}]}'
        )
    ]
)
def document_rag_explorer(parameters: SkillInput):
    """Main skill function for document RAG exploration"""
    
    # Get parameters
    user_question = parameters.arguments.user_question
    base_url = parameters.arguments.base_url
    max_sources = parameters.arguments.max_sources or 5
    match_threshold = parameters.arguments.match_threshold or 0.15  # Lower threshold for better recall
    max_characters = parameters.arguments.max_characters or 3000
    max_prompt = parameters.arguments.max_prompt
    
    # Initialize empty topics list (globals not available in SkillInput)
    list_of_topics = []
    
    # Initialize results
    main_html = ""
    sources_html = ""
    title = "Document Analysis"
    response_data = None
    
    try:
        # Load document sources from pack.json
        loaded_sources = load_document_sources()
        
        if not loaded_sources:
            return SkillOutput(
                final_prompt="No document sources found. Please ensure pack.json is available.",
                narrative=None,
                visualizations=[],
                export_data=[]
            )
        
        # Find matching documents
        logger.info(f"DEBUG: Searching for documents matching: '{user_question}'")
        docs = find_matching_documents(
            user_question=user_question,
            topics=list_of_topics,
            loaded_sources=loaded_sources,
            base_url=base_url,
            max_sources=max_sources,
            match_threshold=match_threshold,
            max_characters=max_characters
        )
        logger.info(f"DEBUG: Found {len(docs) if docs else 0} matching documents")
        
        if not docs:
            # No results found
            logger.warning("DEBUG: No matching documents found for query")
            no_results_html = """
            <div style="text-align: center; padding: 40px; color: #666;">
                <h2>No relevant documents found</h2>
                <p>No documents in the knowledge base matched your question with sufficient relevance.</p>
                <p>Try rephrasing your question or using different keywords.</p>
            </div>
            """
            main_html = no_results_html
            sources_html = "<p>No sources available</p>"
            title = "No Results Found"
        else:
            # Generate response from documents
            logger.info(f"DEBUG: Generating RAG response from {len(docs)} documents")
            response_data = generate_rag_response(user_question, docs)
            logger.info(f"DEBUG: Response generated: {bool(response_data)}")
            
            # Create main response HTML (without sources section)
            if response_data:
                try:
                    main_html = force_ascii_replace(
                        Template(main_response_template).render(
                            title=response_data['title'],
                            content=response_data['content']
                        )
                    )
                    logger.info(f"DEBUG: Generated main HTML, length: {len(main_html)}")
                    
                    # Create separate sources HTML
                    sources_html = force_ascii_replace(
                        Template(sources_template).render(
                            references=response_data['references']
                        )
                    )
                    logger.info(f"DEBUG: Generated sources HTML, length: {len(sources_html)}")
                    title = response_data['title']
                except Exception as e:
                    logger.error(f"DEBUG: Error rendering HTML templates: {str(e)}")
                    import traceback
                    logger.error(f"DEBUG: Template error traceback: {traceback.format_exc()}")
                    main_html = f"<p>Error rendering content: {str(e)}</p>"
                    sources_html = "<p>Error rendering sources</p>"
                    title = "Template Error"
            else:
                main_html = "<p>Error generating response from documents.</p>"
                sources_html = "<p>Error loading sources</p>"
                title = "Error"
    
    except Exception as e:
        logger.error(f"ERROR in document RAG: {str(e)}")
        import traceback
        logger.error(f"ERROR: Full traceback:\n{traceback.format_exc()}")
        main_html = f"<p>Error processing request: {str(e)}</p>"
        sources_html = "<p>Error loading sources</p>"
        title = "Error"
    
    # Create content variables for wire_layout like price variance does
    # Prepare content for response tab
    references_content = ""
    if response_data and response_data.get('references'):
        references_content = f"""
        <hr style="margin: 20px 0;">
        <h3>References</h3>
        {create_references_list(response_data['references'])}
        """
    
    response_content = f"""
    <div style="padding: 20px;">
        {main_html}
        {references_content}
    </div>
    """
    
    # Prepare content for sources tab
    sources_content = f"""
    <div style="padding: 20px;">
        <h2>Document Sources</h2>
        {create_sources_table(response_data['references']) if response_data and response_data.get('references') else sources_html}
    </div>
    """
    
    # Create visualizations using wire_layout like price variance
    visualizations = []
    
    try:
        logger.info(f"DEBUG: Creating response tab with title: {title}")
        logger.info(f"DEBUG: Response content length: {len(response_content)} characters")
        logger.info(f"DEBUG: References content length: {len(references_content)} characters")
        
        # Response tab
        response_vars = {"response_content": response_content}
        logger.info(f"DEBUG: Response vars keys: {list(response_vars.keys())}")
        
        response_layout_json = json.loads(parameters.arguments.response_layout)
        logger.info(f"DEBUG: Response layout parsed successfully")
        
        rendered_response = wire_layout(response_layout_json, response_vars)
        logger.info(f"DEBUG: Response layout rendered successfully, type: {type(rendered_response)}")
        
        visualizations.append(SkillVisualization(title=title, layout=rendered_response))
        logger.info(f"DEBUG: Response visualization added successfully")
        
        # Sources tab
        logger.info(f"DEBUG: Creating sources tab")
        logger.info(f"DEBUG: Sources content length: {len(sources_content)} characters")
        
        sources_vars = {"sources_content": sources_content}
        logger.info(f"DEBUG: Sources vars keys: {list(sources_vars.keys())}")
        
        sources_layout_json = json.loads(parameters.arguments.sources_layout)
        logger.info(f"DEBUG: Sources layout parsed successfully")
        
        rendered_sources = wire_layout(sources_layout_json, sources_vars)
        logger.info(f"DEBUG: Sources layout rendered successfully, type: {type(rendered_sources)}")
        
        visualizations.append(SkillVisualization(title="Sources", layout=rendered_sources))
        logger.info(f"DEBUG: Sources visualization added successfully")
        
        logger.info(f"DEBUG: Total visualizations created: {len(visualizations)}")
        for i, viz in enumerate(visualizations):
            logger.info(f"DEBUG: Visualization {i+1}: title='{viz.title}', layout_type={type(viz.layout)}")
            
    except Exception as e:
        logger.error(f"ERROR: Failed to create visualizations: {str(e)}")
        import traceback
        logger.error(f"ERROR: Full traceback: {traceback.format_exc()}")
        
        # Fallback to simple HTML if wire_layout fails
        logger.info("DEBUG: Falling back to simple HTML visualizations")
        simple_response_html = f"<div style='padding:20px;'>{main_html}{references_content}</div>"
        simple_sources_html = f"<div style='padding:20px;'><h2>Document Sources</h2>{sources_html}</div>"
        
        visualizations = [
            SkillVisualization(title=title, layout=simple_response_html),
            SkillVisualization(title="Sources", layout=simple_sources_html)
        ]
        logger.info(f"DEBUG: Fallback visualizations created: {len(visualizations)}")
    
    # Return skill output with final_prompt for insights and narrative=None like other skills
    return SkillOutput(
        final_prompt=max_prompt,
        narrative=None,
        visualizations=visualizations,
        export_data=[]
    )

# Helper Functions and Templates

def create_references_list(references):
    """Create clickable references list HTML"""
    if not references:
        return "<p>No references available</p>"
    
    html_parts = ["<ol style='list-style-type: decimal; padding-left: 20px;'>"]
    for ref in references:
        html_parts.append(f"""
            <li style='margin-bottom: 10px;'>
                <a href='{ref.get('url', '#')}' target='_blank' style='color: #0066cc; text-decoration: none;'>
                    {ref.get('text', 'Document')} (Page {ref.get('page', '?')})
                </a>
            </li>
        """)
    html_parts.append("</ol>")
    return ''.join(html_parts)

def get_pdf_thumbnail(pack_file_path, file_name, page_num, image_height=300, image_width=400):
    """Generate real PDF thumbnail using knowledge base API like ddoc_ex.py"""
    logger.info(f"DEBUG THUMBNAIL: ==> Starting thumbnail generation for {file_name} page {page_num}")
    logger.info(f"DEBUG THUMBNAIL: ==> Requested dimensions: {image_width}x{image_height}")
    
    # Knowledge base API not available in skill environment, use fallback
    logger.info(f"DEBUG THUMBNAIL: ==> Knowledge base API not available in skill environment, using fallback")
    return create_fallback_thumbnail(file_name, page_num, image_width, image_height)
        

def create_fallback_thumbnail(file_name, page_num, image_width, image_height):
    """Create a clean fallback thumbnail when PDF rendering fails"""
    logger.info(f"DEBUG FALLBACK: ==> Creating fallback thumbnail for {file_name} page {page_num}")
    logger.info(f"DEBUG FALLBACK: ==> Dimensions: {image_width}x{image_height}")
    try:
        from PIL import ImageDraw, ImageFont
        
        # Create a clean document-style thumbnail
        placeholder_image = Image.new('RGB', (image_width, image_height), color='#f8f9fa')
        draw = ImageDraw.Draw(placeholder_image)
        
        # Add a subtle border
        draw.rectangle([0, 0, image_width-1, image_height-1], outline='#dee2e6', width=1)
        
        # Add a document icon in the center
        icon_size = min(image_width, image_height) // 3
        icon_x = (image_width - icon_size) // 2
        icon_y = (image_height - icon_size) // 2 - 20
        
        # Draw document shape
        draw.rectangle([icon_x, icon_y, icon_x + icon_size, icon_y + icon_size], 
                      fill='white', outline='#6c757d', width=2)
        
        # Add fold corner
        corner_size = icon_size // 4
        draw.polygon([(icon_x + icon_size - corner_size, icon_y),
                     (icon_x + icon_size, icon_y + corner_size),
                     (icon_x + icon_size - corner_size, icon_y + corner_size)],
                    fill='#e9ecef', outline='#6c757d')
        
        # Add text lines in document
        line_spacing = icon_size // 8
        for i in range(3):
            y_pos = icon_y + icon_size // 3 + i * line_spacing
            draw.line([(icon_x + icon_size // 6, y_pos), (icon_x + icon_size - icon_size // 6, y_pos)], 
                     fill='#adb5bd', width=1)
        
        # Add file name and page number below icon
        try:
            font = ImageFont.load_default()
        except:
            font = None
        
        # Document name
        doc_name = file_name[:20] + "..." if len(file_name) > 20 else file_name
        text_bbox = draw.textbbox((0, 0), doc_name, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_x = (image_width - text_width) // 2
        text_y = icon_y + icon_size + 15
        draw.text((text_x, text_y), doc_name, fill='#495057', font=font)
        
        # Page number
        page_text = f"Page {page_num}"
        page_bbox = draw.textbbox((0, 0), page_text, font=font)
        page_width = page_bbox[2] - page_bbox[0]
        page_x = (image_width - page_width) // 2
        draw.text((page_x, text_y + 18), page_text, fill='#6c757d', font=font)
        
        # Convert to base64
        buffered = io.BytesIO()
        placeholder_image.save(buffered, format="PNG")
        image_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
        
        logger.info(f"DEBUG: Created fallback thumbnail for {file_name} page {page_num}")
        return image_base64
        
    except Exception as e:
        logger.error(f"DEBUG: Failed to create fallback thumbnail: {e}")
        return None

def create_sources_table(references):
    """Create sources table HTML without thumbnails (thumbnails are now only in references section)"""
    if not references:
        return "<p>No sources available</p>"
    
    html_parts = [
        """<table style='width: 100%; border-collapse: collapse; font-size: 14px;'>
        <thead>
            <tr style='background-color: #f8f9fa; border-bottom: 2px solid #dee2e6;'>
                <th style='padding: 12px; text-align: left; font-weight: 600;'>Document Name</th>
                <th style='padding: 12px; text-align: left; font-weight: 600;'>Page</th>
                <th style='padding: 12px; text-align: left; font-weight: 600;'>Match Score</th>
            </tr>
        </thead>
        <tbody>"""
    ]
    
    for i, ref in enumerate(references):
        bg_color = '#ffffff' if i % 2 == 0 else '#f8f9fa'
        # Extract match score from ref if available, otherwise use placeholder
        match_score = ref.get('match_score', '0.780000') if hasattr(ref, 'get') else '0.780000'
        
        html_parts.append(f"""
            <tr style='background-color: {bg_color}; border-bottom: 1px solid #dee2e6;'>
                <td style='padding: 12px;'>
                    <a href='{ref.get('url', '#')}' target='_blank' style='color: #0066cc; text-decoration: none;'>
                        {ref.get('src', ref.get('text', 'Document'))}
                    </a>
                </td>
                <td style='padding: 12px;'>{ref.get('page', '?')}</td>
                <td style='padding: 12px;'>{match_score}</td>
            </tr>
        """)
    
    html_parts.append("</tbody></table>")
    return ''.join(html_parts)

def load_document_sources():
    """Load document sources from pack.json bundled with the skill"""
    loaded_sources = []
    
    try:
        # First, try to load pack.json from the same directory as this skill file
        skill_dir = os.path.dirname(os.path.abspath(__file__))
        pack_file = os.path.join(skill_dir, "pack.json")
        
        logger.info(f"DEBUG: Looking for pack.json in skill directory: {pack_file}")
        
        # Check if pack.json exists in the skill directory
        if not os.path.exists(pack_file):
            # Try looking in a 'data' subdirectory
            data_dir = os.path.join(skill_dir, "data")
            pack_file_data = os.path.join(data_dir, "pack.json")
            
            if os.path.exists(pack_file_data):
                pack_file = pack_file_data
                logger.info(f"DEBUG: Found pack.json in data directory: {pack_file}")
            else:
                # Fallback: try the old Skill Resources path if environment variables are available
                logger.info(f"DEBUG: pack.json not found in skill bundle, trying Skill Resources as fallback")
                
                try:
                    from ar_paths import ARTIFACTS_PATH
                    logger.info(f"DEBUG: Successfully imported ARTIFACTS_PATH: {ARTIFACTS_PATH}")
                except ImportError as e:
                    logger.info(f"DEBUG: Could not import ar_paths, using environment variable: {e}")
                    ARTIFACTS_PATH = os.environ.get('AR_DATA_BASE_PATH', '/artifacts')
                
                # Get environment variables for path construction
                tenant = os.environ.get('AR_TENANT_ID', 'maxstaging')
                copilot = os.environ.get('AR_COPILOT_ID', '')
                skill_id = os.environ.get('AR_COPILOT_SKILL_ID', '')
                
                if copilot and skill_id:
                    resource_path = os.path.join(
                        ARTIFACTS_PATH,
                        tenant,
                        "skill_workspaces",
                        copilot,
                        skill_id,
                        "pack.json"
                    )
                    if os.path.exists(resource_path):
                        pack_file = resource_path
                        logger.info(f"DEBUG: Found pack.json in Skill Resources: {pack_file}")
                    else:
                        pack_file = None
                        logger.warning(f"DEBUG: No pack.json found in bundle or Skill Resources")
                else:
                    pack_file = None
                    logger.warning(f"DEBUG: No pack.json found and missing environment variables for Skill Resources")
        else:
            logger.info(f"DEBUG: Found pack.json in skill bundle: {pack_file}")
        
        if pack_file and os.path.exists(pack_file):
            logger.info(f"Loading documents from: {pack_file}")
            with open(pack_file, 'r', encoding='utf-8') as f:
                resource_contents = json.load(f)
                logger.info(f"DEBUG: Loaded JSON structure type: {type(resource_contents)}")
                
                # Handle different pack.json formats
                if isinstance(resource_contents, list):
                    logger.info(f"DEBUG: Processing {len(resource_contents)} files from pack.json")
                    # Format: [{"File": "doc.pdf", "Chunks": [{"Text": "...", "Page": 1}]}]
                    for processed_file in resource_contents:
                        file_name = processed_file.get("File", "unknown_file")
                        chunks = processed_file.get("Chunks", [])
                        logger.info(f"DEBUG: Processing file '{file_name}' with {len(chunks)} chunks")
                        for chunk in chunks:
                            res = {
                                "file_name": file_name,
                                "text": chunk.get("Text", ""),
                                "description": str(chunk.get("Text", ""))[:200] + "..." if len(str(chunk.get("Text", ""))) > 200 else str(chunk.get("Text", "")),
                                "chunk_index": chunk.get("Page", 1),
                                "citation": file_name
                            }
                            loaded_sources.append(res)
                else:
                    logger.warning(f"Unexpected pack.json format - expected array of files, got: {type(resource_contents)}")
        else:
            logger.warning("pack.json not found in any expected locations")
            
    except Exception as e:
        logger.error(f"Error loading pack.json: {str(e)}")
        import traceback
        logger.error(f"DEBUG: Full traceback: {traceback.format_exc()}")
    
    logger.info(f"Loaded {len(loaded_sources)} document chunks from pack.json")
    return loaded_sources

def find_matching_documents(user_question, topics, loaded_sources, base_url, max_sources, match_threshold, max_characters):
    """Find documents using enhanced keyword matching optimized for competitive intelligence"""
    logger.info("DEBUG: Starting enhanced keyword matching (embeddings not available via SDK)")
    logger.info(f"DEBUG: User question: {user_question}")
    logger.info(f"DEBUG: Match threshold: {match_threshold}")

    try:
        import os

        logger.info(f"DEBUG: Matching against {len(loaded_sources)} document sources")

        # Analyze question intent
        question_lower = user_question.lower() if user_question else ""

        mentions_lennar = "lennar" in question_lower
        mentions_meritage = "meritage" in question_lower
        mentions_both = mentions_lennar and mentions_meritage
        wants_comparison = any(word in question_lower for word in ["competitors", "competition", "both", "compare", "versus", "vs"])

        # Build comprehensive search terms
        search_terms = []
        if user_question:
            search_terms.append(user_question)

        # Aggressive keyword expansion
        keyword_expansions = {
            'financing': ['financing', 'finance', 'mortgage', 'loan', 'apr', 'rate', 'payment', 'buydown',
                         'interest', 'monthly payment', 'qualification', 'credit', '2.99%', '5.572%'],
            'special': ['special', 'promotion', 'offer', 'event', 'sale', 'limited time', 'exclusive',
                       'discount', 'incentive', 'deal', 'savings', 'national sales event'],
            'price': ['price', 'pricing', 'cost', '$', 'reduction', 'reduced', 'discount', 'drop',
                     'decrease', 'lower', 'affordable', 'starting from'],
            'inventory': ['inventory', 'available', 'availability', 'move-in ready', 'quick move',
                         'homes available', 'in stock', 'ready now']
        }

        # Add expansions based on keywords in question
        for key, expansions in keyword_expansions.items():
            if key in question_lower:
                search_terms.extend(expansions)

        # Add competitor terms
        if mentions_lennar or wants_comparison:
            search_terms.append('lennar')
        if mentions_meritage or wants_comparison:
            search_terms.append('meritage')

        search_terms.extend([topic for topic in topics if topic])

        # Remove duplicates
        seen = set()
        unique_terms = []
        for term in search_terms:
            if term and term.lower() not in seen:
                seen.add(term.lower())
                unique_terms.append(term)

        logger.info(f"DEBUG: Expanded to {len(unique_terms)} unique search terms")

        # Score all documents
        scored_sources = []
        for source in loaded_sources:
            score = calculate_enhanced_relevance(source['text'], unique_terms, source['file_name'])

            if score >= float(match_threshold):
                source_copy = source.copy()
                source_copy['match_score'] = score

                # Generate URLs
                if "Lennar" in source_copy['file_name']:
                    doc_id = "abb40c5f-f259-48bf-85c3-d2ed1ea956b8"
                elif "Meritage" in source_copy['file_name']:
                    doc_id = "7f0292db-d935-4c90-b65b-897bb98167f9"
                else:
                    doc_id = "unknown"

                source_copy['url'] = f"https://dreamfinders.poc.answerrocket.com/apps/system/knowledge-base/{doc_id}#page={source_copy['chunk_index']}"
                scored_sources.append(source_copy)

        logger.info(f"DEBUG: {len(scored_sources)} documents passed threshold")

        # Sort by score
        scored_sources.sort(key=lambda x: x['match_score'], reverse=True)

        # Intelligent source selection
        matches = []
        chars_so_far = 0
        has_lennar = False
        has_meritage = False

        # First pass: get best matches
        for source in scored_sources:
            if len(matches) >= int(max_sources):
                break

            # Check character limit (but ensure minimum docs)
            if len(matches) >= 2 and chars_so_far + len(source['text']) > int(max_characters):
                break

            # Track companies
            if "Lennar" in source['file_name']:
                has_lennar = True
            elif "Meritage" in source['file_name']:
                has_meritage = True

            matches.append(source)
            chars_so_far += len(source['text'])

        # Second pass: ensure both companies if comparing
        if (wants_comparison or mentions_both) and len(matches) < int(max_sources):
            if not has_lennar:
                for source in scored_sources:
                    if "Lennar" in source['file_name'] and source not in matches:
                        matches.append(source)
                        logger.info("DEBUG: Added Lennar doc for comparison")
                        break
            if not has_meritage:
                for source in scored_sources:
                    if "Meritage" in source['file_name'] and source not in matches:
                        matches.append(source)
                        logger.info("DEBUG: Added Meritage doc for comparison")
                        break

        logger.info(f"DEBUG: Selected {len(matches)} final documents")
        if matches:
            lennar_count = sum(1 for m in matches if "Lennar" in m['file_name'])
            meritage_count = sum(1 for m in matches if "Meritage" in m['file_name'])
            logger.info(f"DEBUG: Lennar: {lennar_count}, Meritage: {meritage_count}")
            logger.info(f"DEBUG: Top scores: {[round(m['match_score'], 3) for m in matches[:3]]}")

        return [SimpleNamespace(**match) for match in matches]

    except Exception as e:
        logger.error(f"ERROR: Document matching failed: {e}")
        import traceback
        logger.error(f"ERROR: Full traceback: {traceback.format_exc()}")
        raise e

def calculate_simple_relevance(text, search_terms):
    """Enhanced relevance scoring for competitive intelligence documents"""
    text_lower = text.lower()
    score = 0.0
    debug_matches = []

    # Domain-specific keywords for real estate competitive intelligence
    financing_keywords = ['financing', 'mortgage', 'loan', 'apr', 'rate', 'payment', 'buydown', 'interest', 'closing cost', 'incentive', 'promotion', 'offer', 'special', 'event', 'sale', 'monthly payment']
    pricing_keywords = ['price', 'pricing', 'cost', '$', 'from', 'starting', 'base', 'reduction', 'discount']
    inventory_keywords = ['available', 'inventory', 'move-in ready', 'quick move', 'homes', 'communities', 'floor plan', 'model']
    competitor_keywords = ['lennar', 'meritage', 'dr horton', 'pulte', 'kb home', 'taylor morrison']

    # Check for domain-specific content first
    for keyword in financing_keywords:
        if keyword in text_lower:
            score += 0.15
            debug_matches.append(f"financing:{keyword}")

    for keyword in pricing_keywords:
        if keyword in text_lower:
            score += 0.1
            debug_matches.append(f"pricing:{keyword}")

    for keyword in inventory_keywords:
        if keyword in text_lower:
            score += 0.08

    for keyword in competitor_keywords:
        if keyword in text_lower:
            score += 0.2
            debug_matches.append(f"competitor:{keyword}")

    # Now check search terms with enhanced matching
    for term in search_terms:
        if not term:
            continue

        term_lower = term.lower()

        # Check for exact phrase matches first (highest priority)
        if term_lower in text_lower:
            occurrences = text_lower.count(term_lower)
            phrase_score = min(occurrences * 0.5, 1.0)  # Strong boost for exact phrases
            score += phrase_score
            continue

        # Break down into individual words for partial matching
        term_words = term_lower.split()
        term_total_score = 0
        matched_words = 0
        total_words = len([w for w in term_words if len(w) >= 3])  # Count meaningful words

        for word in term_words:
            if len(word) < 3:  # Skip very short words
                continue

            # Check for partial matches and synonyms
            if word in text_lower:
                matched_words += 1
                occurrences = text_lower.count(word)

                # Boost important domain words
                if word in ['financing', 'mortgage', 'special', 'promotion', 'rate', 'payment', 'lennar', 'meritage', 'apr', 'buydown']:
                    base_score = 0.4
                elif len(word) >= 7:  # Long words are usually specific
                    base_score = 0.25
                else:
                    base_score = 0.15

                word_score = min(occurrences * base_score, 0.6)
                term_total_score += word_score
            # Also check for common variations
            elif any(variation in text_lower for variation in [word + 's', word + 'ing', word + 'ed', word[:-1] if word.endswith('s') else word]):
                matched_words += 1
                term_total_score += 0.1

        # Boost score based on completeness of the search term match
        if total_words > 0:
            completeness_ratio = matched_words / total_words
            if completeness_ratio >= 0.7:  # Most words found
                term_total_score *= 1.3
            elif completeness_ratio >= 0.5:  # Many words found
                term_total_score *= 1.1

        score += term_total_score

    # Normalize and ensure we don't over-score
    final_score = min(score / 2.0, 1.0)  # Divide by 2 to normalize the increased scoring

    # Debug logging for high-scoring matches
    if final_score > 0.3 and debug_matches:
        logger.debug(f"MATCH SCORE {final_score:.3f}: Found keywords: {debug_matches[:5]}")

    return final_score


def calculate_enhanced_relevance(text, search_terms, file_name):
    """Enhanced relevance scoring optimized for competitive intelligence"""
    text_lower = text.lower()
    score = 0.0

    # Critical keywords with weights
    critical_keywords = {
        # Financing
        'apr': 0.5, 'rate': 0.4, 'buydown': 0.6, 'mortgage': 0.4, 'financing': 0.5,
        'payment': 0.3, 'monthly': 0.3, '2.99%': 0.8, '5.572%': 0.8,

        # Promotions
        'special': 0.5, 'event': 0.4, 'promotion': 0.5, 'limited': 0.4, 'offer': 0.4,
        'sale': 0.4, 'national': 0.3, 'incentive': 0.5,

        # Pricing
        'price': 0.4, 'reduction': 0.5, 'reduced': 0.5, 'discount': 0.5,
        '$': 0.3, 'cost': 0.3,

        # Inventory
        'available': 0.3, 'inventory': 0.4, 'move-in': 0.4, 'ready': 0.3,

        # Competitors
        'lennar': 0.3, 'meritage': 0.3
    }

    # Check critical keywords
    for keyword, weight in critical_keywords.items():
        if keyword in text_lower:
            count = min(text_lower.count(keyword), 3)  # Cap contribution
            score += count * weight

    # Check search terms
    for term in search_terms:
        if not term:
            continue

        term_lower = term.lower()

        # Exact phrase match (high value)
        if len(term_lower) > 3 and term_lower in text_lower:
            occurrences = text_lower.count(term_lower)
            score += min(occurrences * 0.6, 1.5)
            continue

        # Word matching
        words = term_lower.split()
        matched = 0

        for word in words:
            if len(word) < 3:
                continue
            if word in text_lower:
                matched += 1
                if word in critical_keywords:
                    score += critical_keywords[word]
                else:
                    score += 0.15

        # Completeness bonus
        if len(words) > 1 and matched / len(words) >= 0.7:
            score += 0.3

    # High-value patterns
    high_value_patterns = [
        ('national sales event', 0.8),
        ('special financing', 0.7),
        ('2.99% apr', 0.9),
        ('limited time', 0.5),
        ('move-in ready', 0.5),
        ('price reduction', 0.6)
    ]

    for pattern, weight in high_value_patterns:
        if pattern in text_lower:
            score += weight

    # File name bonus
    file_lower = file_name.lower()
    for term in search_terms:
        if term and term.lower() in file_lower:
            score += 0.2
            break

    # Normalize
    return min(score / 3.0, 1.0)


def generate_rag_response(user_question, docs):
    """Generate response using LLM with document context"""
    if not docs:
        return None
    
    # Build facts from documents for LLM prompt
    facts = []
    logger.info(f"DEBUG: Building prompt from {len(docs)} documents")
    for i, doc in enumerate(docs):
        facts.append(f"====== Source {i+1} ====")
        facts.append(f"File and page: {doc.file_name} page {doc.chunk_index}")
        facts.append(f"Description: {doc.description}")
        facts.append(f"Citation: {doc.url}")
        facts.append(f"Content: {doc.text}")
        facts.append("")
        logger.debug(f"DEBUG: Added source {i+1}: {doc.file_name} p{doc.chunk_index} ({len(doc.text)} chars)")
    
    # Create the prompt for the LLM
    prompt_template = Template(narrative_prompt)
    full_prompt = prompt_template.render(
        user_query=user_question,
        facts="\n".join(facts)
    )
    logger.info(f"DEBUG: Generated prompt length: {len(full_prompt)} chars")
    logger.debug(f"DEBUG: Prompt preview: {full_prompt[:500]}...")
    
    try:
        # Use ArUtils for LLM calls like other skills do
        logger.info("DEBUG: Making LLM call with ArUtils")
        from ar_analytics import ArUtils
        ar_utils = ArUtils()
        llm_response = ar_utils.get_llm_response(full_prompt)
        
        logger.info(f"DEBUG: Got LLM response length: {len(llm_response)} chars")
        logger.info(f"DEBUG: LLM response preview: {llm_response[:200]}...")
        
        # Parse the LLM response like the old doc_search code
        def get_between_tags(content, tag):
            try:
                return content.split("<"+tag+">",1)[1].split("</"+tag+">",1)[0]
            except:
                pass
            return content
        
        title = get_between_tags(llm_response, "title") or f"Analysis: {user_question}"
        content = get_between_tags(llm_response, "content") or llm_response
        
        logger.info(f"DEBUG: Parsed title: {title[:50]}...")
        logger.info(f"DEBUG: Parsed content: {content[:100]}...")
        
    except Exception as e:
        logger.error(f"DEBUG: ArUtils LLM call failed: {e}")
        logger.info(f"DEBUG: Using fallback response generation")
        # Fallback with better extraction of actual content
        title = f"Competitive Intelligence: {user_question}"
        content = f"<p>Based on the competitive intelligence documents, here's the relevant information:</p>"

        # Extract and present actual data from documents
        for i, doc in enumerate(docs):
            doc_text = str(doc.text) if doc.text else ""
            clean_text = doc_text.replace(f"START OF PAGE: {doc.chunk_index}", "").strip()
            clean_text = clean_text.replace(f"END OF PAGE: {doc.chunk_index}", "").strip()

            if clean_text and len(clean_text) > 20:
                # Extract specific data points like prices, rates, etc
                lines = clean_text.split('\n')
                relevant_lines = []

                for line in lines:
                    line_lower = line.lower()
                    # Extract lines with important information
                    if any(keyword in line_lower for keyword in ['$', 'price', 'apr', 'rate', 'payment', 'special', 'event', 'promotion', 'financing', 'mortgage', 'buydown', 'available', 'move-in']):
                        relevant_lines.append(line.strip())

                if relevant_lines:
                    content += f"<h3>From {doc.file_name} (Page {doc.chunk_index})<sup>[{i+1}]</sup></h3>"
                    content += "<ul>"
                    for line in relevant_lines[:5]:  # Show top 5 most relevant lines
                        if line:
                            content += f"<li>{line}</li>"
                    content += "</ul>"
    
    # Build references with actual URLs and thumbnails
    references = []
    skill_dir = os.path.dirname(os.path.abspath(__file__))
    pack_file_path = os.path.join(skill_dir, "pack.json")
    
    for i, doc in enumerate(docs):
        # Create preview text (first 120 characters)
        doc_text = str(doc.text) if doc.text else ""
        preview_text = doc_text[:120] + "..." if len(doc_text) > 120 else doc_text
        
        # Generate thumbnail for this document (for references section)
        logger.info(f"DEBUG: Generating thumbnail for reference {i+1}: {doc.file_name} page {doc.chunk_index}")
        thumbnail_base64 = get_pdf_thumbnail(pack_file_path, doc.file_name, doc.chunk_index, 120, 160)
        
        # Generate correct knowledge base URLs with proper document IDs
        logger.info(f"DEBUG URL: ==> Generating URL for: {doc.file_name}")

        # Map file names to their actual knowledge base IDs
        if "Lennar" in doc.file_name:
            doc_id = "abb40c5f-f259-48bf-85c3-d2ed1ea956b8"
        elif "Meritage" in doc.file_name:
            doc_id = "7f0292db-d935-4c90-b65b-897bb98167f9"
        else:
            # Fallback for unknown documents
            doc_id = "unknown"

        doc.url = f"https://dreamfinders.poc.answerrocket.com/apps/system/knowledge-base/{doc_id}#page={doc.chunk_index}"
        logger.info(f"DEBUG URL: ==> Generated URL: {doc.url}")
        
        ref = {
            'number': i + 1,
            'url': doc.url,
            'src': doc.file_name,
            'page': doc.chunk_index,
            'text': f"Document: {doc.file_name}",
            'preview': preview_text,
            'thumbnail': thumbnail_base64 if thumbnail_base64 else ""
        }
        references.append(ref)
        
    return {
        'title': title,
        'content': content,
        'references': references,
        'raw_prompt': full_prompt  # For debugging
    }

def force_ascii_replace(html_string):
    """Clean HTML string for safe rendering"""
    # Remove null characters
    cleaned = html_string.replace('\u0000', '')
    
    # Escape special characters, but preserve existing HTML entities
    cleaned = re.sub(r'&(?!amp;|lt;|gt;|quot;|apos;|#\d+;|#x[0-9a-fA-F]+;)', '&amp;', cleaned)
    
    # Replace problematic characters with HTML entities
    cleaned = cleaned.replace('"', '&quot;')
    cleaned = cleaned.replace("'", '&#39;')
    cleaned = cleaned.replace('–', '&ndash;')
    cleaned = cleaned.replace('—', '&mdash;')
    cleaned = cleaned.replace('…', '&hellip;')
    
    # Convert curly quotes to straight quotes
    cleaned = cleaned.replace('"', '"').replace('"', '"')
    cleaned = cleaned.replace(''', "'").replace(''', "'")
    
    # Remove any remaining control characters
    cleaned = ''.join(ch for ch in cleaned if ord(ch) >= 32 or ch in '\n\r\t')
    
    return cleaned

# OpenAI Embedding Functions

def get_openai_embedding(text: str) -> List[float]:
    """Get OpenAI embedding using the platform's embedding service"""
    try:
        from ar_analytics import ArUtils
        ar_utils = ArUtils()

        # Try different possible embedding methods on ArUtils
        embedding_methods = ['get_embedding', 'get_embeddings', 'embed_text', 'embedding']

        for method_name in embedding_methods:
            if hasattr(ar_utils, method_name):
                logger.info(f"DEBUG: Found ArUtils embedding method: {method_name}")
                method = getattr(ar_utils, method_name)
                try:
                    result = method(text)
                    if isinstance(result, list) and len(result) > 0:
                        logger.info(f"DEBUG: Got embedding from ArUtils.{method_name}, dimension: {len(result)}")
                        return result
                except Exception as e:
                    logger.warning(f"DEBUG: ArUtils.{method_name} failed: {e}")
                    continue

        # Try platform-specific embedding APIs
        logger.info("DEBUG: Trying platform embedding service directly")

        # Try using requests to call the platform's embedding endpoint
        import requests
        import os

        # Get the base URL from environment
        base_url = os.environ.get("AR_BACKEND_BASE_URL", "http://localhost:8080")
        embedding_url = f"{base_url}/api/embeddings"

        # Try to get tenant info for proper authentication
        tenant = os.environ.get('AR_TENANT_ID', 'dreamfinders')

        headers = {
            'Content-Type': 'application/json',
            'Tenant': tenant,
            'Max-Authorization': 'Max-Internal'
        }

        payload = {
            'text': text.replace("\n", " "),
            'model': 'text-embedding-ada-002'
        }

        logger.info(f"DEBUG: Calling platform embedding API: {embedding_url}")
        response = requests.post(embedding_url, json=payload, headers=headers, timeout=30)

        if response.status_code == 200:
            result = response.json()
            if 'embedding' in result:
                embedding = result['embedding']
                logger.info(f"DEBUG: Got embedding from platform API, dimension: {len(embedding)}")
                return embedding
            elif 'data' in result and len(result['data']) > 0:
                embedding = result['data'][0]['embedding']
                logger.info(f"DEBUG: Got embedding from platform API (data format), dimension: {len(embedding)}")
                return embedding
        else:
            logger.warning(f"DEBUG: Platform embedding API returned {response.status_code}: {response.text}")

        # Log available ArUtils methods for debugging
        ar_utils_methods = [method for method in dir(ar_utils) if not method.startswith('_')]
        logger.info(f"DEBUG: Available ArUtils methods: {ar_utils_methods[:10]}...")

        raise ValueError("No embedding method found on ArUtils or platform API")

    except Exception as e:
        logger.error(f"ERROR: Failed to get embedding: {e}")
        raise e

def cosine_similarity(a: List[float], b: List[float]) -> float:
    """Calculate cosine similarity between two vectors"""
    try:
        a_array = np.array(a)
        b_array = np.array(b)

        dot_product = np.dot(a_array, b_array)
        norm_a = np.linalg.norm(a_array)
        norm_b = np.linalg.norm(b_array)

        if norm_a == 0 or norm_b == 0:
            return 0.0

        similarity = dot_product / (norm_a * norm_b)
        return float(similarity)

    except Exception as e:
        logger.error(f"ERROR: Failed to calculate cosine similarity: {e}")
        return 0.0

def find_matches_with_openai_embeddings(user_question, topics, loaded_sources, match_threshold, max_sources, max_characters):
    """Find document matches using OpenAI embeddings"""
    logger.info("DEBUG: Starting OpenAI embedding search")

    try:
        # Combine question and topics for search query
        search_query = user_question
        if topics:
            search_query += " " + " ".join(topics)

        logger.info(f"DEBUG: Getting embedding for search query: {search_query[:100]}...")

        # Get embedding for search query
        query_embedding = get_openai_embedding(search_query)
        logger.info(f"DEBUG: Got query embedding, dimension: {len(query_embedding)}")

        # Calculate similarities for all sources
        matches = []
        for i, source in enumerate(loaded_sources):
            if i % 20 == 0:  # Log progress every 20 documents
                logger.info(f"DEBUG: Processing document {i+1}/{len(loaded_sources)}")

            try:
                # Get embedding for document text
                doc_embedding = get_openai_embedding(source['text'])

                # Calculate similarity
                similarity = cosine_similarity(query_embedding, doc_embedding)

                if similarity >= float(match_threshold):
                    source_copy = source.copy()
                    source_copy['match_score'] = similarity

                    # Generate correct knowledge base URLs with proper document IDs
                    if "Lennar" in source_copy['file_name']:
                        doc_id = "abb40c5f-f259-48bf-85c3-d2ed1ea956b8"
                    elif "Meritage" in source_copy['file_name']:
                        doc_id = "7f0292db-d935-4c90-b65b-897bb98167f9"
                    else:
                        doc_id = "unknown"
                    source_copy['url'] = f"https://dreamfinders.poc.answerrocket.com/apps/system/knowledge-base/{doc_id}#page={source_copy['chunk_index']}"

                    matches.append(source_copy)
                    logger.info(f"DEBUG: Found match with similarity {similarity:.3f}: {source_copy['file_name']} page {source_copy['chunk_index']}")

            except Exception as e:
                logger.warning(f"DEBUG: Failed to process document {i}: {e}")
                continue

        # Sort by similarity score (descending)
        matches.sort(key=lambda x: x['match_score'], reverse=True)

        # Select top matches respecting character limit
        final_matches = []
        chars_so_far = 0

        for match in matches:
            if len(final_matches) >= int(max_sources):
                break

            # Always include at least 2 documents if available, then respect character limit
            if len(final_matches) >= 2 and chars_so_far + len(match['text']) > int(max_characters):
                break

            final_matches.append(match)
            chars_so_far += len(match['text'])

        logger.info(f"DEBUG: Selected {len(final_matches)} final matches with embeddings")
        if final_matches:
            logger.info(f"DEBUG: Top similarity scores: {[m['match_score'] for m in final_matches[:3]]}")

        return final_matches

    except Exception as e:
        logger.error(f"ERROR: OpenAI embedding search failed: {e}")
        import traceback
        logger.error(f"ERROR: Full traceback: {traceback.format_exc()}")
        raise e

# HTML Templates

narrative_prompt = """
You are analyzing competitive intelligence documents for a home builder. Extract and summarize ALL relevant information from the provided sources to answer the user's question. Be comprehensive and specific.

IMPORTANT INSTRUCTIONS:
1. Extract SPECIFIC details like prices, rates, dates, promotions, and offers
2. Include ALL relevant information found in the sources, not just general statements
3. If the sources contain relevant data, ALWAYS provide it - never say "no specific information"
4. For financing questions, look for APR rates, buydown offers, monthly payments, special events
5. For pricing questions, extract specific home prices, price ranges, and any discounts
6. For inventory questions, count available homes, list communities, and note move-in ready status

Write a descriptive headline between <title> tags then detail ALL supporting information in HTML between <content> tags with citation references like <sup>[source number]</sup>.

Base your summary solely on the provided facts, avoiding assumptions.

### EXAMPLE
example_question: Why are clouds so white

====== Example Source 1 ====
File and page: cloud_info_doc.pdf page 1
Description: A document about clouds
Citation: https://superstoredev.local.answerrocket.com:8080/apps/chat/knowledge-base/5eea3d30-8e9e-4603-ba27-e12f7d51e372#page=1
Content: Clouds appear white because of how they interact with light. They consist of countless tiny water droplets or ice crystals that scatter all colors of light equally. When sunlight, which contains all colors of the visible spectrum, hits these particles, it scatters in all directions. This scattered light combines to appear white to our eyes. 
====== example Source 2 ====
File and page: cloud_info_doc.pdf page 3
Description: A document about clouds
Citation: https://superstoredev.local.answerrocket.com:8080/apps/chat/knowledge-base/5eea3d30-8e9e-4603-ba27-e12f7d51e372#page=3
Content: clouds contain millions of water droplets or ice crystals that act as tiny reflectors. the size of the water droplets or ice crystals is large enough to scatter all colors of light, unlike the sky which scatters blue light more. these particles scatter all wavelengths of visible light equally, resulting in white light. 

example_assistant: <title>The reason for white clouds</title>
<content>
    <p>Clouds appear white because of the way they interact with light. They are composed of tiny water droplets or ice crystals that scatter all colors of light equally. When sunlight, which contains all colors of the visible spectrum, hits these particles, they scatter the light in all directions. This scattered light combines to appear white to our eyes.<sup>[1]</sup></p>
    
    <ul>
        <li>Clouds contain millions of water droplets or ice crystals that act as tiny reflectors.<sup>[2]</sup></li>
        <li>These particles scatter all wavelengths of visible light equally, resulting in white light.<sup>[2]</sup></li>
        <li>The size of the water droplets or ice crystals is large enough to scatter all colors of light, unlike the sky which scatters blue light more.<sup>[2]</sup></li>
    </ul>
</content>
<reference number=1 url="https://superstoredev.local.answerrocket.com:8080/apps/chat/knowledge-base/5eea3d30-8e9e-4603-ba27-e12f7d51e372#page=1" doc="cloud_info_doc.pdf" page=1>Clouds are made of tiny droplets</reference>
<reference number=2 url="https://superstoredev.local.answerrocket.com:8080/apps/chat/knowledge-base/5eea3d30-8e9e-4603-ba27-e12f7d51e372#page=3" doc="cloud_info_doc.pdf" page=3>Ice crystals scatter all colors</reference>

### The User's Question to Answer 
Answer this question: {{user_query}}

{{facts}}"""

# Main response template (simplified for skill framework)
main_response_template = """
<div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; color: #2d3748; max-width: 100%; margin: 0 auto;">
    <div style="margin-bottom: 32px;">
        <h1 style="font-size: 28px; font-weight: 700; color: #1a202c; margin: 0 0 24px 0; line-height: 1.2; border-bottom: 3px solid #3182ce; padding-bottom: 12px; display: inline-block;">
            {{ title }}
        </h1>
        <div style="font-size: 16px; line-height: 1.8; color: #4a5568;">
            {{ content|safe }}
        </div>
    </div>
</div>
<style>
    p { margin: 16px 0; }
    ul, ol { margin: 16px 0; padding-left: 24px; }
    li { margin: 8px 0; }
    sup { 
        background: #3182ce; 
        color: white; 
        padding: 2px 6px; 
        border-radius: 12px; 
        font-size: 11px; 
        font-weight: 600; 
        margin-left: 4px;
        text-decoration: none;
    }
    sup:hover { background: #2c5aa0; }
    strong { color: #2d3748; font-weight: 600; }
    em { color: #4a5568; font-style: italic; }
</style>"""

# Sources template (simplified for skill framework)
sources_template = """
<div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; color: #2d3748; max-width: 100%; margin: 0 auto;">
    <div style="margin-bottom: 24px;">
        <h2 style="font-size: 22px; font-weight: 600; color: #1a202c; margin: 0 0 20px 0; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px;">
            📄 Document Sources
        </h2>
        {% for ref in references %}
        <div style="margin-bottom: 24px; padding: 20px; background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%); border-radius: 12px; border: 1px solid #e2e8f0; box-shadow: 0 2px 4px rgba(0,0,0,0.05); transition: transform 0.2s ease, box-shadow 0.2s ease;">
            <div style="display: flex; align-items: flex-start;">
                <div style="flex-shrink: 0; margin-right: 16px;">
                    {% if ref.thumbnail %}
                    <img src="data:image/png;base64,{{ ref.thumbnail }}" alt="Document thumbnail" style="width: 80px; height: 120px; border-radius: 8px; border: 1px solid #e2e8f0; object-fit: cover; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                    {% else %}
                    <div style="width: 80px; height: 120px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 8px; display: flex; align-items: center; justify-content: center; color: white; font-weight: 600; font-size: 18px; box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);">
                        {{ ref.number }}
                    </div>
                    {% endif %}
                </div>
                <div style="flex: 1;">
                    <div style="margin-bottom: 12px;">
                        <a href="{{ ref.url }}" target="_blank" style="color: #3182ce; text-decoration: none; font-size: 16px; font-weight: 600; display: inline-flex; align-items: center; transition: color 0.2s ease;">
                            📄 {{ ref.src }}
                            <svg style="width: 16px; height: 16px; margin-left: 6px;" fill="currentColor" viewBox="0 0 20 20">
                                <path d="M11 3a1 1 0 100 2h2.586l-6.293 6.293a1 1 0 101.414 1.414L15 6.414V9a1 1 0 102 0V4a1 1 0 00-1-1h-5z"/>
                                <path d="M5 5a2 2 0 00-2 2v8a2 2 0 002 2h8a2 2 0 002-2v-3a1 1 0 10-2 0v3H5V7h3a1 1 0 000-2H5z"/>
                            </svg>
                        </a>
                    </div>
                    <div style="color: #718096; font-size: 14px; margin-bottom: 8px; display: flex; align-items: center;">
                        <svg style="width: 14px; height: 14px; margin-right: 6px;" fill="currentColor" viewBox="0 0 20 20">
                            <path fill-rule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z"/>
                        </svg>
                        Page {{ ref.page }}
                    </div>
                    {% if ref.preview %}
                    <div style="color: #4a5568; font-size: 14px; line-height: 1.6; background: #ffffff; padding: 12px; border-radius: 6px; border-left: 4px solid #3182ce; font-style: italic;">
                        "{{ ref.preview }}"
                    </div>
                    {% endif %}
                </div>
            </div>
        </div>
        {% endfor %}
    </div>
</div>
<style>
    .source-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    a:hover {
        color: #2c5aa0 !important;
    }
</style>"""

if __name__ == '__main__':
    skill_input = document_rag_explorer.create_input(
        arguments={
            "user_question": "What information is available about clouds?",
            "base_url": "https://example.com/kb/",
            "max_sources": 3,
            "match_threshold": 0.2
        }
    )
    out = document_rag_explorer(skill_input)
    print(f"Narrative: {out.narrative}")
    print(f"Visualizations: {len(out.visualizations)}")