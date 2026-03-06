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
            "Predict the nucleophilic and electrophilic reaction sites of a molecule. "
            "Returns methyl anion affinity (MAA, electrophilicity) and methyl cation affinity "
            "(MCA, nucleophilicity) values in kJ/mol for each reactive atom. "
            "Higher MAA = more electrophilic. Higher MCA = more nucleophilic."
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
    """Predict nucleophilic and electrophilic sites for a molecule."""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return {"error": f"Invalid SMILES: {smiles}"}

    canonical = Chem.MolToSmiles(mol, isomericSmiles=True)
    name = hashlib.md5(canonical.encode()).hexdigest()

    df_elec, df_nuc, *_ = pred_MAA_and_MCA(canonical, name)

    electrophilic = [
        {
            "atom_id": row["Atom ID"],
            "type": row["Type"],
            "MAA_kJ_mol": round(row["MAA Value [kJ/mol]"], 1),
            "estimated_error_kJ_mol": round(row["Est. Error [kJ/mol]"], 1),
        }
        for _, row in df_elec.iterrows()
    ]

    nucleophilic = [
        {
            "atom_id": row["Atom ID"],
            "type": row["Type"],
            "MCA_kJ_mol": round(row["MCA Value [kJ/mol]"], 1),
            "estimated_error_kJ_mol": round(row["Est. Error [kJ/mol]"], 1),
        }
        for _, row in df_nuc.iterrows()
    ]

    return {
        "smiles": canonical,
        "electrophilic_sites": electrophilic,  # sorted descending by MAA
        "nucleophilic_sites": nucleophilic,     # sorted descending by MCA
    }


TOOL_REGISTRY = {
    "predict_reactivity": predict_reactivity,
}
