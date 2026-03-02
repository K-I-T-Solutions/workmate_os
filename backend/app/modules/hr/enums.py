"""
HR Module Enums
Zentrale Definition aller Status-Enums und Typen für das HR-Modul.
"""
from enum import Enum


# ============================================================================
# RECRUITING ENUMS
# ============================================================================

class JobPostingStatus(str, Enum):
    """Status einer Stellenausschreibung"""
    DRAFT = "draft"
    PUBLISHED = "published"
    CLOSED = "closed"
    ARCHIVED = "archived"


class ApplicationStatus(str, Enum):
    """Status einer Bewerbung im Recruiting-Pipeline"""
    RECEIVED = "received"
    SCREENING = "screening"
    INTERVIEW = "interview"
    ASSESSMENT = "assessment"
    OFFER = "offer"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


class EmploymentType(str, Enum):
    """Beschäftigungsart"""
    FULLTIME = "fulltime"
    PARTTIME = "parttime"
    CONTRACT = "contract"
    INTERN = "intern"
    FREELANCE = "freelance"


# ============================================================================
# ONBOARDING ENUMS
# ============================================================================

class OnboardingStatus(str, Enum):
    """Status eines Onboarding-Prozesses"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    OVERDUE = "overdue"


class ChecklistItemStatus(str, Enum):
    """Status eines Checklist-Items"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"


# ============================================================================
# LEAVE MANAGEMENT ENUMS
# ============================================================================

class LeaveType(str, Enum):
    """Typ der Abwesenheit"""
    VACATION = "vacation"
    SICK = "sick"
    UNPAID = "unpaid"
    PARENTAL = "parental"
    BEREAVEMENT = "bereavement"
    TRAINING = "training"
    REMOTE = "remote"
    OTHER = "other"


class LeaveStatus(str, Enum):
    """Status eines Urlaubsantrags"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


# ============================================================================
# TRAINING ENUMS
# ============================================================================

class TrainingStatus(str, Enum):
    """Status einer Schulungsteilnahme"""
    PLANNED = "planned"
    ONGOING = "ongoing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class CertificationStatus(str, Enum):
    """Status eines Zertifikats"""
    ACTIVE = "active"
    EXPIRED = "expired"
    EXPIRING_SOON = "expiring_soon"


class SkillLevel(str, Enum):
    """Skill-Level / Kompetenzstufe"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


# ============================================================================
# COMPENSATION ENUMS
# ============================================================================

class CompensationType(str, Enum):
    """Art der Vergütung"""
    BASE_SALARY = "base_salary"
    BONUS = "bonus"
    COMMISSION = "commission"
    ALLOWANCE = "allowance"
    STOCK_OPTIONS = "stock_options"


class BenefitType(str, Enum):
    """Art des Benefits"""
    HEALTH_INSURANCE = "health_insurance"
    DENTAL = "dental"
    VISION = "vision"
    RETIREMENT = "retirement"
    GYM = "gym"
    MEAL_VOUCHER = "meal_voucher"
    TRANSPORT = "transport"
    PHONE = "phone"
    HOME_OFFICE = "home_office"
    OTHER = "other"


# ============================================================================
# HR DOCUMENTS ENUMS
# ============================================================================

class HRDocumentType(str, Enum):
    """Typ eines HR-Dokuments"""
    CONTRACT = "contract"
    AMENDMENT = "amendment"
    TERMINATION = "termination"
    CERTIFICATE = "certificate"
    REFERENCE = "reference"
    WARNING = "warning"
    EVALUATION = "evaluation"
    PROOF_OF_EMPLOYMENT = "proof_of_employment"
    TAX_DOCUMENT = "tax_document"
    OTHER = "other"
