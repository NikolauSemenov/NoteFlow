from typing import Annotated

from fastapi import APIRouter, Depends, Path

from src.dependencies import get_notes, get_note_by_id
from src.types import NotesRow, NoteRow
from src.services.get_notes import GetAllNotes, GetNote

router = APIRouter()


@router.get("/notes", tags=["Notes"])
async def get_all_notes(service: Annotated[GetAllNotes, Depends(get_notes)]) -> list[NotesRow]:
    return await service()


@router.get("/note/{note_id}", tags=["Notes"])
async def get_note(
    service: Annotated[GetNote, Depends(get_note_by_id)], note_id: int = Path(..., ge=1, le=2147483647)
) -> NoteRow:
    return await service(note_id)
