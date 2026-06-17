"""
General Agent — Financial Demo Script
Run directly without LLM for tool testing, or with LLM for full agent flow.
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


async def demo_tools_direct():
    """Demo 1: Call tools directly (no LLM needed)"""
    from tools.calc_tool import CalcTool
    from tools.financial_tool import FinancialTool

    print("=" * 60)
    print("Demo 1: Direct Tool Calls (no LLM needed)")
    print("=" * 60)

    # Calculator
    calc = CalcTool()
    result = await calc(expression="2**50")
    print(f"\n[Calculator] 2^50 = {result.output}")
    print(f"  Success: {result.success}, Time: {result.elapsed_ms}ms")

    # Financial Report
    fin = FinancialTool()
    print("\n[Financial] Fetching 600519 (Moutai) income statement...")
    result = await fin(symbol="600519", report_type="income")
    print(f"  Success: {result.success}")
    if result.success:
        lines = result.output.split("\n")[:5]
        for line in lines:
            print(f"  {line}")
    else:
        print(f"  Error: {result.error}")


async def demo_agent_flow():
    """Demo 2: Full agent flow (needs LLM API key)"""
    from agent.engine import AgentEngine
    from tools.registry import ToolRegistry

    print("\n" + "=" * 60)
    print("Demo 2: Full Agent Flow (needs OPENAI_API_KEY)")
    print("=" * 60)

    ToolRegistry.discover()
    print(f"Registered tools: {ToolRegistry.list_tools()}")

    events = []

    async def on_event(event):
        events.append(event)
        icon = "▶" if event["type"] == "step_start" else "✓"
        detail = f" — {event['detail']}" if event.get("detail") else ""
        print(f"  {icon} {event['step']}{detail}")

    engine = AgentEngine(on_event=on_event)
    query = "茅台2024年Q3财报分析"
    print(f"\nQuery: {query}")
    print("-" * 40)

    result = await engine.run(query)

    print("-" * 40)
    print(f"Domain: {result.domain} | Complexity: {result.complexity}")
    print(f"Time: {result.elapsed_ms}ms | Steps: {len(result.steps)}")
    print(f"\nAnswer:\n{result.answer[:500]}")


async def main():
    print("General Agent — Financial Demo\n")

    # Always run direct tool demo
    await demo_tools_direct()

    # Try full agent flow
    try:
        from config import settings
        if settings.openai_api_key and settings.openai_api_key != "sk-xxx":
            await demo_agent_flow()
        else:
            print("\n[Skipping Demo 2] Set OPENAI_API_KEY in .env to run full agent flow.")
    except Exception as e:
        print(f"\n[Demo 2 Error] {e}")


if __name__ == "__main__":
    asyncio.run(main())
