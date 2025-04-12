import os
from dotenv import load_dotenv
from portia import (
    Config,
    LLMModel,
    LLMProvider,
    Portia,
    example_tool_registry,
)

# Load .env variables
load_dotenv()
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

# Validate key presence
if not ANTHROPIC_API_KEY:
    raise ValueError("Claude API key not found in .env!")

# Set up config using Claude 3.5 Sonnet
anthropic_config = Config.from_default(
    llm_provider=LLMProvider.ANTHROPIC,
    llm_model_name=LLMModel.CLAUDE_3_5_SONNET,
    anthropic_api_key=ANTHROPIC_API_KEY
)

# Initialize Portia
portia = Portia(config=anthropic_config, tools=example_tool_registry)

# Sample code diff (could be fetched dynamically from a GitHub PR)
pr_diff = '''
function processPayment(user_id, amount) {
    if (amount < 0) {
        console.log("Amount cannot be negative");
        return false;
    }
    let paymentProcessed = false;
    if (amount > 1000) {
        // Some complex logic
        paymentProcessed = true;
    }
    // more code here
    return paymentProcessed;
}
'''

# Run Portia for code review
def review_code(diff: str):
    review_result = portia.run(f"Review the following code for readability, function length, naming conventions, and possible improvements:\n{diff}")
    return review_result.model_dump_json(indent=2)

# Get the review
review_feedback = review_code(pr_diff)

# Print the review
print(review_feedback)
