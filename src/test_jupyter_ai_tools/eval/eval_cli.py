import argparse
import os
from test_jupyter_ai_tools.eval.eval_suite import run_eval_suite
from test_jupyter_ai_tools.eval.load_agent import make_default_agent


def main():
    parser = argparse.ArgumentParser(description="Run agent evaluation suite on tool usage")
    parser.add_argument("--openai_key", type=str, help="OpenAI API key")
    parser.add_argument("--model", type=str, default="gpt-4-turbo", help="OpenAI model to use")
    parser.add_argument("--custom_agent", type=str, help="Optional path to Python file that defines a get_agent() function")
    args = parser.parse_args()

    agent = None

    if args.custom_agent:
        print("📥 Loading custom agent from:", args.custom_agent)
        import importlib.util
        spec = importlib.util.spec_from_file_location("custom_agent_module", args.custom_agent)
        custom_agent_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(custom_agent_module)
        agent = custom_agent_module.get_agent()
    else:
        print("🔑 Using OpenAI LLM to build agent with tools...")
        os.environ["OPENAI_API_KEY"] = args.openai_key
        agent = make_default_agent(openai_key=args.openai_key, model=args.model)

    print("🚀 Running evaluation suite...")
    run_eval_suite(agent)


if __name__ == "__main__":
    main()
