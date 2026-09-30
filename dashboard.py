from flask import Flask, render_template, request, redirect, session, send_file
import sqlite3
import datetime

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak
)

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter

from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart


app = Flask(__name__)
app.secret_key = "honeypot_secret"

USERNAME = "admin"
PASSWORD = "admin123"


# ================= LOGIN =================

@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        user = request.form["username"]
        pwd = request.form["password"]

        if user == USERNAME and pwd == PASSWORD:

            session["admin"] = True

            return redirect("/dashboard")

    return render_template("login.html")


# ================= DASHBOARD =================

@app.route("/dashboard")
def dashboard():

    if "admin" not in session:
        return redirect("/")

    conn = sqlite3.connect("honeypot_logs.db")

    cursor = conn.cursor()

    cursor.execute("SELECT * FROM logs ORDER BY id ASC")

    logs = cursor.fetchall()

    conn.close()

    # ================= COUNTS =================

    total_alerts = len(logs)

    created_count = 0
    modified_count = 0
    deleted_count = 0

    unique_docs = set()

    timeline_dates = []
    timeline_values = []

    count = 1

    for row in logs:

        event = str(row[5]).upper()

        file_path = row[6]

        unique_docs.add(file_path)

        if event == "CREATED":
            created_count += 1

        elif event == "MODIFIED":
            modified_count += 1

        elif event == "DELETED":
            deleted_count += 1

        # timeline data
        timeline_dates.append(str(row[1]).split(" ")[0])
        timeline_values.append(count)

        count += 1

    suspicious_count = modified_count + deleted_count

    decoy_count = len(unique_docs)

    return render_template(

        "dashboard.html",

        logs=logs,

        total_alerts=total_alerts,

        suspicious_count=suspicious_count,

        decoy_count=decoy_count,

        created_count=created_count,

        modified_count=modified_count,

        deleted_count=deleted_count,

        timeline_dates=timeline_dates,

        timeline_values=timeline_values

    )


# ================= ACTIVITY LOGS =================

@app.route("/activity")
def activity():

    if "admin" not in session:
        return redirect("/")

    conn = sqlite3.connect("honeypot_logs.db")

    cursor = conn.cursor()

    cursor.execute("SELECT * FROM logs ORDER BY id ASC")

    logs = cursor.fetchall()

    conn.close()

    return render_template("activity.html", logs=logs)


# ================= ALERTS =================

@app.route("/alerts")
def alerts():

    if "admin" not in session:
        return redirect("/")

    conn = sqlite3.connect("honeypot_logs.db")

    cursor = conn.cursor()

    cursor.execute("""

        SELECT * FROM logs

        WHERE event_type='MODIFIED'

        OR event_type='DELETED'

        ORDER BY id DESC

    """)

    logs = cursor.fetchall()

    conn.close()

    return render_template("alerts.html", logs=logs)


# ================= SETTINGS =================

@app.route("/settings", methods=["GET", "POST"])
def settings():

    global PASSWORD

    if "admin" not in session:
        return redirect("/")

    message = ""

    if request.method == "POST":

        new_password = request.form["password"]

        if new_password:

            PASSWORD = new_password

            message = "Password Changed Successfully"

    return render_template("settings.html", message=message)


# ================= RESET LOGS =================

@app.route("/reset_logs")
def reset_logs():

    if "admin" not in session:
        return redirect("/")

    conn = sqlite3.connect("honeypot_logs.db")

    cursor = conn.cursor()

    cursor.execute("DELETE FROM logs")

    cursor.execute("DELETE FROM sqlite_sequence WHERE name='logs'")

    conn.commit()

    conn.close()

    return redirect("/dashboard")


# ================= PDF REPORT =================

@app.route("/generate_report")
def generate_report():

    if "admin" not in session:
        return redirect("/")

    conn = sqlite3.connect("honeypot_logs.db")

    cursor = conn.cursor()

    cursor.execute("SELECT * FROM logs ORDER BY id DESC")

    logs = cursor.fetchall()

    conn.close()

    pdf_file = "honeypot_report.pdf"

    doc = SimpleDocTemplate(

        pdf_file,

        pagesize=letter

    )

    styles = getSampleStyleSheet()

    elements = []

    # ================= TITLE =================

    title = Paragraph(

        "<b>Honeypot Monitoring Security Report</b>",

        styles['Title']

    )

    elements.append(title)

    elements.append(Spacer(1,20))

    # ================= DATE =================

    current_time = datetime.datetime.now().strftime(

        "%d-%m-%Y %I:%M:%S %p"

    )

    date_para = Paragraph(

        f"<b>Generated Date & Time :</b> {current_time}",

        styles['Normal']

    )

    elements.append(date_para)

    elements.append(Spacer(1,20))

    # ================= COUNTS =================

    created_count = 0
    modified_count = 0
    deleted_count = 0

    unique_files = set()

    for row in logs:

        event = str(row[5]).upper()

        unique_files.add(row[6])

        if event == "CREATED":
            created_count += 1

        elif event == "MODIFIED":
            modified_count += 1

        elif event == "DELETED":
            deleted_count += 1

    total_alerts = len(logs)

    suspicious_count = modified_count + deleted_count

    decoy_count = len(unique_files)

    # ================= SUMMARY =================

    summary_title = Paragraph(

        "<b>Security Summary</b>",

        styles['Heading2']

    )

    elements.append(summary_title)

    elements.append(Spacer(1,10))

    summary_text = f"""

    <b>Total Alerts :</b> {total_alerts}<br/><br/>

    <b>Suspicious Activities :</b> {suspicious_count}<br/><br/>

    <b>Decoy Documents :</b> {decoy_count}<br/><br/>

    <b>Created Events :</b> {created_count}<br/><br/>

    <b>Modified Events :</b> {modified_count}<br/><br/>

    <b>Deleted Events :</b> {deleted_count}<br/><br/>

    <b>Severity Status :</b> ACTIVE MONITORING ENABLED<br/><br/>

    """

    summary_para = Paragraph(

        summary_text,

        styles['BodyText']

    )

    elements.append(summary_para)

    elements.append(Spacer(1,25))

    # ================= PRIORITY CHART =================

    chart_title = Paragraph(

        "<b>Priority Level Analysis</b>",

        styles['Heading2']

    )

    elements.append(chart_title)

    elements.append(Spacer(1,15))

    drawing = Drawing(400,200)

    chart = VerticalBarChart()

    chart.x = 50
    chart.y = 50

    chart.height = 125
    chart.width = 300

    chart.data = [

        (

            created_count,
            modified_count,
            deleted_count

        )

    ]

    chart.categoryAxis.categoryNames = [

        'Created',
        'Modified',
        'Deleted'

    ]

    chart.bars[0].fillColor = colors.darkblue

    drawing.add(chart)

    elements.append(drawing)

    elements.append(Spacer(1,30))

    # ================= DESCRIPTION SUMMARY =================

    desc_title = Paragraph(

        "<b>Event Description Summary</b>",

        styles['Heading2']

    )

    elements.append(desc_title)

    elements.append(Spacer(1,15))

    for row in logs[:10]:

        event = row[5]
        file_name = row[6]
        timestamp = row[1]

        description = f"""

        <b>Event :</b> {event}<br/>

        <b>Time :</b> {timestamp}<br/>

        <b>Description :</b>
        A suspicious activity was detected in the honeypot environment.
        The monitored decoy document
        <b>{file_name}</b>
        triggered a security event classified as
        <b>{event}</b>.
        This activity was recorded for forensic investigation.

        """

        para = Paragraph(

            description,

            styles['BodyText']

        )

        elements.append(para)

        elements.append(Spacer(1,18))

    # ================= NEW PAGE =================

    elements.append(PageBreak())

    # ================= LOG TABLE =================

    table_title = Paragraph(

        "<b>Detailed Honeypot Log Report</b>",

        styles['Heading2']

    )

    elements.append(table_title)

    elements.append(Spacer(1,20))

    data = [[

        "ID",
        "Time",
        "User",
        "Host",
        "IP",
        "Event",
        "File"

    ]]

    for row in logs:

        data.append([

            str(row[0]),
            str(row[1]),
            str(row[2]),
            str(row[3]),
            str(row[4]),
            str(row[5]),
            str(row[6])

        ])

    table = Table(data)

    table.setStyle(TableStyle([

        ('BACKGROUND',(0,0),(-1,0),colors.darkblue),

        ('TEXTCOLOR',(0,0),(-1,0),colors.white),

        ('GRID',(0,0),(-1,-1),1,colors.black),

        ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),

        ('BACKGROUND',(0,1),(-1,-1),colors.beige),

        ('FONTSIZE',(0,0),(-1,-1),8)

    ]))

    elements.append(table)

    # ================= BUILD PDF =================

    doc.build(elements)

    return send_file(

        pdf_file,

        as_attachment=True

    )


# ================= LOGOUT =================

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")


# ================= MAIN =================

if __name__ == "__main__":

    app.run(debug=True)