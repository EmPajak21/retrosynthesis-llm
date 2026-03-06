"""
Thermo Agent — reasons about molecular reaction sites using ESNUEL_ML.

Requires Ollama running locally:
    ollama serve
    ollama pull qwen2.5:1.5b
"""
import json
import argparse
from openai import OpenAI

from tools import TOOL_SCHEMA, TOOL_REGISTRY

MODEL = "qwen2.5:1.5b"
OLLAMA_BASE_URL = "http://localhost:11434/v1"

SYSTEM_PROMPT = """You are an expert computational chemist specialising in molecular reactivity.
You have access to a tool that predicts nucleophilic and electrophilic reaction sites using \
quantum-chemistry-based ML models (xTB/GFN1 + LightGBM).

When given a molecule:
1. Call predict_reactivity with its SMILES to get MAA (electrophilicity) and MCA (nucleophilicity) values.
2. Identify the most reactive sites and explain what chemistry they are likely to undergo.
3. Highlight any sites where both electrophilicity and nucleophilicity are notable (ambident reactivity).
4. Comment on estimated errors — if error > 25 kJ/mol, flag that QM calculations are recommended.

Be concise but chemically precise."""


def run_agent(smiles: str, model: str = MODEL, verbose: bool = True):
    client = OpenAI(base_url=OLLAMA_BASE_URL, api_key="ollama")

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Analyse the reaction sites of this molecule: {smiles}"},
    ]

    if verbose:
        print(f"\n{'='*60}")
        print(f"Molecule: {smiles}")
        print(f"{'='*60}\n")

    # --- Agentic loop ---
    while True:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=[TOOL_SCHEMA],
            tool_choice="auto",
        )
        msg = response.choices[0].message
        messages.append(msg)

        # No tool call — model has produced its final answer
        if not msg.tool_calls:
            if verbose:
                print(f"[Agent]\n{msg.content}\n")
            return msg.content

        # Execute each tool call
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
    parser = argparse.ArgumentParser(description="Thermo agent — reaction site analysis")
    parser.add_argument("--smi", default="CC(=O)Oc1ccccc1C(=O)O", help="SMILES to analyse")
    parser.add_argument("--model", default=MODEL, help="Ollama model name")
    args = parser.parse_args()

    run_agent(args.smi, model=args.model)
