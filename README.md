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
* **Multi-Format Upload:** Supports `.csv`, `.xlsx`, and `.xls` files of any column order[span_1](start_span)[span_1](end_span).
* **Auto-Detect Column Mapping:** Automatically recognizes standard BOM fields (Part Number, Component Name, Supplier, Country of Origin) as well as retail product structures[span_2](start_span)[span_2](end_span).
* **Automated Risk Screening:** Cross-checks components and suppliers against:
  * Sanctioned Countries (OFAC / EU / UN embargoes)[span_3](start_span)[span_3](end_span)
  * Restricted Entities (Denied-party supplier lists)[span_4](start_span)[span_4](end_span)
  * Controlled Keywords (EAR / ITAR dual-use terms)[span_5](start_span)[span_5](end_span)
* **Audit Reporting:** Flags high-risk items for review and allows users to download the completed compliance audit report[span_6](start_span)[span_6](end_span).

---

## Repository Structure
* `app.py` — Main Streamlit web application and screening logic[span_7](start_span)[span_7](end_span).
* `requirements.txt` — Python dependencies required for cloud deployment[span_8](start_span)[span_8](end_span).
* `sample_bom.csv` — Sample dataset for testing the screening workflow[span_9](start_span)[span_9](end_span).

---

## How to Run Locally

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/22072000palak-boop/bob-compliance-screener.git](https://github.com/22072000palak-boop/bob-compliance-screener.git)
   cd bob-compliance-screener
   2.Install dependies:pip install -r requirements.txt
   3.Launch the application :
   streamlit run app.py
   
