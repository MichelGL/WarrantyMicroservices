import pytest
from defect_service.app.defect import add_defect, get_defect, update_defect_status
from defect_service.app.defect_schemas import DefectStatus, SDefectAdd, SDefect

# Последовательность тестов обязательна
@pytest.mark.asyncio
async def test_add_defect():
    name = "Трещина на стене"
    new_defect = SDefectAdd(name=name,
                       status=DefectStatus.new,
                       repair_deadline=4,
                       contractor="Строительная компания А")
    added_user = await add_defect(defect=new_defect)
    assert added_user.name is name


@pytest.mark.asyncio
async def test_get_defect():
    defect = await get_defect(defect_id=1)
    assert defect is not None


@pytest.mark.asyncio
async def test_update_defect_status():
    edit_status = DefectStatus.in_progress
    edited_defect = await update_defect_status(defect_id=1,
                                     new_status=edit_status)
    assert edited_defect.status is edit_status