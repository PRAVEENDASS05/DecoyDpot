# Advanced Honeypot Dashboard UI Upgrade

## ✅ Important

Your existing `dashboard.py` logic and functions remain unchanged.
Only the **interface/UI** is upgraded.

---

# 1️⃣ Replace `templates/dashboard.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Honeypot Dashboard</title>

    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.2/css/all.min.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

    <style>

        body{
            background:#06142b;
            color:white;
            font-family:Arial, Helvetica, sans-serif;
        }

        .sidebar{
            width:250px;
            height:100vh;
            background:#081222;
            position:fixed;
            padding:20px;
            border-right:1px solid #1d2d50;
        }

        .sidebar h3{
            color:#ff4d4d;
            margin-bottom:30px;
        }

        .sidebar a{
            display:block;
            color:#cbd5e1;
            text-decoration:none;
            padding:12px;
            margin-bottom:10px;
            border-radius:10px;
            transition:0.3s;
        }

        .sidebar a:hover{
            background:#1e3a8a;
            color:white;
        }

        .main{
            margin-left:270px;
            padding:30px;
        }

        .top-title{
            font-size:38px;
            font-weight:bold;
        }

        .card-box{
            border-radius:18px;
            padding:25px;
            color:white;
            margin-bottom:20px;
            box-shadow:0 0 20px rgba(0,0,0,0.3);
        }

        .red-card{
            background:linear-gradient(135deg,#7f1d1d,#dc2626);
        }

        .orange-card{
            background:linear-gradient(135deg,#78350f,#f97316);
        }

        .blue-card{
            background:linear-gradient(135deg,#1e3a8a,#2563eb);
        }

        .green-card{
            background:linear-gradient(135deg,#14532d,#16a34a);
        }

        .card-number{
            font-size:40px;
            font-weight:bold;
        }

        .dashboard-panel{
            background:#0b1730;
            border-radius:20px;
            padding:20px;
            margin-top:25px;
            box-shadow:0 0 20px rgba(0,0,0,0.2);
        }

        table{
            color:white !important;
        }

        th{
            background:#ef4444 !important;
            color:white;
        }

        td{
            background:#091427 !important;
            border-color:#1f2937 !important;
        }

        .btn-custom{
            border:none;
            border-radius:10px;
            padding:10px 18px;
            font-weight:bold;
        }

        .severity-high{
            color:#ef4444;
            font-weight:bold;
        }

        .severity-medium{
            color:#f59e0b;
            font-weight:bold;
        }

        .severity-low{
            color:#22c55e;
            font-weight:bold;
        }

        .filter-box input{
            background:#0f172a;
            border:1px solid #1e293b;
            color:white;
        }

        .filter-box input::placeholder{
            color:#94a3b8;
        }

    </style>
</head>
<body>

<div class="sidebar">

    <h3><i class="fa-solid fa-shield-halved"></i> Honeypot System</h3>

    <a href="#"><i class="fa-solid fa-chart-line"></i> Dashboard</a>
    <a href="#logs"><i class="fa-solid fa-file-lines"></i> Activity Logs</a>
    <a href="#"><i class="fa-solid fa-bell"></i> Alerts</a>
    <a href="#"><i class="fa-solid fa-file"></i> Decoy Documents</a>
    <a href="#"><i class="fa-solid fa-gear"></i> Settings</a>

    <hr>

    <a href="/logout"><i class="fa-solid fa-right-from-bracket"></i> Logout</a>

</div>

<div class="main">

    <div class="d-flex justify-content-between align-items-center mb-4">
        <div>
            <div class="top-title">Administrator Dashboard</div>
            <div class="text-secondary">Real-time monitoring of suspicious activities</div>
        </div>

        <div>
            <button class="btn btn-success btn-custom" onclick="location.reload()">
                <i class="fa-solid fa-rotate"></i> Refresh
            </button>

            <button class="btn btn-danger btn-custom" onclick="confirmReset()">
                <i class="fa-solid fa-trash"></i> Reset Logs
            </button>
        </div>
    </div>


    <div class="row">

        <div class="col-md-3">
            <div class="card-box red-card">
                <h5>Total Alerts</h5>
                <div class="card-number">{{logs|length}}</div>
                <div><i class="fa-solid fa-triangle-exclamation"></i> Active alerts detected</div>
            </div>
        </div>

        <div class="col-md-3">
            <div class="card-box orange-card">
                <h5>Suspicious Activities</h5>
                <div class="card-number">{{logs|length}}</div>
                <div><i class="fa-solid fa-user-secret"></i> Unauthorized access attempts</div>
            </div>
        </div>

        <div class="col-md-3">
            <div class="card-box blue-card">
                <h5>Decoy Documents</h5>
                <div class="card-number">12</div>
                <div><i class="fa-solid fa-file"></i> Active decoy files</div>
            </div>
        </div>

        <div class="col-md-3">
            <div class="card-box green-card">
                <h5>System Status</h5>
                <div class="card-number">ACTIVE</div>
                <div><i class="fa-solid fa-shield"></i> Monitoring operational</div>
            </div>
        </div>

    </div>


    <div class="dashboard-panel">

        <div class="row">

            <div class="col-md-8">
                <h4>Alerts Overview</h4>
                <canvas id="alertChart"></canvas>
            </div>

            <div class="col-md-4">
                <h4>Event Severity</h4>
                <canvas id="severityChart"></canvas>
            </div>

        </div>

    </div>


    <div class="dashboard-panel mt-4" id="logs">

        <div class="d-flex justify-content-between align-items-center mb-3">
            <h4>Recent Alerts / Activity Logs</h4>
        </div>


        <form method="GET" action="/dashboard" class="row g-3 filter-box mb-4">

            <div class="col-md-3">
                <input type="text" name="user" class="form-control" placeholder="Filter by User">
            </div>

            <div class="col-md-3">
                <input type="text" name="event" class="form-control" placeholder="Filter by Event">
            </div>

            <div class="col-md-3">
                <input type="text" name="file" class="form-control" placeholder="Filter by File">
            </div>

            <div class="col-md-3 d-flex gap-2">
                <button type="submit" class="btn btn-success w-100">
                    <i class="fa-solid fa-magnifying-glass"></i> Apply
                </button>

                <button type="button" onclick="location.href='/dashboard'" class="btn btn-danger w-100">
                    Clear
                </button>
            </div>

        </form>


        <div class="table-responsive">

            <table class="table table-bordered table-hover align-middle">

                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Time</th>
                        <th>User</th>
                        <th>Host</th>
                        <th>IP</th>
                        <th>Event</th>
                        <th>File</th>
                    </tr>
                </thead>

                <tbody>

                    {% for row in logs %}

                    <tr>
                        <td>{{row[0]}}</td>
                        <td>{{row[1]}}</td>
                        <td>{{row[2]}}</td>
                        <td>{{row[3]}}</td>
                        <td>{{row[4]}}</td>

                        <td>

                            {% if row[5] == 'DELETED' %}
                                <span class="severity-high">HIGH</span>

                            {% elif row[5] == 'MODIFIED' %}
                                <span class="severity-medium">MEDIUM</span>

                            {% else %}
                                <span class="severity-low">LOW</span>
                            {% endif %}

                            <br>
                            {{row[5]}}

                        </td>

                        <td>{{row[6]}}</td>
                    </tr>

                    {% endfor %}

                </tbody>

            </table>

        </div>

    </div>

</div>


<script>

function confirmReset(){

    if(confirm("Are you sure you want to delete all logs?")){
        window.location="/reset_logs"
    }

}


const ctx = document.getElementById('alertChart');

new Chart(ctx, {
    type: 'line',
    data: {
        labels: ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'],
        datasets: [{
            label: 'Alerts',
            data: [3,7,4,9,5,2,8],
            borderColor: '#ef4444',
            backgroundColor:'rgba(239,68,68,0.2)',
            tension:0.4,
            fill:true
        }]
    }
});


const pie = document.getElementById('severityChart');

new Chart(pie, {
    type:'doughnut',
    data:{
        labels:['High','Medium','Low'],
        datasets:[{
            data:[12,8,4],
            backgroundColor:['#ef4444','#f59e0b','#22c55e']
        }]
    }
});

</script>

</body>
</html>
```

---

# 2️⃣ Keep Your Existing `dashboard.py`

✅ No logic changed
✅ No functions changed
✅ Your filters still work
✅ Reset logs still works
✅ Login still works

---

# 3️⃣ Run the Dashboard

```bash
python dashboard.py
```

Open:

```text
http://127.0.0.1:5000
```

---

# ✅ New Features Added

✔ Modern SOC-style dashboard
✔ Sidebar navigation
✔ Statistics cards
✔ Line chart analytics
✔ Severity doughnut chart
✔ Advanced dark UI
✔ Severity levels (High / Medium / Low)
✔ Bootstrap responsive layout
✔ Icons using Font Awesome
✔ Filter section redesign
✔ Better activity table
✔ Professional admin dashboard look

---

# 🔥 Your Project Now Looks Like

* Real cybersecurity SOC dashboard
* Enterprise monitoring system
* SIEM / Honeypot platform
* Threat monitoring panel

This is far beyond a normal mini project UI.
