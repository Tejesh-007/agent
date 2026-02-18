import logging
from typing import Literal

logger = logging.getLogger("intent_classifier")

CLASSIFICATION_PROMPT = """You are a router. Classify the user question into ONE category:
- sql: database queries, counts, analysis, filtering, statistics, data retrieval
- rag: document content, policies, procedures, uploaded files, reports
- hybrid: needs both database data AND document content

Examples:
Q: "How many customers are in the database?" → sql
Q: "Show me top 10 products by revenue" → sql
Q: "What does the privacy policy say?" → rag
Q: "Summarize the employee handbook" → rag
Q: "Compare sales data with the Q4 report document" → hybrid
Q: "Do customer counts match what's in the board report?" → hybrid

Question: {question}

Respond with ONLY one word: sql, rag, or hybrid"""


def classify_intent(
    question: str, 
    model
) -> Literal["sql", "rag", "hybrid"]:
    """Classify user question intent to route to appropriate agent.
    
    Args:
        question: The user's question
        model: The LangChain chat model instance
        
    Returns:
        One of: "sql", "rag", "hybrid"
    """
    try:
        # Format the prompt with the question
        prompt = CLASSIFICATION_PROMPT.format(question=question)
        
        # Invoke the model
        response = model.invoke(prompt)
        
        # Extract the classification from response
        if hasattr(response, 'content'):
            classification = response.content.strip().lower()
        else:
            classification = str(response).strip().lower()
        
        # Validate and normalize the response
        if "sql" in classification:
            result = "sql"
        elif "rag" in classification:
            result = "rag"
        elif "hybrid" in classification:
            result = "hybrid"
        else:
            # Default to sql if unclear
            logger.warning(
                f"Unclear classification '{classification}' for question: '{question[:50]}...'. "
                "Defaulting to 'sql'"
            )
            result = "sql"
        
        logger.info(
            f"Intent classified as '{result}' for question: '{question[:50]}...'"
        )
        return result
        
    except Exception as e:
        logger.error(
            f"Error classifying intent for question '{question[:50]}...': {e}. "
            "Defaulting to 'sql'"
        )
        return "sql"
