from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from app.database import run_query
from app.auth import get_user_from_session

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/grades", response_class=HTMLResponse)
def grades(request: Request):
    user = get_user_from_session(request)
    if not user:
        return RedirectResponse("/login", status_code=302)

    grade_rows = run_query(
        """
        SELECT g.*, a.title as assignment_title
        FROM grades g
        JOIN assignments a ON a.id = g.assignment_id
        WHERE g.student_id=%s
        ORDER BY g.id DESC
        """,
        (user["id"],),
        fetchall=True,
    )
    return templates.TemplateResponse("grades.html", {"request": request, "user": user, "grades": grade_rows})


@router.get("/grades/{grade_id}", response_class=HTMLResponse)
def grade_detail(request: Request, grade_id: int):
    user = get_user_from_session(request)
    if not user:
        return RedirectResponse("/login", status_code=302)

    grade = run_query(
        """
        SELECT g.*, a.title as assignment_title, u.full_name as student_name
        FROM grades g
        JOIN assignments a ON a.id=g.assignment_id
        JOIN users u ON u.id=g.student_id
        WHERE g.id=%s
        """,
        (grade_id,),
        fetchone=True,
    )

    # IDOR fix: check if the grade exists
    if not grade:
        raise HTTPException(status_code=404, detail="Grade not found")

    # IDOR fix: ensure the grade belongs to the logged-in student (or user is admin/teacher)
    if grade["student_id"] != user["id"] and user.get("role") not in ("admin", "teacher"):
        raise HTTPException(
            status_code=403,
            detail="You are not authorized to view this grade"
        )

    return templates.TemplateResponse("grade_detail.html", {"request": request, "user": user, "grade": grade})