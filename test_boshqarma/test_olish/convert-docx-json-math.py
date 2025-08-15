import docx
import re
import json
import argparse
from typing import List, Dict, Any, Optional, Tuple

def extract_problems(document_path: str) -> List[Dict[str, Any]]:
    """
    Extract math problems from a Word document and convert to JSON with LaTeX notation.
    
    Args:
        document_path: Path to the .docx file
        
    Returns:
        List of problem dictionaries ready for JSON serialization
    """
    # Load the document
    doc = docx.Document(document_path)
    
    problems = []
    current_problem = None
    current_options = []
    correct_option = None
    
    # Regular expressions for parsing
    problem_pattern = re.compile(r'^\s*(\d+)\.\s*(.+)$')
    option_pattern = re.compile(r'^\s*([A-D])\)\s*(.+?)\s*(#)?$')
    
    for paragraph in doc.paragraphs:
        text = paragraph.text.strip()
        if not text:
            continue
        
        # Check if this is a new problem
        problem_match = problem_pattern.match(text)
        if problem_match:
            # Save previous problem if exists
            if current_problem and current_options:
                problems.append(create_problem_dict(current_problem, current_options, correct_option))
                current_options = []
                correct_option = None
            
            # Start new problem
            _, problem_text = problem_match.groups()
            current_problem = problem_text
        else:
            # Check if this is an option
            option_match = option_pattern.match(text)
            if option_match and current_problem:
                option_letter, option_text, is_correct = option_match.groups()
                current_options.append((option_letter, option_text))
                if is_correct:
                    correct_option = option_letter
    
    # Add the last problem
    if current_problem and current_options:
        problems.append(create_problem_dict(current_problem, current_options, correct_option))
    
    return problems

def create_problem_dict(problem_text: str, options: List[Tuple[str, str]], correct_option: Optional[str]) -> Dict[str, Any]:
    """
    Create a dictionary for a single problem with LaTeX notation.
    
    Args:
        problem_text: The text of the problem
        options: List of (letter, text) tuples for each option
        correct_option: The letter of the correct option
        
    Returns:
        Dictionary representation of the problem
    """
    # Convert to LaTeX notation
    problem_latex = convert_to_latex(problem_text)
    
    # Create options list
    options_list = []
    for letter, text in options:
        option_latex = convert_to_latex(text)
        options_list.append({
            letter: option_latex,
            "image": None,
            "is_correct": letter == correct_option
        })
    
    return {
        "question": problem_latex,
        "image": None,
        "options": options_list
    }

def convert_to_latex(text: str) -> str:
    """
    Convert mathematical expressions to LaTeX notation.
    
    Args:
        text: Text with potential mathematical expressions
        
    Returns:
        Text with LaTeX notation for mathematical expressions
    """
    # Replace common mathematical patterns with LaTeX
    # Fractions like a/b
    text = re.sub(r'(\d+)/(\d+)', r'\\frac{\1}{\2}', text)
    
    # Superscripts like x^2
    text = re.sub(r'(\w+)\^(\d+)', r'\1^{\2}', text)
    
    # Basic math operations
    text = re.sub(r'(\d+)\s*×\s*(\w+)', r'\1 \\times \2', text)
    text = re.sub(r'(\d+)\s*:\s*(\d+)', r'\1 : \2', text)
    
    # Check if the text contains mathematical expressions
    # If it contains operation symbols or other indicators, wrap in $
    math_indicators = ['\\frac', '\\times', ':', '=', '<', '>', '+', '-', '/', '\\cdot', '^']
    needs_math_delimiters = any(indicator in text for indicator in math_indicators)
    
    if needs_math_delimiters:
        # Make sure we're not double-wrapping already LaTeX-formatted text
        if not (text.startswith('$') and text.endswith('$')):
            text = f'${text}$'
    
    return text

def main():
    parser = argparse.ArgumentParser(description='Convert math problems from DOCX to LaTeX JSON')
    parser.add_argument('input_file', help='Path to the input DOCX file')
    parser.add_argument('output_file', help='Path to the output JSON file')
    
    args = parser.parse_args()
    
    try:
        problems = extract_problems(args.input_file)
        
        # Write to JSON file
        with open(args.output_file, 'w', encoding='utf-8') as f:
            json.dump(problems, f, ensure_ascii=False, indent=2)
        
        print(f"Successfully converted {len(problems)} problems to {args.output_file}")
    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()