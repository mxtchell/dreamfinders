# Enhanced keyword matching for competitive intelligence

def enhanced_find_matching_documents(user_question, topics, loaded_sources, base_url, max_sources, match_threshold, max_characters):
    """Find documents using enhanced keyword matching optimized for competitive intelligence"""
    import logging
    from types import SimpleNamespace

    logger = logging.getLogger(__name__)
    logger.info("DEBUG: Using enhanced keyword matching for document search")
    logger.info(f"DEBUG: Question: {user_question}")

    # Analyze question intent to determine search strategy
    question_lower = user_question.lower() if user_question else ""

    # Detect if question is about both competitors or just one
    mentions_lennar = "lennar" in question_lower
    mentions_meritage = "meritage" in question_lower
    mentions_both = mentions_lennar and mentions_meritage
    mentions_competitors = any(word in question_lower for word in ["competitors", "competition", "both", "compare"])

    # Build comprehensive search terms with synonyms
    search_terms = []
    if user_question:
        search_terms.append(user_question)

    # Aggressive keyword expansion based on domain
    keyword_expansions = {
        'financing': ['financing', 'finance', 'mortgage', 'loan', 'apr', 'rate', 'payment', 'buydown',
                     'interest', 'monthly payment', 'qualification', 'credit', 'lending', 'lender'],
        'special': ['special', 'promotion', 'offer', 'event', 'sale', 'limited time', 'exclusive',
                   'discount', 'incentive', 'deal', 'savings', 'national sales event'],
        'price': ['price', 'pricing', 'cost', '$', 'reduction', 'reduced', 'discount', 'drop',
                 'decrease', 'lower', 'affordable', 'starting from', 'base price'],
        'inventory': ['inventory', 'available', 'availability', 'move-in ready', 'quick move',
                     'homes available', 'in stock', 'ready now', 'immediate'],
        'home': ['home', 'house', 'property', 'residence', 'unit', 'model', 'floor plan', 'community'],
        'new': ['new', 'latest', 'current', 'upcoming', 'recent', 'now', 'today']
    }

    # Add relevant expansions
    for key, expansions in keyword_expansions.items():
        if key in question_lower:
            search_terms.extend(expansions)

    # Add specific competitor terms if mentioned
    if mentions_lennar or mentions_competitors:
        search_terms.extend(['lennar', 'len'])
    if mentions_meritage or mentions_competitors:
        search_terms.extend(['meritage', 'mhi'])

    search_terms.extend([topic for topic in topics if topic])

    # Remove duplicates while preserving order
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

        # Apply minimum threshold
        if score >= float(match_threshold):
            source_copy = source.copy()
            source_copy['match_score'] = score

            # Generate correct URLs
            if "Lennar" in source_copy['file_name']:
                doc_id = "abb40c5f-f259-48bf-85c3-d2ed1ea956b8"
            elif "Meritage" in source_copy['file_name']:
                doc_id = "7f0292db-d935-4c90-b65b-897bb98167f9"
            else:
                doc_id = "unknown"

            source_copy['url'] = f"https://dreamfinders.poc.answerrocket.com/apps/system/knowledge-base/{doc_id}#page={source_copy['chunk_index']}"
            scored_sources.append(source_copy)

    logger.info(f"DEBUG: {len(scored_sources)} documents passed threshold of {match_threshold}")

    # Sort by score
    scored_sources.sort(key=lambda x: x['match_score'], reverse=True)

    # Intelligent source selection
    matches = []
    chars_so_far = 0
    has_lennar = False
    has_meritage = False

    # If asking about both or comparing, try to get at least one from each
    wants_both = mentions_both or mentions_competitors or \
                any(word in question_lower for word in ['compare', 'versus', 'vs', 'and', 'both'])

    # First pass: get best matches respecting diversity if needed
    for source in scored_sources:
        if len(matches) >= int(max_sources):
            break

        if chars_so_far + len(source['text']) > int(max_characters):
            # If we need both companies and don't have one yet, skip this and look for smaller docs
            if wants_both and len(matches) < 2 and (not has_lennar or not has_meritage):
                continue
            # Otherwise respect the limit after minimum docs
            if len(matches) >= 2:
                break

        # Track which companies we have
        if "Lennar" in source['file_name']:
            # Skip if we want only Meritage
            if mentions_meritage and not mentions_lennar and not mentions_both:
                continue
            has_lennar = True
        elif "Meritage" in source['file_name']:
            # Skip if we want only Lennar
            if mentions_lennar and not mentions_meritage and not mentions_both:
                continue
            has_meritage = True

        matches.append(source)
        chars_so_far += len(source['text'])

    # Second pass: if we want both but missing one, find it
    if wants_both and len(matches) < int(max_sources):
        if not has_lennar:
            for source in scored_sources:
                if "Lennar" in source['file_name'] and source not in matches:
                    matches.append(source)
                    logger.info("DEBUG: Added Lennar doc to ensure both companies represented")
                    break
        if not has_meritage:
            for source in scored_sources:
                if "Meritage" in source['file_name'] and source not in matches:
                    matches.append(source)
                    logger.info("DEBUG: Added Meritage doc to ensure both companies represented")
                    break

    logger.info(f"DEBUG: Selected {len(matches)} final documents")
    if matches:
        lennar_count = sum(1 for m in matches if "Lennar" in m['file_name'])
        meritage_count = sum(1 for m in matches if "Meritage" in m['file_name'])
        logger.info(f"DEBUG: Distribution - Lennar: {lennar_count}, Meritage: {meritage_count}")
        logger.info(f"DEBUG: Top scores: {[m['match_score'] for m in matches[:3]]}")

    return [SimpleNamespace(**match) for match in matches]


def calculate_enhanced_relevance(text, search_terms, file_name):
    """Enhanced relevance scoring optimized for competitive intelligence"""
    import logging
    logger = logging.getLogger(__name__)

    text_lower = text.lower()
    score = 0.0
    matches_found = []

    # High-value competitive intelligence keywords
    critical_keywords = {
        # Financing terms
        'apr': 0.5, 'rate': 0.4, 'buydown': 0.6, 'mortgage': 0.4, 'financing': 0.5,
        'payment': 0.3, 'monthly': 0.3, 'qualification': 0.3, 'credit': 0.3,

        # Promotional terms
        'special': 0.5, 'event': 0.4, 'promotion': 0.5, 'limited': 0.4, 'offer': 0.4,
        'sale': 0.4, 'national': 0.3, 'exclusive': 0.4, 'incentive': 0.5,

        # Pricing terms
        'price': 0.4, 'reduction': 0.5, 'reduced': 0.5, 'discount': 0.5,
        '$': 0.3, 'cost': 0.3, 'affordable': 0.3, 'starting': 0.3,

        # Inventory terms
        'available': 0.3, 'inventory': 0.4, 'move-in': 0.4, 'ready': 0.3,
        'quick': 0.3, 'immediate': 0.3,

        # Competitor names
        'lennar': 0.3, 'meritage': 0.3
    }

    # Check for critical keywords first
    for keyword, weight in critical_keywords.items():
        if keyword in text_lower:
            count = text_lower.count(keyword)
            keyword_score = min(count * weight, weight * 2)  # Cap at 2x weight
            score += keyword_score
            matches_found.append(f"{keyword}({count})")

    # Check search terms
    for term in search_terms:
        if not term:
            continue

        term_lower = term.lower()

        # Exact phrase match (highest value)
        if len(term_lower) > 3 and term_lower in text_lower:
            occurrences = text_lower.count(term_lower)
            phrase_score = min(occurrences * 0.6, 1.5)
            score += phrase_score
            matches_found.append(f"exact:{term_lower}")
            continue

        # Word-by-word matching
        words = term_lower.split()
        matched_words = 0

        for word in words:
            if len(word) < 3:
                continue

            if word in text_lower:
                matched_words += 1
                occurrences = text_lower.count(word)

                # Boost important words
                if word in critical_keywords:
                    word_score = critical_keywords[word] * min(occurrences, 3)
                else:
                    word_score = min(occurrences * 0.15, 0.4)

                score += word_score

        # Completeness bonus - reward if most words from search term are found
        if len(words) > 1 and matched_words > 0:
            completeness = matched_words / len(words)
            if completeness >= 0.7:
                score += 0.3
            elif completeness >= 0.5:
                score += 0.15

    # Special patterns that indicate high relevance
    high_value_patterns = [
        ('national sales event', 0.8),
        ('special financing', 0.7),
        ('limited time', 0.5),
        ('move-in ready', 0.5),
        ('price reduction', 0.6),
        ('apr buydown', 0.8),
        ('closing cost', 0.5),
        ('monthly payment', 0.5)
    ]

    for pattern, weight in high_value_patterns:
        if pattern in text_lower:
            score += weight
            matches_found.append(f"pattern:{pattern}")

    # File name bonus - if searching for specific company
    file_lower = file_name.lower()
    if "lennar" in file_lower and any("lennar" in str(t).lower() for t in search_terms):
        score += 0.2
    if "meritage" in file_lower and any("meritage" in str(t).lower() for t in search_terms):
        score += 0.2

    # Normalize score
    final_score = min(score / 3.0, 1.0)  # Aggressive normalization

    # Debug logging for high scores
    if final_score > 0.3 and matches_found:
        logger.debug(f"MATCH {final_score:.3f}: {file_name} - Found: {matches_found[:5]}")

    return final_score