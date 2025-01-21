from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable
from langchain_aws import ChatBedrock
import boto3
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import AnyMessage, add_messages
from langchain_core.messages import ToolMessage
from langchain_core.runnables import RunnableLambda
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph, START
from langgraph.prebuilt import tools_condition

# Fitness Analysis Tool
@tool
def analyze_fitness(workout_data: dict) -> dict:
    """
    Analyzes workout data and provides personalized recommendations.
    
    Args:
        workout_data (dict): Dictionary containing:
            - workout_type: str (e.g., 'cardio', 'strength')
            - duration_minutes: int
            - intensity_level: str ('low', 'medium', 'high')
            - frequency_per_week: int
    
    Returns:
        dict: Analysis results and recommendations
    """
    def calculate_recommendations(data):
        # Calculate optimal workout parameters
        base_duration = data['duration_minutes']
        current_frequency = data['frequency_per_week']
        intensity = data['intensity_level']
        
        # Calculate recommended progression
        if intensity == 'low':
            recommended_duration = min(base_duration + 10, 60)
            recommended_frequency = min(current_frequency + 1, 5)
        elif intensity == 'medium':
            recommended_duration = min(base_duration + 5, 45)
            recommended_frequency = min(current_frequency + 1, 4)
        else:  # high intensity
            recommended_duration = base_duration
            recommended_frequency = min(current_frequency, 3)
            
        return {
            "current_analysis": {
                "workout_level": intensity,
                "weekly_minutes": base_duration * current_frequency
            },
            "recommendations": {
                "target_duration": recommended_duration,
                "target_frequency": recommended_frequency,
                "next_intensity": "medium" if intensity == "low" else "high",
                "rest_days": max(7 - recommended_frequency, 2)
            }
        }
    
    return calculate_recommendations(workout_data)

# Error Handling
def handle_tool_error(state) -> dict:
    """Handles errors during tool execution."""
    error = state.get("error")
    tool_calls = state["messages"][-1].tool_calls
    
    return {
        "messages": [
            ToolMessage(
                content=f"Error: {repr(error)}\nPlease provide valid workout information.",
                tool_call_id=tc["id"],
            )
            for tc in tool_calls
        ]
    }

def create_tool_node_with_fallback(tools: list) -> dict:
    """Creates a tool node with error handling."""
    return ToolNode(tools).with_fallbacks(
        [RunnableLambda(handle_tool_error)],
        exception_key="error"
    )

# State Management
class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]

class Assistant:
    def __init__(self, runnable: Runnable):
        self.runnable = runnable

    def __call__(self, state: State):
        while True:
            result = self.runnable.invoke(state)
            
            if not result.tool_calls and (
                not result.content
                or isinstance(result.content, list)
                and not result.content[0].get("text")
            ):
                messages = state["messages"] + [("user", "Please provide a valid response.")]
                state = {**state, "messages": messages}
            else:
                break

        return {"messages": result}

# LLM Configuration
def get_bedrock_client(region):
    return boto3.client("bedrock-runtime", region_name=region)

def create_bedrock_llm(client):
    return ChatBedrock(
        model_id='anthropic.claude-3-sonnet-20240229-v1:0',
        client=client,
        model_kwargs={'temperature': 0},
        region_name='us-east-1'
    )

llm = create_bedrock_llm(get_bedrock_client(region='us-east-1'))

# Prompt Template
fitness_assistant_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """You are a knowledgeable fitness assistant. Gather the following information:
        - workout type (cardio/strength)
        - workout duration in minutes
        - intensity level (low/medium/high)
        - workouts per week
        
        Ask for clarification if needed. Once you have the information, use the analyze_fitness tool.
        Provide clear, encouraging feedback based on the analysis.
        """,
    ),
    ("placeholder", "{messages}"),
])

# Tools Configuration
fitness_tools = [analyze_fitness]
fitness_assistant_runnable = fitness_assistant_prompt | llm.bind_tools(fitness_tools)

# Graph Construction
builder = StateGraph(State)

# Add nodes
builder.add_node("assistant", Assistant(fitness_assistant_runnable))
builder.add_node("tools", create_tool_node_with_fallback(fitness_tools))

# Add edges
builder.add_edge(START, "assistant")
builder.add_conditional_edges(
    "assistant",
    tools_condition,
)
builder.add_edge("tools", "assistant")

# Memory Configuration
memory = MemorySaver()
graph = builder.compile(checkpointer=memory)

# Example usage (for testing)
if __name__ == "__main__":
    config = {
        "configurable": {
            "thread_id": "fitness-session-1",
        }
    }
    
    test_messages = [
        "I want to improve my workouts",
        "I do cardio for 30 minutes at medium intensity, 3 times per week",
    ]
    
    for message in test_messages:
        response = graph.invoke(
            {"messages": ("user", message)},
            config
        )
        print(f"User: {message}")
        print(f"Assistant: {response['messages'].content}\n")

