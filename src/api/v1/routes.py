from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query
from pydantic import Field
from starlette import status

from src.services.mutation_notes import TakeDownActiveNote, CreateNote
from src.dependencies import get_notes, get_note_by_id, update_note_active, create_note
from src.schemas import NotesRow, NoteRow, NoteIdRow, CreateNoteBody
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


@router.put("/note/active", tags=["Notes"], response_model=NoteIdRow)
async def update_note(
    note_id: Annotated[Annotated[int, Field(gt=0, le=2_147_483_647)], Query(..., alias="id")],
    service: Annotated[TakeDownActiveNote, Depends(update_note_active)],
) -> NoteIdRow | None:
    return await service(note_id)


@router.post("/note", tags=["Notes"], status_code=status.HTTP_201_CREATED)
async def create_note_data(
    body: CreateNoteBody,
    service: Annotated[CreateNote, Depends(create_note)],
) -> NoteIdRow | None:
    return await service(body)
