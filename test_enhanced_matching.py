#!/usr/bin/env python3

import sys
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

# Test cases
mock_sources = [
    {
        'text': 'Lennar offers special financing with 2.99% APR for qualified buyers during our National Sales Event. Limited time offer with reduced closing costs.',
        'file_name': 'Lennar_Competitor_Analysis.pdf',
        'chunk_index': 1,
        'description': 'Lennar financing promotion'
    },
    {
        'text': 'Meritage Homes National Sales Event featuring special buydown programs and move-in ready homes with incentives.',
        'file_name': 'Meritage_Market_Data.pdf',
        'chunk_index': 2,
        'description': 'Meritage inventory and pricing'
    },
    {
        'text': 'Standard home pricing information for the market. Base prices start from $300,000 for new construction.',
        'file_name': 'Generic_Market_Report.pdf',
        'chunk_index': 3,
        'description': 'General market data'
    }
]

def test_company_prioritization():
    """Test that company-specific questions prioritize the right company"""
    print("=== TESTING COMPANY PRIORITIZATION ===")
    print()

    # Simulate the logic from find_matching_documents
    def test_question_logic(question, expected_company):
        question_lower = question.lower()
        mentions_lennar = "lennar" in question_lower
        mentions_meritage = "meritage" in question_lower
        mentions_both = mentions_lennar and mentions_meritage
        wants_comparison = any(word in question_lower for word in ["competitors", "competition", "both", "compare", "versus", "vs"])

        company_specific = mentions_lennar and not mentions_meritage  # Only Lennar
        company_specific_meritage = mentions_meritage and not mentions_lennar  # Only Meritage

        print(f"Question: {question}")
        print(f"  mentions_lennar: {mentions_lennar}")
        print(f"  mentions_meritage: {mentions_meritage}")
        print(f"  mentions_both: {mentions_both}")
        print(f"  wants_comparison: {wants_comparison}")
        print(f"  company_specific (Lennar): {company_specific}")
        print(f"  company_specific_meritage: {company_specific_meritage}")

        if company_specific:
            detected = "Lennar"
        elif company_specific_meritage:
            detected = "Meritage"
        elif wants_comparison or mentions_both:
            detected = "Both"
        else:
            detected = "None"

        print(f"  Expected: {expected_company}, Detected: {detected}")
        print(f"  ✅ PASS" if detected == expected_company else f"  ❌ FAIL")
        print()
        return detected == expected_company

    # Test cases
    test_cases = [
        ("Are there any special financing programs currently available at Meritage?", "Meritage"),
        ("What special financing options does Lennar offer?", "Lennar"),
        ("Compare Lennar and Meritage financing options", "Both"),
        ("What are the differences between Lennar and Meritage homes?", "Both"),
        ("Tell me about competitors in the market", "Both"),
        ("What financing is available?", "None"),  # Generic question
    ]

    passed = 0
    for question, expected in test_cases:
        if test_question_logic(question, expected):
            passed += 1

    print(f"=== RESULTS: {passed}/{len(test_cases)} tests passed ===")
    return passed == len(test_cases)

def test_enhanced_matching():
    print("=== TESTING ENHANCED KEYWORD MATCHING ===")
    print()

    # Test 1: Financing question about both competitors
    question1 = "What special financing options do Lennar and Meritage offer?"
    search_terms1 = ['special', 'financing', 'lennar', 'meritage', 'apr', 'offer', 'buydown', 'national sales event']

    print(f"TEST 1: {question1}")
    print(f"Search terms: {search_terms1}")
    print()

    scores1 = []
    for i, source in enumerate(mock_sources):
        score = calculate_enhanced_relevance(source['text'], search_terms1, source['file_name'])
        scores1.append((score, source))
        print(f"Source {i+1}: {source['file_name']} = Score {score:.3f}")
        print(f"  Text: {source['text'][:80]}...")
        print()

    # Sort by score
    scores1.sort(key=lambda x: x[0], reverse=True)
    print("Ranking by relevance:")
    for i, (score, source) in enumerate(scores1):
        print(f"{i+1}. {source['file_name']} (Score: {score:.3f})")
    print()

    # Test 2: Meritage-specific question
    question2 = "Does Meritage have move-in ready homes available?"
    search_terms2 = ['meritage', 'move-in ready', 'available', 'homes', 'inventory']

    print(f"TEST 2: {question2}")
    print(f"Search terms: {search_terms2}")
    print()

    scores2 = []
    for i, source in enumerate(mock_sources):
        score = calculate_enhanced_relevance(source['text'], search_terms2, source['file_name'])
        scores2.append((score, source))
        print(f"Source {i+1}: {source['file_name']} = Score {score:.3f}")
        print(f"  Text: {source['text'][:80]}...")
        print()

    # Sort by score
    scores2.sort(key=lambda x: x[0], reverse=True)
    print("Ranking by relevance:")
    for i, (score, source) in enumerate(scores2):
        print(f"{i+1}. {source['file_name']} (Score: {score:.3f})")
    print()

    print("=== TEST SUMMARY ===")
    print(f"Test 1 (Both competitors): Best match = {scores1[0][1]['file_name']} ({scores1[0][0]:.3f})")
    print(f"Test 2 (Meritage specific): Best match = {scores2[0][1]['file_name']} ({scores2[0][0]:.3f})")

    # Check if both competitors appear in top results for comparison question
    top_2_files_test1 = [scores1[0][1]['file_name'], scores1[1][1]['file_name']]
    has_both = any('Lennar' in f for f in top_2_files_test1) and any('Meritage' in f for f in top_2_files_test1)
    print(f"Test 1 has both competitors in top 2: {has_both}")

if __name__ == "__main__":
    test_company_prioritization()
    print()
    test_enhanced_matching()