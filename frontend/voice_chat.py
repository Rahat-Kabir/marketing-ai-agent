from neo.graph import build_graph, AgentState
from neo.voice import record_audio_until_stop, play_audio, transcribe_audio
from neo.prompts import neo_voice_system_prompt
from langchain_core.messages import AIMessageChunk, HumanMessage, SystemMessage
from typing import AsyncGenerator, Any
from langgraph.graph import StateGraph
from langgraph.types import Command
import json
import asyncio


async def stream_graph_responses(
        input: dict[str, Any],
        graph: StateGraph,
        **kwargs
        ) -> AsyncGenerator[str, None]:
    """Asynchronously stream the result of the graph run.

    Args:
        input: The input to the graph.
        graph: The compiled graph.
        **kwargs: Additional keyword arguments.

    Returns:
        str: The final LLM or tool call response
    """
    async for message_chunk, metadata in graph.astream(
        input=input,
        stream_mode="messages",
        **kwargs
        ):
        if isinstance(message_chunk, AIMessageChunk):
            if message_chunk.response_metadata:
                finish_reason = message_chunk.response_metadata.get("finish_reason", "")
                if finish_reason == "tool_calls":
                    yield "\n\n"

            if message_chunk.tool_call_chunks:
                tool_chunk = message_chunk.tool_call_chunks[0]

                tool_name = tool_chunk.get("name", "")
                args = tool_chunk.get("args", "")

                if tool_name:
                    tool_call_str = f"\n\n< TOOL CALL: {tool_name} >\n\n"
                if args:
                    tool_call_str = args

                yield tool_call_str
            else:
                yield message_chunk.content
            continue


async def stream_voice_responses(
        input: dict[str, Any],
        graph: StateGraph,
        **kwargs
        ) -> tuple[AsyncGenerator[str, None], AsyncGenerator[str, None]]:
    """Stream responses with separate console and voice outputs.

    Args:
        input: The input to the graph.
        graph: The compiled graph.
        **kwargs: Additional keyword arguments.

    Returns:
        tuple: (console_stream, voice_stream)
            - console_stream: All output including tool calls (for display)
            - voice_stream: Only AI content (for TTS)
    """
    console_content = []
    voice_content = []
    
    async def console_generator():
        for item in console_content:
            yield item
    
    async def voice_generator():
        for item in voice_content:
            yield item
    
    # Collect all chunks first
    async for message_chunk, metadata in graph.astream(
        input=input,
        stream_mode="messages",
        **kwargs
        ):
        if isinstance(message_chunk, AIMessageChunk):
            if message_chunk.response_metadata:
                finish_reason = message_chunk.response_metadata.get("finish_reason", "")
                if finish_reason == "tool_calls":
                    console_content.append("\n\n")

            if message_chunk.tool_call_chunks:
                tool_chunk = message_chunk.tool_call_chunks[0]

                tool_name = tool_chunk.get("name", "")
                args = tool_chunk.get("args", "")

                if tool_name:
                    tool_call_str = f"\n\n< TOOL CALL: {tool_name} >\n\n"
                    console_content.append(tool_call_str)
                if args:
                    console_content.append(args)
                # Note: Tool calls are NOT added to voice_content
            else:
                # Only add actual AI message content to both console and voice
                if message_chunk.content:
                    console_content.append(message_chunk.content)
                    voice_content.append(message_chunk.content)
    
    return console_generator(), voice_generator()


async def get_voice_input() -> str:
    """Get user input via voice recording and transcription."""
    print("Press Enter and speak your message. Press Enter again when done.")
    
    # Record audio
    audio_data = record_audio_until_stop()
    
    if not audio_data:
        print("No audio recorded. Please try again.")
        return ""
    
    # Transcribe audio
    print("Transcribing...")
    text = transcribe_audio(audio_data)
    
    if not text:
        print("Could not transcribe audio. Please try again.")
        return ""
    
    print(f"You said: {text}")
    return text


async def play_response(response_text: str):
    """Play the agent's response using text-to-speech."""
    if response_text.strip():
        play_audio(response_text)


async def main():
    try:
        print("Initializing voice-enabled CRM assistant...")
        graph = await build_graph()

        config = {
            "configurable": {
                "thread_id": "voice_1"
            }
        }
        yolo_mode = False

        # Initial greeting with voice-optimized prompt
        graph_input = AgentState(
            messages=[
                SystemMessage(content=neo_voice_system_prompt),
                HumanMessage(content="Briefly introduce yourself and offer to help me.")
            ],
            yolo_mode=yolo_mode
        )

        print("Voice assistant ready! Listening for your first message...")
        
        while True:
            print(f"\n ---- Assistant ---- \n")
            
            # Get separate streams for console and voice
            console_stream, voice_stream = await stream_voice_responses(graph_input, graph, config=config)
            
            # Display console output (includes tool calls)
            async for response in console_stream:
                print(response, end="", flush=True)
            
            # Collect voice content (excludes tool calls)
            voice_text = ""
            async for voice_content in voice_stream:
                voice_text += voice_content

            # Play only the voice content via TTS
            await play_response(voice_text)

            thread_state = graph.get_state(config=config)

            # Handle human approval interrupts
            while thread_state.interrupts:
                for interrupt in thread_state.interrupts:
                    print("\n ----- ✅ / ❌ Human Approval Required ----- \n")
                    interrupt_json_str = json.dumps(interrupt.value, indent=2, ensure_ascii=False)
                    print(interrupt_json_str)
                    
                    # Use voice for approval
                    play_audio("I need your approval to proceed. Please say continue, update, or feedback.")
                    
                    approval_input = await get_voice_input()
                    if not approval_input:
                        continue
                        
                    # Simple keyword matching for voice commands
                    approval_lower = approval_input.lower()
                    if "continue" in approval_lower:
                        action = "continue"
                        data = None
                    elif "update" in approval_lower:
                        action = "update"
                        play_audio("Please provide the update data.")
                        data = await get_voice_input()
                    elif "feedback" in approval_lower:
                        action = "feedback"
                        play_audio("Please provide your feedback.")
                        data = await get_voice_input()
                    else:
                        play_audio("I didn't understand. Please say continue, update, or feedback.")
                        continue

                    print(f" ----- Assistant ----- \n")
                    
                    # Get separate streams for approval response
                    approval_console_stream, approval_voice_stream = await stream_voice_responses(Command(resume={"action": action, "data": data}), graph, config=config)
                    
                    # Display console output
                    async for response in approval_console_stream:
                        print(response, end="", flush=True)
                    
                    # Collect and play voice content only
                    approval_voice_text = ""
                    async for voice_content in approval_voice_stream:
                        approval_voice_text += voice_content
                    
                    await play_response(approval_voice_text)
                    thread_state = graph.get_state(config=config)

            # Get voice input from user
            user_input = await get_voice_input()
            
            if not user_input:
                continue
                
            # Check for exit commands
            if any(word in user_input.lower() for word in ["exit", "quit", "goodbye", "bye"]):
                play_audio("Goodbye! It was great helping you today.")
                print("\n\nVoice command received. Exiting...\n\n")
                break
                
            graph_input = AgentState(
                messages=[
                    HumanMessage(content=user_input)
                ],
                yolo_mode=yolo_mode
            )

            print(f"\n\n ----- Human ----- \n\n{user_input}\n")

    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Exiting...\n\n")
    except Exception as e:
        error_message = f"Error: {type(e).__name__}: {str(e)}"
        print(error_message)
        play_audio("I encountered an error. Please check the console for details.")
        raise


if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()
    
    asyncio.run(main())