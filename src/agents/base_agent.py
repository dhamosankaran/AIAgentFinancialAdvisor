"""
Base class for all financial advisor agents
"""

import logging
from typing import Dict, List, Optional, Any
from langchain_openai import ChatOpenAI
from langchain_core.tools import Tool
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain.memory import ConversationBufferMemory
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_core.runnables import RunnablePassthrough

class BaseFinancialAgent:
    """Base class for all financial advisor agents"""
    
    def __init__(
        self,
        llm: Optional[ChatOpenAI] = None,
        tools: Optional[List[Tool]] = None,
        system_prompt: Optional[str] = None,
        memory: Optional[ConversationBufferMemory] = None
    ):
        """Initialize the base agent"""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.llm = llm or ChatOpenAI(
            model="gpt-4-turbo-preview",
            temperature=0.7
        )
        self.tools = tools or []
        self.system_prompt = system_prompt
        self.memory = memory or ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        # Initialize the agent
        self._initialize_agent()
    
    def _initialize_agent(self):
        """Initialize the agent with tools and memory"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt or "You are a helpful financial advisor."),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        self.agent = create_openai_functions_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
        
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            memory=self.memory,
            verbose=True,
            handle_parsing_errors=True
        )
    
    async def process_message(self, message: str, chat_history: List[Dict[str, str]] = None) -> str:
        """Process a message and return a response"""
        try:
            # Convert chat history to LangChain message format if provided
            if chat_history:
                messages = []
                for msg in chat_history:
                    if msg["role"] == "user":
                        messages.append(HumanMessage(content=msg["content"]))
                    elif msg["role"] == "assistant":
                        messages.append(AIMessage(content=msg["content"]))
                self.memory.chat_memory.messages = messages
            
            # Process the message
            response = await self.agent_executor.ainvoke({"input": message})
            return response["output"]
            
        except Exception as e:
            self.logger.error(f"Error processing message: {str(e)}")
            return f"I apologize, but I encountered an error: {str(e)}"
    
    def get_memory(self) -> List[Dict[str, str]]:
        """Get the current conversation history"""
        messages = self.memory.chat_memory.messages
        return [
            {
                "role": "user" if isinstance(msg, HumanMessage) else "assistant",
                "content": msg.content
            }
            for msg in messages
        ] 