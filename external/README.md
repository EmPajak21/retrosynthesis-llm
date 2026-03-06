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
