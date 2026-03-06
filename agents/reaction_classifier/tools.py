import sys
from pathlib import Path

_LOCALMAPPER_SRC = Path(__file__).parents[2] / "external" / "LocalMapper"
if str(_LOCALMAPPER_SRC) not in sys.path:
    sys.path.insert(0, str(_LOCALMAPPER_SRC))

from localmapper import localmapper as LocalMapper

_mapper = None

def _get_mapper():
    global _mapper
    if _mapper is None:
        _mapper = LocalMapper()
    return _mapper


TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "map_reaction",
        "description": (
            "Given a reaction SMILES (reactants>>products), uses LocalMapper to produce "
            "an atom-mapped reaction and extract the reaction template in SMARTS format. "
            "The template captures the minimal reaction centre — use it to classify the "
            "reaction type rather than the full (potentially long) reaction SMILES. "
            "IMPORTANT: pass the reaction SMILES exactly as provided by the user."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "rxn_smiles": {
                    "type": "string",
                    "description": "Reaction SMILES in the format reactants>>products. Must be passed exactly as given.",
                }
            },
            "required": ["rxn_smiles"],
        },
    },
}


def map_reaction(rxn_smiles: str) -> dict:
    """Map a reaction and extract its reaction centre template."""
    try:
        mapper = _get_mapper()
        result = mapper.get_atom_map(rxn_smiles, return_dict=True)
        return {
            "mapped_rxn": result["mapped_rxn"],
            "template": result["template"],
            "confident": result["confident"],
        }
    except Exception as e:
        return {"error": str(e), "rxn_smiles": rxn_smiles}


TOOL_REGISTRY = {
    "map_reaction": map_reaction,
}
