from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse

from ..auth import require_api_key
from ..chem_utils import (
    VIZ_OUTPUT_DIR,
    compute_descriptors,
    generate_molecule_3d_html,
    smiles_to_2d_png_base64,
)
from ..schemas import (
    Mol2DResponse,
    Molecule3DResponse,
    PropertiesResponse,
    SmilesListRequest,
    SmilesRequest,
)

router = APIRouter(prefix="/api", tags=["chemistry"])


@router.post("/mol-2d", response_model=Mol2DResponse, dependencies=[Depends(require_api_key)])
def convert_mol_to_2d(payload: SmilesRequest):
    image_b64 = smiles_to_2d_png_base64(payload.smiles)
    return Mol2DResponse(smiles=payload.smiles, image_base64=image_b64)


@router.post("/properties", response_model=PropertiesResponse, dependencies=[Depends(require_api_key)])
def get_all_properties(payload: SmilesListRequest):
    props = compute_descriptors(payload.smiles_list)
    return PropertiesResponse(count=len(props), properties=props)


@router.post("/mol-3d", response_model=Molecule3DResponse, dependencies=[Depends(require_api_key)])
def get_molecule_3d(payload: SmilesRequest):
    filepath = generate_molecule_3d_html(payload.smiles)
    return Molecule3DResponse(smiles=payload.smiles, html_url=f"/api/mol-3d-file/{filepath.name}")


@router.get("/mol-3d-file/{filename}", dependencies=[Depends(require_api_key)])
def get_molecule_3d_file(filename: str):
    filepath = VIZ_OUTPUT_DIR / filename
    return FileResponse(filepath, media_type="text/html")
