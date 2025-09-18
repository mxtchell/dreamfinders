# Clean version of find_matching_documents with enhanced keyword matching

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