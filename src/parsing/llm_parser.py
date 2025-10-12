#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM-based Parser for Exam Papers

Uses LangChain and an LLM to transpile Markdown exam files into structured JSON.
"""

import logging
from typing import Dict, List, Optional, Any

from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain.output_parsers import PydanticOutputParser

# Configure logging
logger = logging.getLogger(__name__)

# --- Pydantic Models for Structured Output ---

class ExamOption(BaseModel):
    A: str = Field(description="Option A text")
    B: str = Field(description="Option B text")
    C: str = Field(description="Option C text")
    D: str = Field(description="Option D text")

class EssayQuestion(BaseModel):
    question_number: int = Field(description="The number of the essay question")
    content: str = Field(description="The full text of the essay question")
    points: int = Field(description="The points allocated to the question")

class MultipleChoiceQuestion(BaseModel):
    question_number: int = Field(description="The number of the multiple-choice question")
    content: str = Field(description="The full text of the multiple-choice question")
    options: ExamOption = Field(description="The four options for the question")
    points: int = Field(description="The points allocated to the question, typically 2")

class ExamMetadata(BaseModel):
    exam_title: str = Field(description="The main title of the exam")
    course_name: str = Field(description="The subject name of the exam")
    exam_duration: str = Field(description="The duration of the exam")

class QuestionPaper(BaseModel):
    exam_metadata: ExamMetadata = Field(description="Metadata about the exam")
    essay_section: List[EssayQuestion] = Field(description="List of all essay questions")
    multiple_choice_section: List[MultipleChoiceQuestion] = Field(description="List of all multiple-choice questions")

class AnswerKey(BaseModel):
    answers: Dict[str, str] = Field(description="A mapping of question number (as string) to the correct letter answer")

# --- LLM Parsing Functions ---

def get_llm_parser_chain(output_model):
    """Creates a LangChain chain with a specified Pydantic output model."""
    # Set up a parser
    parser = PydanticOutputParser(pydantic_object=output_model)

    # Initialize the LLM
    # Expects OPENAI_API_KEY to be in the environment (e.g., from a .env file)
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    # Create the prompt with specialized instructions for exam parsing
    if output_model == QuestionPaper:
        template = """
        You are an expert at parsing Chinese exam papers. Your task is to extract exam content into structured JSON.
        
        IMPORTANT INSTRUCTIONS FOR MULTIPLE CHOICE QUESTIONS:
        1. Look for numbered questions (1, 2, 3, etc.) in the "乙、測驗題部分" section
        2. Each question starts with a number followed by the question text
        3. The options are concatenated together WITHOUT (A), (B), (C), (D) labels
        4. You must intelligently split the concatenated options into exactly 4 parts (A, B, C, D)
        5. Look for natural sentence boundaries, repeated patterns, or logical breaks
        6. Each option typically represents a complete statement or phrase
        
        EXAMPLE FORMAT YOU'LL SEE:
        "1 Question text here?
        Option1 text here Option2 text here Option3 text here Option4 text here"
        
        YOU MUST CONVERT THIS TO:
        - A: "Option1 text here"
        - B: "Option2 text here" 
        - C: "Option3 text here"
        - D: "Option4 text here"
        
        For essay questions in "甲、申論題部分", extract normally.
        
        {format_instructions}
        
        --- CONTENT BEGINS ---
        {content}
        --- CONTENT ENDS ---
        """
    else:
        template = """
        You are an expert data extraction assistant.
        Your task is to parse the user's text content and extract the information into a specific JSON format.
        Please populate all fields accurately.
        {format_instructions}
        Here is the content to parse:
        --- CONTENT BEGINS ---
        {content}
        --- CONTENT ENDS ---
        """

    prompt = PromptTemplate(
        template=template,
        input_variables=["content"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    # Create the chain
    chain = prompt | llm | parser
    return chain

def parse_questions_with_llm(markdown_content: str) -> Optional[QuestionPaper]:
    """Parses the question paper markdown to a structured QuestionPaper object."""
    logger.info("Starting question paper parsing with LLM...")
    try:
        chain = get_llm_parser_chain(QuestionPaper)
        parsed_result = chain.invoke({"content": markdown_content})
        logger.info("Successfully parsed question paper.")
        return parsed_result
    except Exception as e:
        # Try to extract JSON from markdown code block if parser failed
        error_msg = str(e)
        if "Invalid json output:" in error_msg or "```json" in error_msg:
            logger.warning("Attempting to extract JSON from markdown code block...")
            try:
                import re
                import json
                # Extract JSON from error message or try to get raw response
                json_match = re.search(r'```json\s*(\{.*?\})\s*```', error_msg, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                    # Fix invalid escape sequences by doubling backslashes
                    # This handles LaTeX escapes like \%, \cdot, \underline, etc.
                    # We need to be careful not to break valid JSON escapes like \n, \t, \uXXXX
                    import re
                    def fix_escape(match):
                        next_char = match.group(1) if match.group(1) else ''
                        # Valid JSON escapes: \n, \t, \r, \b, \f, \", \\, \/
                        if next_char in ['n', 't', 'r', 'b', 'f', '"', '/', '\\']:
                            return match.group(0)  # Keep valid escapes
                        # Check for valid Unicode escape: \uXXXX (4 hex digits)
                        if next_char == 'u':
                            remaining = match.string[match.end():]
                            if len(remaining) >= 4 and all(c in '0123456789abcdefABCDEF' for c in remaining[:4]):
                                return match.group(0)  # Valid Unicode escape
                        # All other cases: double the backslash
                        return '\\\\' + next_char

                    json_str = re.sub(r'\\(.?)', fix_escape, json_str)
                    json_data = json.loads(json_str)
                    parsed_result = QuestionPaper(**json_data)
                    logger.info("Successfully extracted and parsed JSON from code block.")
                    return parsed_result
            except Exception as parse_error:
                logger.error(f"Failed to extract JSON from code block: {parse_error}")

        logger.error(f"Failed to parse question paper with LLM: {e}")
        return None

def parse_answers_with_llm(markdown_content: str) -> Optional[AnswerKey]:
    """Parses the answer sheet markdown to a structured AnswerKey object."""
    logger.info("Starting answer key parsing with LLM...")
    try:
        chain = get_llm_parser_chain(AnswerKey)
        parsed_result = chain.invoke({"content": markdown_content})
        logger.info(f"Successfully parsed answer key.")
        return parsed_result
    except Exception as e:
        # Try to extract JSON from markdown code block if parser failed
        error_msg = str(e)
        if "Invalid json output:" in error_msg or "```json" in error_msg:
            logger.warning("Attempting to extract JSON from markdown code block...")
            try:
                import re
                import json
                # Extract JSON from error message
                json_match = re.search(r'```json\s*(\{.*?\})\s*```', error_msg, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                    # Fix invalid escape sequences (same as in parse_questions_with_llm)
                    def fix_escape(match):
                        next_char = match.group(1) if match.group(1) else ''
                        # Valid JSON escapes: \n, \t, \r, \b, \f, \", \\, \/
                        if next_char in ['n', 't', 'r', 'b', 'f', '"', '/', '\\']:
                            return match.group(0)
                        # Check for valid Unicode escape: \uXXXX (4 hex digits)
                        if next_char == 'u':
                            remaining = match.string[match.end():]
                            if len(remaining) >= 4 and all(c in '0123456789abcdefABCDEF' for c in remaining[:4]):
                                return match.group(0)
                        return '\\\\' + next_char
                    json_str = re.sub(r'\\(.?)', fix_escape, json_str)
                    json_data = json.loads(json_str)
                    parsed_result = AnswerKey(**json_data)
                    logger.info("Successfully extracted and parsed JSON from code block.")
                    return parsed_result
            except Exception as parse_error:
                logger.error(f"Failed to extract JSON from code block: {parse_error}")

        logger.error(f"Failed to parse answer key with LLM: {e}")
        return None

# --- Merging Function ---

def merge_qa_json(questions: QuestionPaper, answers: AnswerKey) -> Dict[str, Any]:
    """Merges the parsed questions and answers into the final JSON structure."""
    logger.info("Merging parsed questions and answers...")
    
    # Convert Pydantic models to dictionaries
    q_dict = questions.dict()
    a_dict = answers.dict()

    # Inject correct answers into the multiple-choice questions
    for question in q_dict.get("multiple_choice_section", []):
        q_num_str = str(question["question_number"])
        if q_num_str in a_dict.get("answers", {}):
            question["correct_answer"] = a_dict["answers"][q_num_str]

    # Reconstruct the final dictionary in the desired format
    final_json = {
        "exam_metadata": q_dict.get("exam_metadata"),
        "essay_section": {
            "questions": q_dict.get("essay_section", [])
        },
        "multiple_choice_section": {
            "questions": q_dict.get("multiple_choice_section", [])
        },
        "answer_key": a_dict
    }
    
    logger.info("Successfully merged JSON data.")
    return final_json
