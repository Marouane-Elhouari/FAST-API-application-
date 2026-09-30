import base64
import io
import math
from pathlib import Path
from typing import List

from fastapi import HTTPException
from rdkit import Chem
from rdkit.Chem import AllChem, Draw

VIZ_OUTPUT_DIR = Path(__file__).resolve().parent.parent / "generated" / "mol_viz"
VIZ_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

ATOM_COLORS = {
    "C": "grey", "N": "blue", "O": "red", "S": "gold",
    "Cl": "green", "F": "lightgreen", "Br": "darkred",
    "P": "orange", "H": "white",
}


def _mol_from_smiles_or_400(smiles: str) -> Chem.Mol:
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise HTTPException(status_code=400, detail=f"Invalid SMILES: {smiles}")
    return mol


def _json_safe(value):
    if isinstance(value, float) and math.isnan(value):
        return None
    if isinstance(value, (int, float, str, bool)) or value is None:
        return value
    return str(value)


def smiles_to_2d_png_base64(smiles: str, add_hydrogens: bool = False, size=(400, 400)) -> str:
    mol = _mol_from_smiles_or_400(smiles)
    if add_hydrogens:
        mol = Chem.AddHs(mol)

    img = Draw.MolToImage(mol, size=size)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def compute_descriptors(smiles_list: List[str], ignore_3d: bool = True) -> List[dict]:
    from mordred import Calculator, descriptors

    calc = Calculator(descriptors, ignore_3d=ignore_3d)
    results = []
    for smi in smiles_list:
        mol = Chem.MolFromSmiles(smi)
        if mol is None:
            results.append({"smiles": smi, "error": "invalid SMILES"})
            continue
        raw_row = calc(mol).asdict()
        row = {str(k): _json_safe(v) for k, v in raw_row.items()}
        row["smiles"] = smi
        results.append(row)
    return results


def generate_molecule_3d_html(smiles: str, marker_size: int = 10, add_hydrogens: bool = False) -> Path:
    import plotly.graph_objects as go

    mol = _mol_from_smiles_or_400(smiles)
    if add_hydrogens:
        mol = Chem.AddHs(mol)

    try:
        embed_status = AllChem.EmbedMolecule(mol, randomSeed=42)
        if embed_status != 0:
            embed_status = AllChem.EmbedMolecule(mol, useRandomCoords=True, randomSeed=42)
        if embed_status != 0:
            raise ValueError("embedding failed")
        AllChem.MMFFOptimizeMolecule(mol)
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Impossible de générer la géométrie 3D pour '{smiles}': {exc}",
        ) from exc

    conf = mol.GetConformer()
    coords = conf.GetPositions()
    symbols = [atom.GetSymbol() for atom in mol.GetAtoms()]

    fig = go.Figure()

    edge_x, edge_y, edge_z = [], [], []
    for bond in mol.GetBonds():
        i, j = bond.GetBeginAtomIdx(), bond.GetEndAtomIdx()
        p1, p2 = coords[i], coords[j]
        edge_x += [p1[0], p2[0], None]
        edge_y += [p1[1], p2[1], None]
        edge_z += [p1[2], p2[2], None]

    fig.add_trace(go.Scatter3d(
        x=edge_x, y=edge_y, z=edge_z, mode="lines",
        line=dict(color="rgba(80,80,80,0.6)", width=4),
        name="bonds", hoverinfo="none", showlegend=False,
    ))

    for element in sorted(set(symbols)):
        mask = [s == element for s in symbols]
        fig.add_trace(go.Scatter3d(
            x=coords[mask, 0], y=coords[mask, 1], z=coords[mask, 2],
            mode="markers+text",
            marker=dict(size=marker_size, color=ATOM_COLORS.get(element, "purple"), opacity=0.9),
            text=[element] * sum(mask), textposition="top center",
            name=element,
        ))

    fig.update_layout(
        title=f"Molecule 3D graph — {smiles}",
        height=750, legend_title_text="atom",
        scene=dict(xaxis_title="x (Å)", yaxis_title="y (Å)", zaxis_title="z (Å)"),
    )

    safe_name = "".join(c if c.isalnum() else "_" for c in smiles)[:60]
    filepath = VIZ_OUTPUT_DIR / f"mol3d_{safe_name}.html"
    fig.write_html(filepath, include_plotlyjs="cdn", full_html=True)
    return filepath
