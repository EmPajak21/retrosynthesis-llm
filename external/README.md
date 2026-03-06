# External Dependencies

This directory contains third-party tools included as git subtrees.

## ESNUEL_ML

Atom-based ML for predicting nucleophilicity (MCA) and electrophilicity (MAA) from SMILES.
Repository: https://github.com/EmPajak21/ESNUEL_ML

### Setup

**1. Download models**

```bash
cd external/ESNUEL_ML
curl -L -o models.tar.xz https://sid.erda.dk/share_redirect/Ear6g6wl0G
tar xf models.tar.xz && mv models src/esnuelML/ && rm models.tar.xz
```

**2. Install xtb (macOS)**

```bash
brew install grimme-lab/qc/xtb
mkdir -p external/ESNUEL_ML/dep
ln -s /opt/homebrew/Cellar/xtb/$(brew list --versions xtb | awk '{print $2}') external/ESNUEL_ML/dep/xtb-dist
```

**3. Install Python dependencies**

```bash
uv pip install -e "."
```

### Usage

```bash
cd external/ESNUEL_ML
python src/esnuelML/predictor.py --smi 'CC(=O)Oc1ccccc1C(=O)O'
```

### Pulling upstream updates

```bash
git subtree pull --prefix=external/ESNUEL_ML https://github.com/EmPajak21/ESNUEL_ML.git main --squash
```

---

## LocalMapper

Atom-to-atom reaction mapping via human-in-the-loop ML (Nature Communications, 2024).
Repository: https://github.com/EmPajak21/LocalMapper
License: CC BY-NC-SA 4.0 (non-commercial use only)

### Setup

```bash
uv pip install -e "."
uv pip install -e external/LocalMapper/
```

### Usage

```python
from localmapper import localmapper
mapper = localmapper()
rxn = 'CC(C)S.CN(C)C=O.Fc1cccnc1F.O=C([O-])[O-].[K+].[K+]>>CC(C)Sc1ncccc1F'
result = mapper.get_atom_map(rxn, return_dict=True)
# result: {'rxn': ..., 'mapped_rxn': ..., 'template': ..., 'confident': True}
```

### Pulling upstream updates

```bash
git subtree pull --prefix=external/LocalMapper https://github.com/EmPajak21/LocalMapper.git main --squash
```
