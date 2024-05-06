from fastapi import APIRouter, Depends

from app.dependencies import get_token_header

router = APIRouter(
    prefix='/api/v1/keys',
    tags=['keys'],
    dependencies=[Depends(get_token_header)],
    responses={404: {'message': 'Not found'}}
)


@router.get('/{slave_sae_id}/status')
async def status(slave_sae_id: str):
    return {'slave_sae_id': slave_sae_id}
