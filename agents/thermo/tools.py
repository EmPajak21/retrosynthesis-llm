import sys
import hashlib
from pathlib import Path

# Add ESNUEL_ML to path
_ESNUEL_SRC = Path(__file__).parents[2] / "external" / "ESNUEL_ML" / "src" / "esnuelML"
if str(_ESNUEL_SRC) not in sys.path:
    sys.path.insert(0, str(_ESNUEL_SRC))

from rdkit import Chem
from predictor import pred_MAA_and_MCA


TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "predict_reactivity",
        "description": (
            "Predict nucleophilic and electrophilic reaction sites of a molecule. "
            "Returns MAA (electrophilicity) and MCA (nucleophilicity) values in kJ/mol "
            "for all reactive atoms, ranked by activity. The top 3 sites by rank are the "
            "most chemically significant. Higher MAA = more electrophilic. Higher MCA = more nucleophilic."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "smiles": {
                    "type": "string",
                    "description": "SMILES string of the molecule to analyse.",
                }
            },
            "required": ["smiles"],
        },
    },
}


def predict_reactivity(smiles: str) -> dict:
    """Predict nucleophilic and electrophilic sites for a molecule, ranked by activity."""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return {"error": f"Invalid SMILES: {smiles}"}

    canonical = Chem.MolToSmiles(mol, isomericSmiles=True)
    name = hashlib.md5(canonical.encode()).hexdigest()

    df_elec, df_nuc, *_ = pred_MAA_and_MCA(canonical, name)

    electrophilic = [
        {
            "rank": i + 1,
            "atom_id": row["Atom ID"],
            "type": row["Type"],
            "MAA_kJ_mol": round(row["MAA Value [kJ/mol]"], 1),
            "estimated_error_kJ_mol": round(row["Est. Error [kJ/mol]"], 1),
            "top_3": i < 3,
        }
        for i, (_, row) in enumerate(df_elec.iterrows())
    ]

    nucleophilic = [
        {
            "rank": i + 1,
            "atom_id": row["Atom ID"],
            "type": row["Type"],
            "MCA_kJ_mol": round(row["MCA Value [kJ/mol]"], 1),
            "estimated_error_kJ_mol": round(row["Est. Error [kJ/mol]"], 1),
            "top_3": i < 3,
        }
        for i, (_, row) in enumerate(df_nuc.iterrows())
    ]

    return {
        "smiles": canonical,
        "electrophilic_sites": electrophilic,  # sorted descending by MAA
        "nucleophilic_sites": nucleophilic,     # sorted descending by MCA
    }


TOOL_REGISTRY = {
    "predict_reactivity": predict_reactivity,
}
