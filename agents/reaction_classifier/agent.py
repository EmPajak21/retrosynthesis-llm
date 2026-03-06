"""
Reaction Classifier Agent — classifies organic reactions using LocalMapper.

Given a reaction SMILES, calls LocalMapper to extract the reaction template
(SMARTS), then asks the LLM to classify the reaction type.

Requires Ollama running locally:
    ollama serve
    ollama pull qwen2.5:7b
"""
import json
import argparse
from openai import OpenAI

from tools import TOOL_SCHEMA, TOOL_REGISTRY

MODEL = "qwen2.5:7b"  # 1.5b hallucinates SMILES strings; 7b+ recommended
OLLAMA_BASE_URL = "http://localhost:11434/v1"

SYSTEM_PROMPT = """You are an expert organic chemist specialising in reaction classification.

You have access to a tool that atom-maps a reaction and returns its reaction template in SMARTS format.
The template captures the minimal reaction centre — the bonds broken and formed.

When given a reaction:
1. Call map_reaction to obtain the reaction template.
2. Interpret the template SMARTS to identify what bonds are broken and formed.
3. Classify the reaction into a specific type (e.g. SNAr, SN2, Grignard addition,
   ester hydrolysis, Suzuki coupling, aldol condensation, etc.).
4. Briefly justify your classification based on the template.
5. If the mapping is marked not confident, note that the classification may be unreliable.

Be concise and precise. Lead with the reaction class."""


def run_agent(rxn_smiles: str, model: str = MODEL, verbose: bool = True):
    client = OpenAI(base_url=OLLAMA_BASE_URL, api_key="ollama")

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Classify this reaction: {rxn_smiles}"},
    ]

    if verbose:
        print(f"\n{'='*60}")
        print(f"Reaction: {rxn_smiles}")
        print(f"{'='*60}\n")

    while True:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=[TOOL_SCHEMA],
            tool_choice="auto",
        )
        msg = response.choices[0].message
        messages.append(msg)

        if not msg.tool_calls:
            if verbose:
                print(f"[Agent]\n{msg.content}\n")
            return msg.content

        for tc in msg.tool_calls:
            fn_name = tc.function.name
            fn_args = json.loads(tc.function.arguments)

            if verbose:
                print(f"[Tool call] {fn_name}({fn_args})")

            tool_fn = TOOL_REGISTRY.get(fn_name)
            result = tool_fn(**fn_args) if tool_fn else {"error": f"Unknown tool: {fn_name}"}

            if verbose:
                print(f"[Tool result] {json.dumps(result, indent=2)}\n")

            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": json.dumps(result),
            })


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reaction classifier agent")
    parser.add_argument(
        "--rxn",
        default="CC(C)S.CN(C)C=O.Fc1cccnc1F.O=C([O-])[O-].[K+].[K+]>>CC(C)Sc1ncccc1F",
        help="Reaction SMILES to classify",
    )
    parser.add_argument("--model", default=MODEL, help="Ollama model name")
    args = parser.parse_args()

    run_agent(args.rxn, model=args.model)
