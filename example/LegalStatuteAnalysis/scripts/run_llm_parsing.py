#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Run the LLM-based parsing workflow.

This script orchestrates the parsing of exam files using the LLM parser module.

Usage:
    python scripts/run_llm_parsing.py \
        --questions_file results/mineru_batch/113190_60150(5601).md \
        --answers_file results/mineru_batch/113190_ANS5601.md \
        --output_file results/exam_113_complete_llm.json
"""

import argparse
import json
import logging
from pathlib import Path
import sys

# Add project root to sys.path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from src.parsing.llm_parser import (
    parse_questions_with_llm,
    parse_answers_with_llm,
    merge_qa_json,
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    """Main function to run the parsing workflow."""
    # Load environment variables from .env file
    load_dotenv()

    parser = argparse.ArgumentParser(description="Run the LLM-based exam parsing workflow.")
    parser.add_argument("--questions_file", type=Path, required=True, help="Path to the questions markdown file.")
    parser.add_argument("--answers_file", type=Path, required=True, help="Path to the answers markdown file.")
    parser.add_argument("--output_file", type=Path, required=True, help="Path to save the final JSON output.")
    args = parser.parse_args()

    logging.info(f"Starting LLM parsing workflow for {args.questions_file.name}")

    # --- Read input files ---
    try:
        q_content = args.questions_file.read_text(encoding="utf-8")
        a_content = args.answers_file.read_text(encoding="utf-8")
    except FileNotFoundError as e:
        logging.error(f"Error reading files: {e}")
        return

    # --- Run LLM Parsing Pipelines ---
    questions_result = parse_questions_with_llm(q_content)
    if not questions_result:
        logging.error("The question parsing pipeline failed. Aborting.")
        return

    answers_result = parse_answers_with_llm(a_content)
    if not answers_result:
        logging.error("The answer parsing pipeline failed. Aborting.")
        return

    # --- Merge and Save ---
    final_json = merge_qa_json(questions_result, answers_result)
    
    try:
        args.output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(args.output_file, 'w', encoding='utf-8') as f:
            json.dump(final_json, f, ensure_ascii=False, indent=2)
        logging.info(f"[SUCCESS] Workflow complete. Output saved to {args.output_file}")
    except IOError as e:
        logging.error(f"Error writing output file: {e}")

if __name__ == "__main__":
    main()
