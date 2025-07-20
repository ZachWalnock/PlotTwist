DEVELOPMENT_OPP_EXAMPLE = """<Report> <Analysis> [ANALYSIS]
1  Property snapshot

Address: 333 Tremont St, Boston, MA 02116 – a free‑standing, cylindrical structure in the Theater District, steps from Boston Common.

Existing improvements: ±14 000 SF GBA over three above‑grade floors plus basement (≈4 000 SF | 2 000 SF | 4 000 SF by floor), 20‑ft stage volume, elevator, commercial kitchens and ±8 surface parking spaces. Built 1972 and presently marketed only for short‑term tenancy, so occupancy is low. 
J Barrett Realty
Zillow

2  Location & access

200 ft to Boylston MBTA Green Line entrance and ~0.2 mi to the Orange Line at Chinatown; Boylston averaged ~5 265 weekday boardings (FY 2019) and patronage is rebounding post‑COVID. 
Wikipedia

Walk Score 99; the Tremont/Boylston corner captures heavy tourist, commuter, and theater traffic.

3  Regulatory context (high‑level)

Falls in the Midtown Cultural / Theater District (Article 38) overlay. Base FAR ≈ 8.0 with bonuses for cultural, affordable‑housing, or sustainability contributions; height limits up to ~155 ft subject to design review and shadow protections on Boston Common.

Not individually landmarked, but adjacency to historic resources triggers Boston Landmarks and Mass. Historic Commission consultation for exterior changes.
Confirm zoning and overlay data with BPDA before design.

4  Market indicators (Q2 2025 unless noted)

Sector	Vacancy / Availability	Trend & note	Source
Downtown office	18.8 % vacancy / 23.3 % availability	Soft demand but flight‑to‑quality; conversions gaining traction	
CBRE
Greater Boston multifamily	5.8 % vacancy (Q1 2025)	Tight supply supports rent growth	
Colliers
Tourism / hotels	Occupancy back to ~80 % city‑wide (industry reports); ADR above 2019	industry data	

5  SWOT (site‑specific)
Strengths – irreplaceable core location; transit‑rich; unique cylindrical “icon” lends branding value; sizeable floorplates for adaptive reuse.
Weaknesses – non‑rectilinear geometry complicates layouts; limited on‑site parking; 1970s systems likely obsolete.
Opportunities – zoning incentives for cultural uses; growing demand for experiential retail and boutique hospitality; city encouragement of office→residential or life‑science conversions.
Threats – high construction costs, stringent shadow / wind studies, competition from newer Seaport assets, lingering office softness.

</ANALYSIS> <OPPORTUNITIES> [OPPORTUNITIES]
Adaptive‑reuse boutique hotel + ground‑floor food & beverage
Why: Cylindrical form fits compact guest‑room ring layout; stage volume converts to speakeasy‑style performance venue; Theater District synergy boosts midweek occupancy.

Vertical addition (2–4 floors) to create 40–60 micro‑loft apartments
Why: FAR headroom and cultural/affordable bonuses can justify extra density; strong multifamily fundamentals and limited new supply downtown.

Hybrid “arts‑tech hub”
Why: Retain lower level performance space, insert two floors of creative co‑working / podcast studios, top floor event terrace. Aligns with city goals for activating cultural districts and leverages demand for flexible, character‑rich office alternatives.

Life‑science TAMI (tech/advertising/media/information) conversion
Why: 20‑ft clear height and elevator core support lab/collaboration floors; modest size suits seed‑stage biotechs priced out of Seaport/Kendal; proximity to Tufts Medical & Mass General talent pool. Requires HVAC/MEP overhaul and hazardous‑use permitting.

Next steps: order ALTA survey & Phase I ESA, confirm Article 80 thresholds, and model financials under each scenario.

</OPPORTUNITIES> </Report>"""

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

Create a report detailing the feasibility of the devleopment opportunities on this property, and who to contact to potentially buy the property. Do not use the first person, and format the promt as if it was being sent directly to the real estate developer.\
IMPORTANT: Withhold all predictions or suggestions about potential developments until the very end of the report. Include a section separated from the rest of the report wrapped in <PREDICTIONS> tags that details your predictions about the property. For example, here is how your output should be organized:

<Report>
<Analysis>
[ANALYSIS]
</ANALYSIS>
<OPPORTUNITIES>
[OPPORTUNITIES]
</OPPORTUNITIES>
</Report>
"""

GET_SIMILAR_DEVELOPMENT_PROMPT = """You are an expert real estate developer assistant. Given some information about a property, your goal is to find developments nearby that could be used as a reference for the development. 
The end goal for the real estate firm is to determine the financial feasibility of developing the property. In order to do this, you should find similar devlopments nearby and analyze the financials of those developments (if possible), in order to create a good understanding of the financials of the property we're analyzing.
Use your search tool to do extensive research online, and discover as much about the surrounding area and the new properties as possible. List out the recent developments in the area with as much detail as possible.

Here is some information about the property in Boston.

<PROPERTY_INFO>
[PROPERTY_INFO]
</PROPERTY_INFO>

Next to each of the developments, list the source you used to find the development.

Using the search tool, find similar developments nearby. Return only the report, and do not use the first person. Only list the developments, do not refer to your tools or thinking. 
"""
