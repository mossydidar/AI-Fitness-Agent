# AI Fitness Agent with LangGraph

This repository contains an example implementation of an AI fitness agent built using LangGraph. The agent helps users analyze their workout data and provides personalized fitness recommendations.

## Features

- Interactive conversation to gather workout information
- Analysis of workout patterns
- Personalized recommendations for workout duration and frequency
- Progress tracking capabilities
- Error handling and state management

## Prerequisites

- Python 3.8+
- AWS Account with Bedrock access
- Required Python packages (see requirements.txt)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/mossydidar/ai-fitness-agent.git
cd ai-fitness-agent
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the root directory with the following variables:
```
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
LANGCHAIN_API_KEY=your_api_key
LANGCHAIN_PROJECT=ai-fitness-agent
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=us-east-1
```

## Usage

1. Start LangGraph Studio:
```bash
langgraph studio start
```

2. Load the project in LangGraph Studio using the `langgraph.json` configuration.

3. Interact with the agent through the LangGraph Studio interface.

Example conversation:
```
User: "I want to improve my workout routine"
Agent: "I'd be happy to help you improve your workout routine. Could you please tell me:
1. What type of workout do you currently do (cardio or strength)?
2. How long are your typical workouts (in minutes)?
3. What's your current intensity level (low, medium, or high)?
4. How many times per week do you work out?"

User: "I do cardio for 30 minutes at medium intensity, 3 times per week"
Agent: [Provides personalized analysis and recommendations]
```

## File Structure

- `agent.py`: Main implementation of the fitness agent
- `langgraph.json`: Configuration file for LangGraph Studio
- `requirements.txt`: Python package dependencies

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
