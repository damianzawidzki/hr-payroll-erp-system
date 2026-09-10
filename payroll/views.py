"""
Payroll views for HRHub Pro.
"""

from decimal import Decimal
from io import BytesIO

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from attendance.models import Attendance
from employees.models import Employee

from .forms import GenerateWeeklyPayslipsForm, PayslipForm
from .models import Payslip


def get_user_role(user):
    """
    Return the role assigned to the logged-in user.
    """

    profile = getattr(user, "profile", None)

    if profile:
        return profile.role

    return None


def get_logged_employee(user):
    """
    Return employee record linked with the logged-in user.
    """

    return Employee.objects.filter(user=user).first()


def user_can_manage_payroll(user):
    """
    Allow only Admin and HR users to manage payroll.
    """

    if user.is_superuser:
        return True

    role = get_user_role(user)

    return role in ["ADMIN", "HR"]


def user_can_view_payslip(user, payslip):
    """
    Allow Admin and HR to view all payslips.
    Managers and employees can view only their own payslips.
    """

    if user_can_manage_payroll(user):
        return True

    employee = get_logged_employee(user)

    if employee and payslip.employee_id == employee.id:
        return True

    return False


def get_payroll_employee_queryset(user):
    """
    Return employees available for payroll processing.
    """

    role = get_user_role(user)

    if user.is_superuser or role in ["ADMIN", "HR"]:
        return Employee.objects.select_related(
            "department",
            "manager",
            "user",
            "user__profile",
        ).order_by(
            "first_name",
            "last_name",
        )

    return Employee.objects.none()


def money(value):
    """
    Format money values for the payslip.
    """

    amount = Decimal(value or 0).quantize(Decimal("0.01"))
    return f"GBP {amount}"


def make_employee_number(employee):
    """
    Return a payroll personnel number.
    """

    return f"10{employee.id:04d}"


def make_national_insurance_number(employee):
    """
    Return a realistic placeholder NI number for the employee.
    """

    number = employee.id + 100000
    return f"SN{number:06d}A"


def make_pay_period_number(payslip):
    """
    Return a weekly pay period number.
    """

    return f"{payslip.week_start.year}{payslip.week_start.isocalendar().week:02d}"


@login_required
def payslip_list(request):
    """
    Display weekly payslips for Admin and HR users.
    """

    if not user_can_manage_payroll(request.user):
        messages.error(request, "You do not have permission to access payroll.")
        return redirect("role_redirect")

    search_query = request.GET.get("search", "")
    status_filter = request.GET.get("status", "")

    payslips = Payslip.objects.select_related(
        "employee",
        "employee__department",
    ).all()

    if search_query:
        payslips = payslips.filter(
            Q(employee__first_name__icontains=search_query)
            | Q(employee__last_name__icontains=search_query)
            | Q(employee__employee_number__icontains=search_query)
        )

    if status_filter:
        payslips = payslips.filter(status=status_filter)

    total_gross = payslips.aggregate(total=Sum("gross_pay"))["total"] or 0
    total_deductions = payslips.aggregate(total=Sum("total_deductions"))["total"] or 0
    total_net = payslips.aggregate(total=Sum("net_pay"))["total"] or 0

    context = {
        "payslips": payslips.order_by("-week_start"),
        "search_query": search_query,
        "status_filter": status_filter,
        "total_gross": total_gross,
        "total_deductions": total_deductions,
        "total_net": total_net,
    }

    return render(request, "payroll/payslip_list.html", context)


@login_required
def payslip_create(request):
    """
    Create a weekly payslip manually.
    """

    if not user_can_manage_payroll(request.user):
        messages.error(request, "You do not have permission to create payslips.")
        return redirect("role_redirect")

    employee_queryset = get_payroll_employee_queryset(request.user)

    if request.method == "POST":
        form = PayslipForm(request.POST)
        form.fields["employee"].queryset = employee_queryset

        if form.is_valid():
            form.save()
            messages.success(request, "Payslip created.")
            return redirect("payslip_list")
    else:
        form = PayslipForm()
        form.fields["employee"].queryset = employee_queryset

    context = {
        "form": form,
        "page_title": "Add Weekly Payslip",
        "button_text": "Create Payslip",
    }

    return render(request, "payroll/payslip_form.html", context)


@login_required
def generate_weekly_payslips(request):
    """
    Generate weekly payslips from attendance records.
    """

    if not user_can_manage_payroll(request.user):
        messages.error(request, "You do not have permission to generate payslips.")
        return redirect("role_redirect")

    employee_queryset = get_payroll_employee_queryset(request.user)

    if request.method == "POST":
        form = GenerateWeeklyPayslipsForm(
            request.POST,
            employee_queryset=employee_queryset,
        )

        if form.is_valid():
            employees = form.cleaned_data["employees"]
            week_start = form.cleaned_data["week_start"]
            week_end = form.cleaned_data["week_end"]
            payment_date = form.cleaned_data["payment_date"]
            hourly_rate = form.cleaned_data["hourly_rate"]
            standard_weekly_hours = form.cleaned_data["standard_weekly_hours"]
            overtime_rate = form.cleaned_data["overtime_rate"]
            bonus = form.cleaned_data["bonus"]
            other_deductions = form.cleaned_data["other_deductions"]
            status = form.cleaned_data["status"]
            overwrite_existing = form.cleaned_data["overwrite_existing"]
            notes = form.cleaned_data["notes"]

            created_count = 0
            updated_count = 0
            skipped_count = 0
            no_attendance_count = 0

            for employee in employees:
                total_hours = Attendance.objects.filter(
                    employee=employee,
                    date__gte=week_start,
                    date__lte=week_end,
                    status__in=["PRESENT", "LATE"],
                ).aggregate(
                    total=Sum("total_hours"),
                )["total"] or Decimal("0.00")

                if total_hours <= Decimal("0.00"):
                    no_attendance_count += 1
                    continue

                standard_hours = min(total_hours, standard_weekly_hours)
                overtime_hours = max(
                    total_hours - standard_weekly_hours,
                    Decimal("0.00"),
                )

                defaults = {
                    "payment_date": payment_date,
                    "hourly_rate": hourly_rate,
                    "hours_worked": standard_hours,
                    "overtime_hours": overtime_hours,
                    "overtime_rate": overtime_rate,
                    "bonus": bonus,
                    "other_deductions": other_deductions,
                    "status": status,
                    "notes": notes,
                }

                existing_payslip = Payslip.objects.filter(
                    employee=employee,
                    week_start=week_start,
                    week_end=week_end,
                ).first()

                if existing_payslip and not overwrite_existing:
                    skipped_count += 1
                    continue

                if existing_payslip and overwrite_existing:
                    for field_name, field_value in defaults.items():
                        setattr(existing_payslip, field_name, field_value)

                    existing_payslip.save()
                    updated_count += 1
                    continue

                Payslip.objects.create(
                    employee=employee,
                    week_start=week_start,
                    week_end=week_end,
                    **defaults,
                )

                created_count += 1

            messages.success(
                request,
                (
                    "Weekly payslips generated. "
                    f"Created: {created_count}, "
                    f"updated: {updated_count}, "
                    f"skipped: {skipped_count}, "
                    f"without attendance: {no_attendance_count}."
                ),
            )

            return redirect("payslip_list")
    else:
        form = GenerateWeeklyPayslipsForm(employee_queryset=employee_queryset)

    context = {
        "form": form,
        "page_title": "Generate Weekly Payslips",
        "button_text": "Generate Payslips",
    }

    return render(request, "payroll/generate_weekly_payslips.html", context)


@login_required
def payslip_update(request, pk):
    """
    Update a weekly payslip.
    """

    if not user_can_manage_payroll(request.user):
        messages.error(request, "You do not have permission to update payslips.")
        return redirect("role_redirect")

    employee_queryset = get_payroll_employee_queryset(request.user)

    payslip = get_object_or_404(
        Payslip,
        pk=pk,
        employee__in=employee_queryset,
    )

    if request.method == "POST":
        form = PayslipForm(request.POST, instance=payslip)
        form.fields["employee"].queryset = employee_queryset

        if form.is_valid():
            form.save()
            messages.success(request, "Payslip updated.")
            return redirect("payslip_list")
    else:
        form = PayslipForm(instance=payslip)
        form.fields["employee"].queryset = employee_queryset

    context = {
        "form": form,
        "payslip": payslip,
        "page_title": "Edit Weekly Payslip",
        "button_text": "Save Changes",
    }

    return render(request, "payroll/payslip_form.html", context)


@login_required
def payslip_delete(request, pk):
    """
    Delete a weekly payslip.
    """

    if not user_can_manage_payroll(request.user):
        messages.error(request, "You do not have permission to delete payslips.")
        return redirect("role_redirect")

    employee_queryset = get_payroll_employee_queryset(request.user)

    payslip = get_object_or_404(
        Payslip,
        pk=pk,
        employee__in=employee_queryset,
    )

    if request.method == "POST":
        payslip.delete()
        messages.success(request, "Payslip deleted.")
        return redirect("payslip_list")

    context = {
        "payslip": payslip,
    }

    return render(request, "payroll/payslip_confirm_delete.html", context)


def build_payslip_pdf_response(request, pk, download=False):
    """
    Build a professional payslip PDF response.
    """

    payslip = get_object_or_404(
        Payslip.objects.select_related(
            "employee",
            "employee__department",
        ),
        pk=pk,
    )

    if not user_can_view_payslip(request.user, payslip):
        messages.error(request, "You do not have permission to view this payslip.")
        return redirect("role_redirect")

    employee = payslip.employee

    buffer = BytesIO()

    file_name = (
        f"payslip_{employee.employee_number}_"
        f"{payslip.week_start}_{payslip.week_end}.pdf"
    )

    response = HttpResponse(content_type="application/pdf")

    if download:
        response["Content-Disposition"] = f'attachment; filename="{file_name}"'
    else:
        response["Content-Disposition"] = f'inline; filename="{file_name}"'

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=35,
        leftMargin=35,
        topMargin=35,
        bottomMargin=35,
    )

    title_style = ParagraphStyle(
        "PayslipTitle",
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        alignment=1,
        textColor=colors.HexColor("#111827"),
        spaceAfter=18,
    )

    normal_style = ParagraphStyle(
        "PayslipNormal",
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#111827"),
    )

    section_style = ParagraphStyle(
        "PayslipSection",
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=12,
        textColor=colors.white,
    )

    elements = []

    elements.append(Paragraph("HRHub Pro - Weekly Payslip", title_style))

    left_header = Paragraph(
        f"""
        <b>{employee.full_name}</b><br/>
        {employee.employee_number}<br/>
        {employee.job_title}<br/>
        {employee.department.name if employee.department else "Warehouse Operations"}<br/>
        Leicester<br/>
        United Kingdom
        """,
        normal_style,
    )

    right_header = Paragraph(
        f"""
        <b>Personnel No:</b> {make_employee_number(employee)}<br/>
        <b>NI Number:</b> {make_national_insurance_number(employee)}<br/>
        <b>Tax Code:</b> 1257L<br/>
        <b>Pay Group:</b> Weekly Payroll<br/>
        <b>Pay Period:</b> {make_pay_period_number(payslip)}<br/>
        <b>Payment Date:</b> {payslip.payment_date.strftime("%d %b %Y") if payslip.payment_date else "-"}
        """,
        normal_style,
    )

    header_table = Table(
        [[left_header, right_header]],
        colWidths=[260, 260],
    )

    header_table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")),
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#ffffff")),
                ("PADDING", (0, 0), (-1, -1), 10),
            ]
        )
    )

    elements.append(header_table)
    elements.append(Spacer(1, 18))

    details_data = [
        [
            Paragraph("Details", section_style),
            "",
            Paragraph("Period", section_style),
            "",
        ],
        ["Pay Grade", "Hourly", "Week Start", payslip.week_start.strftime("%d %b %Y")],
        ["Rate Current", money(payslip.hourly_rate), "Week End", payslip.week_end.strftime("%d %b %Y")],
        ["Tax Basis", "Cumulative", "Status", payslip.get_status_display()],
        ["NI Letter", "A", "Cost Centre", "Warehouse"],
    ]

    details_table = Table(
        details_data,
        colWidths=[115, 145, 115, 145],
    )

    details_table.setStyle(
        TableStyle(
            [
                ("SPAN", (0, 0), (1, 0)),
                ("SPAN", (2, 0), (3, 0)),
                ("BACKGROUND", (0, 0), (1, 0), colors.HexColor("#60a5fa")),
                ("BACKGROUND", (2, 0), (3, 0), colors.HexColor("#60a5fa")),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cbd5e1")),
                ("FONTNAME", (0, 1), (0, -1), "Helvetica-Bold"),
                ("FONTNAME", (2, 1), (2, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8.5),
                ("PADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )

    elements.append(details_table)
    elements.append(Spacer(1, 18))

    standard_pay = (payslip.hours_worked * payslip.hourly_rate).quantize(Decimal("0.01"))
    overtime_pay = (payslip.overtime_hours * payslip.overtime_rate).quantize(Decimal("0.01"))

    earnings_table_data = [
        [Paragraph("Gross Earnings", section_style), "", "", ""],
        ["Description", "Hours", "Rate", "Value"],
        ["Basic Hours", payslip.hours_worked, money(payslip.hourly_rate), money(standard_pay)],
        ["Overtime", payslip.overtime_hours, money(payslip.overtime_rate), money(overtime_pay)],
        ["Bonus", "-", "-", money(payslip.bonus)],
        ["Total Pay", "", "", money(payslip.gross_pay)],
    ]

    deductions_table_data = [
        [Paragraph("Deductions", section_style), "", ""],
        ["Description", "This Period", "Year to Date"],
        ["PAYE", money(payslip.paye_tax), money(payslip.paye_tax)],
        ["Employee NI", money(payslip.national_insurance), money(payslip.national_insurance)],
        ["Other Deductions", money(payslip.other_deductions), money(payslip.other_deductions)],
        ["Total Deductions", money(payslip.total_deductions), money(payslip.total_deductions)],
    ]

    earnings_table = Table(
        earnings_table_data,
        colWidths=[105, 55, 65, 75],
    )

    deductions_table = Table(
        deductions_table_data,
        colWidths=[110, 80, 80],
    )

    table_style = TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#60a5fa")),
            ("SPAN", (0, 0), (-1, 0)),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cbd5e1")),
            ("FONTNAME", (0, 1), (-1, 1), "Helvetica-Bold"),
            ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8.5),
            ("PADDING", (0, 0), (-1, -1), 6),
            ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
        ]
    )

    earnings_table.setStyle(table_style)
    deductions_table.setStyle(table_style)

    earnings_and_deductions = Table(
        [[earnings_table, deductions_table]],
        colWidths=[305, 275],
    )

    earnings_and_deductions.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )

    elements.append(earnings_and_deductions)
    elements.append(Spacer(1, 24))

    totals_table = Table(
        [
            ["Gross Pay for PAYE", money(payslip.gross_pay), "Total Deductions", money(payslip.total_deductions)],
            ["Net Pay", "", "", money(payslip.net_pay)],
        ],
        colWidths=[150, 120, 150, 120],
    )

    totals_table.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cbd5e1")),
                ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#60a5fa")),
                ("FONTNAME", (0, 1), (-1, 1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("PADDING", (0, 0), (-1, -1), 7),
                ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                ("ALIGN", (3, 0), (3, -1), "RIGHT"),
                ("SPAN", (1, 1), (2, 1)),
            ]
        )
    )

    elements.append(totals_table)
    elements.append(Spacer(1, 18))

    if payslip.notes:
        message_table = Table(
            [
                [Paragraph("Message from Employer", section_style)],
                [payslip.notes],
            ],
            colWidths=[540],
        )

        message_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#60a5fa")),
                    ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cbd5e1")),
                    ("FONTSIZE", (0, 0), (-1, -1), 8.5),
                    ("PADDING", (0, 0), (-1, -1), 7),
                ]
            )
        )

        elements.append(message_table)

    document.build(elements)

    pdf = buffer.getvalue()
    buffer.close()

    response.write(pdf)

    return response


@login_required
def payslip_pdf_preview(request, pk):
    """
    Preview a weekly payslip PDF in the browser.
    """

    return build_payslip_pdf_response(request, pk, download=False)


@login_required
def payslip_pdf_download(request, pk):
    """
    Download a weekly payslip PDF file.
    """

    return build_payslip_pdf_response(request, pk, download=True)


@login_required
def payslip_pdf(request, pk):
    """
    Backwards compatible PDF download URL.
    """

    return build_payslip_pdf_response(request, pk, download=True)