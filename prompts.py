DEVELOPMENT_OPP_EXAMPLE = """1 │ Executive Summary
Parcel P‑3 is a ~7.6‑acre (≈330,939 sf) BPDA‑controlled site fronting Tremont Street opposite Ruggles Station in Roxbury’s rapidly revitalising Nubian Square district. The City is seeking a long‑term ground‑lease partner to transform this long‑vacant land into a catalytic mixed‑use campus that advances affordable housing, life‑science employment, and community‑serving cultural space.
City of Boston Planning Department
City of Boston Planning Department

Attribute	Detail
Address	South side of Tremont St. at Ruggles St., Roxbury
Ownership	Boston Planning & Development Agency (BPDA)
Land area	330,939 sf (±7.6 acres)
Zoning/Plans	Campus High Urban Renewal Area; must align with PLAN: Nubian Square and Roxbury Strategic Master Plan
Disposition	99‑year ground lease via BPDA RFP
Transit	Adjacent to MBTA Orange Line & commuter rail (Ruggles), multiple bus routes

2 │ Planning & Zoning Context
The site sits in a Transit‑Oriented core with no height cap under Article 80 large‑project review; FAR of 6.0–8.0 is supportable given precedent life‑science approvals along Tremont St. A minimum 20 % on‑site affordable housing ratio and Article 37 Net‑Zero‑Carbon compliance are mandatory. Public feedback prioritises ground‑floor cultural uses and robust open‑space links to Melnea Cass Blvd greenways.
City of Boston Planning Department

3 │ Market Rationale
Life Science Expansion – Boston’s lab vacancy rests below 3 % in core clusters; Nubian Square offers lower land basis yet the same 15‑minute transit access to Kendall Sq. and the Seaport, positioning P‑3 to capture spill‑over R&D demand.

Housing Pressure – Roxbury median rents have risen 31 % since 2020; deep‑income‑tier housing is undersupplied.

Civic Identity – The neighbourhood lacks a dedicated museum or large performance venue celebrating Roxbury’s cultural legacy; the RFP explicitly rewards proposals delivering such assets.
City of Boston Planning Department

 │ Illustrative Development Program
Component	GSF	Description
Life‑science R&D (2 towers)	550,000 gsf	8–12 story mass‑timber over podium; 32 k sf floorplates
Workforce training center	40,000 gsf	Biotech skills academy operated by Roxbury CC
Mixed‑income housing	420,000 gsf (≈400 units)	60 % market‑rate, 20 % 60‑80 AMI, 20 % ≤50 AMI
Cultural/museum space	60,000 gsf	“Boston Civil Rights & Policy Center” with 500‑seat auditorium
Retail + food hall	35,000 gsf	Local‑operator preference, 25 % micro‑retail (<500 sf)
Structured parking	350 sp	Below‑grade, EV‑ready, 1:5,000 gsf lab ratio
Public open space	1.8 ac	Central green + Tremont St plaza; climate‑resilient landscaping

5 │ Financial Snapshot (order‑of‑magnitude)
Total development cost: $1.05 B

Hard costs $715 M (lab $1,000 /sf; res $475 /sf)

Soft costs $210 M (20 %)

Contingency $52 M (5 %)

Land (ground‑lease PV) $75 M

Capital stack: 60 % senior debt, 25 % equity, 10 % mezzanine, 5 % NMTC/HTC.

Stabilised NOI: $63 M (lab $52 M, residential $9 M, retail $2 M).

Levered IRR (10‑yr exit): 16 %.

Public benefits value: ≈$170 M (land rent, affordable units, cultural fit‑out, workforce program).

6 │ Key Approvals & Milestones
BPDA Designation – Q4 2025 selection following RFP presentations.

Article 80 Large‑Project Review – Scoping & DEIR by Q2 2026; BCDC design approvals concurrent.

Zoning & Urban Renewal Modification – Campus High URA amendment to permit lab use; targeted Q4 2026.

Financing & Ground‑Lease Execution – Q2 2027.

Phase 1 Commencement (Housing + Cultural Core) – Q3 2027; 30‑month schedule.

Full Build‑Out – Final Phase (Lab Tower 2) completes 2032.

7 │ Investment Thesis
By integrating life‑science employment engines with urgently needed affordable housing and signature cultural space, Parcel P‑3 can anchor Nubian Square’s evolution into a resilient, inclusive innovation district. Transit adjacency, City sponsorship, and a community‑backed planning framework materially de‑risk entitlement, while Boston’s structural demand for premier lab inventory underwrites robust long‑term cash‑flow.

This memorandum is illustrative and draws on publicly available BPDA procurement documents; prospective proponents must perform independent due diligence and financial verification."""

DEVELOPMENT_OPPORTUNITIES_PROMPT = f"""
You are a real estate agent. You are given a property and information about that property, including parcel information, surrounding properties, and building value. Your job is to determine if any potential development opportunities are feasible for this property, and if so, what they are.

A development opportunity is something that could potentially be developed to increase the revenue of the property.

Here's an example of a development opportunity:
<DEVELOPMENT_OPP_EXAMPLE>
{DEVELOPMENT_OPP_EXAMPLE}
</DEVELOPMENT_OPP_EXAMPLE>

Here is a report about some recent developments in the area:
<RECENT_DEVELOPMENTS>
[RECENT_DEVELOPMENTS]
</RECENT_DEVELOPMENTS>

Consider questions like "How is this property currently being under utilized" and "What could we do to better take advantage of the property?".

Here's the property information:
<PROPERTY_INFO>
[PROPERTY_INFO]
</PROPERTY_INFO>

Create a report detailing the feasibility of the devleopment opportunities on this property, and who to contact to potentially buy the property. Do not use the first person, and format the promt as if it was being sent directly to the real estate developer.
"""

GET_SIMILAR_DEVELOPMENT_PROMPT = """You are an expert real estate developer assistant. Given some information about a property, your goal is to find  developments nearby that could be used as a reference for the development. 
The end goal for the real estate firm is to determine the financial feasibility of developing the property. In order to do this, you should find similar devlopments nearby and analyze the financials of those developments (if possible), in order to create a good understanding of the financials of the property we're analyzing.
Do extensive research, and discover as much about the surrounding area and the new properties as possible.List out the recent developments in the area with as much detail as possible.

Here is some information about the property in Boston.

<PROPERTY_INFO>
[PROPERTY_INFO]
</PROPERTY_INFO>

Next to each of the developments, list the source you used to find the development.

Using the search tool, find similar developments nearby. Return only the report, and do not use the first person. Only list the developments, do not refer to your tools or thinking. 
"""
