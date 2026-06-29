"""
Onboarding CRUD Operations
"""
from datetime import date, timedelta
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from . import models, schemas


def get_templates(
    db: Session,
    is_active: Optional[bool] = None
) -> list[models.OnboardingTemplate]:
    """Holt alle Templates"""
    query = db.query(models.OnboardingTemplate)
    if is_active is not None:
        query = query.filter(models.OnboardingTemplate.is_active == is_active)
    return query.order_by(models.OnboardingTemplate.name).all()


def create_template(db: Session, data: schemas.TemplateCreate) -> models.OnboardingTemplate:
    """Erstellt ein Onboarding-Template mit Aufgaben"""
    tasks_data = data.tasks
    template_data = data.model_dump(exclude={"tasks"})
    template = models.OnboardingTemplate(**template_data)
    db.add(template)
    db.flush()  # ID erzeugen ohne Commit

    for task_data in tasks_data:
        task = models.OnboardingTemplateTask(
            template_id=template.id,
            **task_data.model_dump()
        )
        db.add(task)

    db.commit()
    db.refresh(template)
    return template


def start_onboarding(
    db: Session,
    employee_id: UUID,
    template_id: UUID,
    start_date: date
) -> models.OnboardingProcess:
    """Startet Onboarding-Prozess für Mitarbeiter basierend auf Template"""
    process = models.OnboardingProcess(
        employee_id=employee_id,
        template_id=template_id,
        start_date=start_date,
        status="pending"
    )
    db.add(process)
    db.flush()

    # Aufgaben aus Template kopieren
    template = db.query(models.OnboardingTemplate).filter(
        models.OnboardingTemplate.id == template_id
    ).first()

    if template:
        for tmpl_task in template.tasks:
            due_date = start_date + timedelta(days=tmpl_task.due_days_offset) if tmpl_task.due_days_offset else None
            task = models.OnboardingProcessTask(
                process_id=process.id,
                title=tmpl_task.title,
                description=tmpl_task.description,
                responsible_role=tmpl_task.responsible_role,
                due_date=due_date,
                order_index=tmpl_task.order_index,
                status="pending"
            )
            db.add(task)

    db.commit()
    db.refresh(process)
    return process


def get_process(db: Session, process_id: UUID) -> Optional[models.OnboardingProcess]:
    """Holt einen spezifischen Prozess"""
    return db.query(models.OnboardingProcess).filter(
        models.OnboardingProcess.id == process_id
    ).first()


def get_employee_onboarding(
    db: Session,
    employee_id: UUID
) -> list[models.OnboardingProcess]:
    """Holt alle Onboarding-Prozesse eines Mitarbeiters"""
    return db.query(models.OnboardingProcess).filter(
        models.OnboardingProcess.employee_id == employee_id
    ).order_by(models.OnboardingProcess.start_date.desc()).all()


def update_task_status(
    db: Session,
    task_id: UUID,
    status: str,
    notes: Optional[str] = None
) -> Optional[models.OnboardingProcessTask]:
    """Aktualisiert Status einer Prozessaufgabe"""
    task = db.query(models.OnboardingProcessTask).filter(
        models.OnboardingProcessTask.id == task_id
    ).first()
    if not task:
        return None
    task.status = status
    if notes is not None:
        task.notes = notes
    if status == "completed" and not task.completed_at:
        task.completed_at = date.today()
    db.commit()
    db.refresh(task)
    return task
