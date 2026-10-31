
import tempfile
from pathlib import Path

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from optimizer import calculate_cost, gradient_descent
from backup import upload_backup, restore_backup, list_backups

st.set_page_config(
    page_title="SmartCloud Archive",
    page_icon="☁️",
    layout="wide"
)

st.title("☁️ SmartCloud Archive")
st.subheader("Calculus-Based Optimization of Cloud Data Backup Scheduling")

st.write(
    "Optimize cloud backup scheduling using Gradient Descent "
    "and securely store files using Supabase Cloud Storage."
)

st.info(
    "Educational simulation: optimization parameters and cost scores "
    "are illustrative, not actual cloud service prices."
)

# SIDEBAR
st.sidebar.header("Optimization Settings")

A = st.sidebar.number_input(
    "Parameter A",
    min_value=1.0,
    max_value=10000.0,
    value=144.0,
    step=1.0
)

B = st.sidebar.number_input(
    "Parameter B",
    min_value=0.01,
    max_value=100.0,
    value=0.25,
    step=0.01,
    format="%.2f"
)

initial_interval = st.sidebar.slider(
    "Initial backup interval (hours)",
    min_value=1,
    max_value=168,
    value=48
)

st.sidebar.caption("Allowed interval: 1 to 168 hours.")

# GRADIENT DESCENT OPTIMIZATION
if st.button("Calculate Optimal Backup Interval", type="primary"):

    optimal_interval, minimum_cost, history = gradient_descent(
        A=A,
        B=B,
        initial_interval=float(initial_interval)
    )

    st.session_state["result"] = {
        "A": A,
        "B": B,
        "initial_interval": initial_interval,
        "optimal_interval": optimal_interval,
        "minimum_cost": minimum_cost,
        "history": history
    }

# DISPLAY OPTIMIZATION RESULTS
if "result" not in st.session_state:

    st.subheader("How to use")

    st.write("1. Choose parameters A and B.")
    st.write("2. Select an initial backup interval.")
    st.write("3. Click Calculate Optimal Backup Interval.")
    st.write("4. Review the optimization results and graphs.")

else:

    result = st.session_state["result"]

    A = result["A"]
    B = result["B"]
    optimal_interval = result["optimal_interval"]
    minimum_cost = result["minimum_cost"]
    history = result["history"]

    initial_cost = calculate_cost(
        result["initial_interval"], A, B
    )

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Recommended Interval",
        f"{optimal_interval:.2f} hours"
    )

    col2.metric(
        "Minimum Model Cost",
        f"{minimum_cost:.2f}"
    )

    col3.metric(
        "Initial Model Cost",
        f"{initial_cost:.2f}",
        delta=f"{minimum_cost - initial_cost:.2f}",
        delta_color="inverse"
    )

    st.success(
        f"Recommended backup interval: every "
        f"{optimal_interval:.2f} hours."
    )

    st.divider()

    # GRAPH 1: OBJECTIVE FUNCTION
    st.subheader("1. Model Cost vs Backup Interval")

    intervals = [
        1 + i * (167 / 299)
        for i in range(300)
    ]

    costs = [
        calculate_cost(t, A, B)
        for t in intervals
    ]

    fig1, ax1 = plt.subplots(figsize=(9, 4))

    ax1.plot(intervals, costs, label="Model cost")

    ax1.scatter(
        [optimal_interval],
        [minimum_cost],
        label="Recommended interval",
        zorder=3
    )

    ax1.set_xlabel("Backup interval (hours)")
    ax1.set_ylabel("Model cost score")
    ax1.set_title("Objective Function")
    ax1.grid(True, alpha=0.3)
    ax1.legend()

    st.pyplot(fig1)
    plt.close(fig1)

    # GRAPH 2: GRADIENT DESCENT
    st.subheader("2. Gradient Descent Convergence")

    history_df = pd.DataFrame(history)

    fig2, ax2 = plt.subplots(figsize=(9, 4))

    ax2.plot(
        history_df["iteration"],
        history_df["cost"],
        marker=".",
        markersize=3
    )

    ax2.set_xlabel("Iteration")
    ax2.set_ylabel("Model cost score")
    ax2.set_title("Cost Reduction During Optimization")
    ax2.grid(True, alpha=0.3)

    st.pyplot(fig2)
    plt.close(fig2)

    # COMPARISON TABLE
    st.subheader("3. Backup Interval Comparison")

    comparison_intervals = sorted(set([
        6.0,
        12.0,
        24.0,
        48.0,
        72.0,
        float(optimal_interval)
    ]))

    comparison = pd.DataFrame({
        "Backup interval (hours)": comparison_intervals,
        "Model cost score": [
            calculate_cost(t, A, B)
            for t in comparison_intervals
        ]
    })

    comparison["Recommended"] = comparison[
        "Backup interval (hours)"
    ].apply(
        lambda t: "Yes" if abs(t - optimal_interval) < 0.01 else "No"
    )

    st.dataframe(
        comparison,
        use_container_width=True,
        hide_index=True
    )

    # MATHEMATICAL FORMULATION
    st.subheader("4. Mathematical Formulation")

    st.latex(r"J(T) = \frac{A}{T} + BT")
    st.latex(r"J'(T) = -\frac{A}{T^2} + B")
    st.latex(
        r"T_{\mathrm{new}} = T_{\mathrm{old}} - \alpha J'(T)"
    )

    st.write(
        "**T:** Backup interval in hours. "
        "**A:** Backup-related cost parameter. "
        "**B:** Estimated data-loss risk parameter. "
        "**J(T):** Combined model cost score."
    )

    with st.expander("View optimization history"):

        st.dataframe(
            history_df,
            use_container_width=True,
            hide_index=True
        )

    st.caption(
        "The recommendation is based on an illustrative mathematical model. "
        "Actual backup policies should consider recovery objectives, "
        "retention requirements and tested restoration."
    )

# SUPABASE CLOUD BACKUP AND RECOVERY
st.divider()

st.header("☁️ Supabase Cloud Backup and Recovery")

st.write(
    "Upload your files to Supabase Cloud Storage, "
    "view stored backups and restore previous files."
)

# UPLOAD BACKUP
st.subheader("1. Upload Backup")

uploaded_file = st.file_uploader(
    "Choose a file to upload to cloud storage",
    key="backup_file"
)

if st.button("Upload Backup to Cloud"):

    if uploaded_file is None:

        st.error("Please select a file first.")

    else:

        temp_path = None

        try:

            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix="_" + Path(uploaded_file.name).name
            ) as temp_file:

                temp_file.write(uploaded_file.getvalue())
                temp_path = temp_file.name

            object_name = upload_backup(temp_path)

            st.session_state["last_backup_name"] = object_name

            st.success("File uploaded successfully to Supabase!")

            st.write("Cloud backup filename:")
            st.code(object_name)

        except Exception as e:

            st.error(f"Backup failed: {e}")

        finally:

            if temp_path and Path(temp_path).exists():
                Path(temp_path).unlink()

# VIEW CLOUD BACKUPS
st.subheader("2. Cloud Backup History")

if st.button("Refresh Backup List"):

    try:

        cloud_backups = list_backups()

        if cloud_backups:

            backup_names = [
                item["name"]
                for item in cloud_backups
                if item.get("name")
            ]

            st.session_state["cloud_backups"] = backup_names

        else:

            st.session_state["cloud_backups"] = []

    except Exception as e:

        st.error(f"Unable to retrieve backups: {e}")

backup_names = st.session_state.get("cloud_backups", [])

if backup_names:

    st.success(f"{len(backup_names)} backup file(s) found in cloud.")

    st.dataframe(
        pd.DataFrame({"Cloud Backup Files": backup_names}),
        use_container_width=True,
        hide_index=True
    )

else:

    st.info("Click Refresh Backup List to view your cloud backups.")

# RESTORE BACKUP
st.subheader("3. Restore Backup")

if backup_names:

    selected_backup = st.selectbox(
        "Select a backup file to restore",
        options=backup_names
    )

    if st.button("Restore Selected Backup"):

        try:

            with tempfile.TemporaryDirectory() as temp_dir:

                destination = (
                    Path(temp_dir) / Path(selected_backup).name
                )

                restore_backup(
                    selected_backup,
                    destination
                )

                file_bytes = destination.read_bytes()

                st.success("Backup restored successfully!")

                st.download_button(
                    "Download Restored File",
                    data=file_bytes,
                    file_name=Path(selected_backup).name,
                    mime="application/octet-stream"
                )

        except Exception as e:

            st.error(f"Restore failed: {e}")

else:

    st.info("Upload a backup and refresh the list before restoring.")

st.divider()

st.caption(
    "SmartCloud Archive | Calculus + Cloud Computing | "
    "Gradient Descent + Supabase Storage"
)
