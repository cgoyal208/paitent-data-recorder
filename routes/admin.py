from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required
from sqlalchemy.exc import SQLAlchemyError

from extensions import db
from models.clinical import ClinicalSession
from models.patient import Patient
from models.privacy import AuditLog, RedFlagAlert
from models.records import MedicalDocument
from models.settings import SystemSetting
from models.user import User
from utils.helpers import get_patient_id_policy, roles_required, write_audit

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/")
@login_required
@roles_required("admin")
def home():
    stats = {
        "users": User.query.count(),
        "patients": Patient.query.count(),
        "sessions": ClinicalSession.query.count(),
        "documents": MedicalDocument.query.count(),
        "open_alerts": RedFlagAlert.query.filter_by(acknowledged=False).count(),
    }
    users = User.query.order_by(User.created_at.desc()).limit(50).all()
    logs = AuditLog.query.order_by(AuditLog.created_at.desc()).limit(40).all()
    patient_id_policy = get_patient_id_policy()
    return render_template("admin/home.html", stats=stats, users=users, logs=logs, patient_id_policy=patient_id_policy)


@admin_bp.route("/patient-id-policy", methods=["POST"])
@login_required
@roles_required("admin")
def update_patient_id_policy():
    policy = (request.form.get("patient_id_policy") or "retain").strip()
    valid = {"retain", "allow_reuse"}
    if policy not in valid:
        policy = "retain"

    setting = SystemSetting.query.filter_by(key="patient_id_policy").first()
    if not setting:
        setting = SystemSetting(key="patient_id_policy", value=policy)
        db.session.add(setting)
    else:
        setting.value = policy
    write_audit("update_patient_id_policy", "system_setting", setting.id, details=policy)
    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        flash("Could not update patient ID policy.", "danger")
        return redirect(url_for("admin.home"))

    flash("Patient ID policy updated.", "success")
    return redirect(url_for("admin.home"))


@admin_bp.route("/users/<int:user_id>/toggle", methods=["POST"])
@login_required
@roles_required("admin")
def toggle_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.role == "admin":
        flash("The primary admin account cannot be disabled from here.", "warning")
        return redirect(url_for("admin.home"))
    user.is_active_account = not user.is_active_account
    write_audit("toggle_user", "user", user.id, details=str(user.is_active_account))
    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        flash("Could not update user.", "danger")
    return redirect(url_for("admin.home"))
