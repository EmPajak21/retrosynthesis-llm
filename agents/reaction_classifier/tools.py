import sys
import re
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


# Atom symbol lookup from SMARTS token
_ATOM_NAMES = {
    "C": "carbon", "c": "aromatic carbon", "N": "nitrogen", "n": "aromatic nitrogen",
    "O": "oxygen", "o": "aromatic oxygen", "S": "sulfur", "s": "aromatic sulfur",
    "F": "fluorine", "Cl": "chlorine", "Br": "bromine", "I": "iodine",
    "P": "phosphorus", "B": "boron", "Si": "silicon",
}

def _atom_label(token: str) -> str:
    """Convert a SMARTS atom token like [S:1] or c to a readable label."""
    # Strip brackets and mapping: [S:1] -> S
    inner = re.sub(r"[\[\]:0-9]", "", token)
    return _ATOM_NAMES.get(inner, inner or "atom")

def _parse_template(template: str) -> tuple[list[str], list[str]]:
    """
    Parse a reaction SMARTS template into plain-language bond lists.
    Returns (bonds_broken, bonds_formed).
    """
    if ">>" not in template:
        return [], []

    reactant_smarts, product_smarts = template.split(">>")

    def extract_bonds(smarts: str) -> list[str]:
        bonds = []
        # Match explicit bonds: atom-atom, atom=atom, atom#atom
        for match in re.finditer(
            r"(\[?[A-Za-z]+(?::[0-9]+)?\]?)([=#\-]|(?<![>]))(\[?[A-Za-z]+(?::[0-9]+)?\]?)",
            smarts,
        ):
            a1, bond_char, a2 = match.group(1), match.group(2), match.group(3)
            bond_type = {"=": "double bond", "#": "triple bond", "-": "single bond"}.get(
                bond_char, "single bond"
            )
            bonds.append(f"{_atom_label(a1)}-{_atom_label(a2)} ({bond_type})")
        return bonds

    # Bonds that exist in reactants but not products are broken
    reactant_bonds = extract_bonds(reactant_smarts)
    product_bonds = extract_bonds(product_smarts)

    bonds_broken = [b for b in reactant_bonds if b not in product_bonds]
    bonds_formed = [b for b in product_bonds if b not in reactant_bonds]

    return bonds_broken, bonds_formed


TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "map_reaction",
        "description": (
            "Given a reaction SMILES (reactants>>products), uses LocalMapper to produce "
            "an atom-mapped reaction and extract the reaction template in SMARTS format. "
            "Also returns plain-language descriptions of bonds broken and formed at the "
            "reaction centre to aid classification. "
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
    """Map a reaction and extract its reaction centre with bond-level annotations."""
    try:
        mapper = _get_mapper()
        result = mapper.get_atom_map(rxn_smiles, return_dict=True)
        template = result["template"]
        bonds_broken, bonds_formed = _parse_template(template)
        return {
            "template": template,
            "bonds_broken": bonds_broken,
            "bonds_formed": bonds_formed,
            "mapped_rxn": result["mapped_rxn"],
            "confident": result["confident"],
        }
    except Exception as e:
        return {"error": str(e), "rxn_smiles": rxn_smiles}


TOOL_REGISTRY = {
    "map_reaction": map_reaction,
}
