# BOM Compliance & Sanctions Screener

An automated web application built with Python and Streamlit that cross-references Bill of Materials (BOM) components against global trade sanctions, denied-party supplier lists, and export-control keywords.

**Live Application:** [Open BOM Compliance & Sanctions Screener](https://bob-compliance-screener-ggqqpjg7jdzemyhqefk2fw.streamlit.app)

---

## Problem Statement
Manually checking every component and supplier in a manufacturing Bill of Materials against international trade restrictions is slow and prone to human error. A single overlooked sanctioned supplier or export-controlled part can halt shipments, trigger heavy regulatory fines, and disrupt supply chains.

## Solution
This tool automates compliance auditing by allowing users to upload their BOM spreadsheets and instantly screen all entries against restricted lists and dual-use keywords, highlighting risks before manufacturing or shipping begins.

---

## Key Features
* **Multi-Format Upload:** Supports `.csv`, `.xlsx`, and `.xls` files of any column order.
* **Auto-Detect Column Mapping:** Automatically recognizes standard BOM fields (Part Number, Component Name, Supplier, Country of Origin) as well as retail product structures.
* **Automated Risk Screening:** Cross-checks components and suppliers against:
  * Sanctioned Countries (OFAC / EU / UN embargoes)
  * Restricted Entities (Denied-party supplier lists)
  * Controlled Keywords (EAR / ITAR dual-use terms)
* **Audit Reporting:** Flags high-risk items for review and allows users to download the completed compliance audit report.

---

## Repository Structure
* `app.py` — Main Streamlit web application and screening logic.
* `requirements.txt` — Python dependencies required for cloud deployment.
* `sample_bom.csv` — Sample dataset for testing the screening workflow.

---

## How to Run Locally

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/22072000palak-boop/bob-compliance-screener.git](https://github.com/22072000palak-boop/bob-compliance-screener.git)
   cd bob-compliance-screener
   2.Install dependies:pip install -r requirements.txt
   3.Launch the application :
   streamlit run app.py
   
