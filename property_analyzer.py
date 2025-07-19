"""
Comprehensive property analyzer that combines parcel data and zoning information
for real estate development opportunity analysis.
"""

import json
from typing import Dict, Optional
from main import get_enhanced_parcel_data
from zoning_scraper import get_comprehensive_zoning_data
from address_data import geocode_address

def analyze_property_comprehensive(street_number: str, street_name: str, street_suffix: str = "", 
                                 unit_number: str = "", parcel_id: str = "") -> Dict:
    """
    Get comprehensive property analysis including parcel data, zoning, and development potential
    
    Args:
        street_number: Street number (e.g., "263")
        street_name: Street name (e.g., "N Harvard")  
        street_suffix: Street suffix (e.g., "St", "Ave") - optional
        unit_number: Unit number if applicable - optional
        parcel_id: Parcel ID if known - optional
    
    Returns:
        Comprehensive property analysis dictionary
    """
    
    # Construct full address
    address_parts = [street_number, street_name]
    if street_suffix:
        address_parts.append(street_suffix)
    full_address = " ".join(address_parts)
    if unit_number:
        full_address += f" Unit {unit_number}"
    
    print(f"Analyzing property: {full_address}")
    
    # Initialize comprehensive analysis structure
    analysis = {
        'property_summary': {
            'address': full_address,
            'parcel_id': parcel_id,
            'analysis_date': None,
            'coordinates': None
        },
        'parcel_data': {},
        'zoning_analysis': {},
        'development_assessment': {},
        'market_context': {},
        'regulatory_requirements': {},
        'development_opportunities': {},
        'risks_and_challenges': {},
        'recommendations': {}
    }
    
    try:
        # Get coordinates
        coordinates = geocode_address(full_address + ", Boston, MA")
        if coordinates:
            analysis['property_summary']['coordinates'] = {
                'latitude': coordinates[0],
                'longitude': coordinates[1]
            }
        
        # Get parcel data
        print("Fetching parcel data...")
        analysis['parcel_data'] = get_enhanced_parcel_data(
            parcel_id, street_number, street_name, street_suffix, unit_number
        )
        
        # Get zoning data
        print("Fetching zoning data...")
        analysis['zoning_analysis'] = get_comprehensive_zoning_data(full_address + ", Boston, MA")
        
        # Perform development assessment
        analysis['development_assessment'] = assess_development_potential(
            analysis['parcel_data'], 
            analysis['zoning_analysis']
        )
        
        # Analyze market context
        analysis['market_context'] = analyze_market_context(analysis)
        
        # Identify regulatory requirements
        analysis['regulatory_requirements'] = identify_regulatory_requirements(analysis)
        
        # Identify development opportunities
        analysis['development_opportunities'] = identify_development_opportunities(analysis)
        
        # Assess risks and challenges
        analysis['risks_and_challenges'] = assess_risks_and_challenges(analysis)
        
        # Generate recommendations
        analysis['recommendations'] = generate_recommendations(analysis)
        
    except Exception as e:
        print(f"Error in comprehensive analysis: {e}")
        analysis['error'] = str(e)
    
    return analysis

def assess_development_potential(parcel_data: Dict, zoning_analysis: Dict) -> Dict:
    """Assess development potential based on parcel and zoning data"""
    
    assessment = {
        'development_feasibility': 'Medium',  # Low/Medium/High
        'upzoning_potential': 'Unknown',
        'density_increase_possible': False,
        'current_utilization': 'Unknown',
        'expansion_options': [],
        'zoning_compliance': 'Unknown',
        'variances_needed': [],
        'development_timeline': '18-36 months'
    }
    
    try:
        # Calculate current utilization
        lot_size_str = parcel_data.get('lot_size', '0')
        living_area_str = parcel_data.get('living_area', '0')
        
        # Extract numeric values (basic parsing)
        lot_size = extract_numeric_value(lot_size_str) if lot_size_str else 0
        living_area = extract_numeric_value(living_area_str) if living_area_str else 0
        
        if lot_size > 0 and living_area > 0:
            current_far = living_area / lot_size
            assessment['current_utilization'] = f"FAR: {current_far:.2f}"
            
            # Check against zoning FAR limits
            zoning_req = zoning_analysis.get('zoning_requirements', {})
            max_far_str = zoning_req.get('max_far', '0')
            max_far = extract_numeric_value(max_far_str) if max_far_str else 0
            
            if max_far > current_far:
                assessment['density_increase_possible'] = True
                assessment['expansion_options'].append(f"Can increase FAR by {max_far - current_far:.2f}")
        
        # Analyze zoning district (with null checks)
        zoning_district = zoning_analysis.get('zoning_info', {}).get('zoning_district')
        if zoning_district and isinstance(zoning_district, str):
            if zoning_district.startswith('R-'):
                assessment['development_feasibility'] = 'Medium'
                assessment['expansion_options'].append('Residential intensification possible')
            elif zoning_district.startswith('B-'):
                assessment['development_feasibility'] = 'High'
                assessment['expansion_options'].append('Commercial/mixed-use development possible')
        
        # Check for development complexity factors
        planning_context = zoning_analysis.get('planning_context', {})
        if planning_context.get('historic_district'):
            assessment['variances_needed'].append('Historic district approval')
            assessment['development_timeline'] = '24-48 months'
        
        if planning_context.get('article_25a_overlay'):
            assessment['variances_needed'].append('Coastal flood resilience review')
            
    except Exception as e:
        print(f"Error in development assessment: {e}")
        assessment['error'] = str(e)
    
    return assessment

def analyze_market_context(analysis: Dict) -> Dict:
    """Analyze market context for development"""
    
    context = {
        'neighborhood': 'Unknown',
        'market_trends': [],
        'comparable_developments': [],
        'transit_accessibility': 'Unknown',
        'walkability_score': 'Unknown',
        'demographic_trends': {},
        'economic_indicators': {}
    }
    
    try:
        # Extract neighborhood from address and parcel data
        address = analysis['property_summary']['address'].upper()
        parcel_data = analysis.get('parcel_data', {})
        full_address = parcel_data.get('address', '').upper()
        
        # Get coordinates for more precise neighborhood detection
        coordinates = analysis.get('property_summary', {}).get('coordinates', {})
        lat = coordinates.get('latitude')
        lon = coordinates.get('longitude')
        
        # Neighborhood detection based on address patterns and coordinates
        neighborhood_info = detect_boston_neighborhood(address, full_address, lat, lon)
        context.update(neighborhood_info)
        
        # Add context based on property value
        total_value = parcel_data.get('fy2025_total_value', '')
        if total_value and '$' in total_value:
            value = extract_numeric_value(total_value)
            if value > 1500000:
                context['market_trends'].append('High-value market segment')
                context['economic_indicators']['property_value_tier'] = 'Premium'
            elif value > 1000000:
                context['economic_indicators']['property_value_tier'] = 'Above-average'
            else:
                context['economic_indicators']['property_value_tier'] = 'Average'
                
        # Add property age context
        year_built = parcel_data.get('year_built', '')
        if year_built and year_built.isdigit():
            age = 2025 - int(year_built)
            if age > 100:
                context['market_trends'].append('Historic property potential')
                context['economic_indicators']['property_age'] = 'Historic (100+ years)'
            elif age > 50:
                context['economic_indicators']['property_age'] = 'Mature (50+ years)'
            else:
                context['economic_indicators']['property_age'] = 'Modern'
        
        # Check zoning analysis for additional transit context
        zoning_analysis = analysis.get('zoning_analysis', {})
        planning_context = zoning_analysis.get('planning_context', {})
        
        if planning_context.get('transit_oriented'):
            context['transit_accessibility'] = 'High'
            if 'TOD bonus potential' not in context['market_trends']:
                context['market_trends'].append('TOD bonus potential')
        
    except Exception as e:
        print(f"Error in market context analysis: {e}")
        context['error'] = str(e)
    
    return context

def detect_boston_neighborhood(address: str, full_address: str, lat: float = None, lon: float = None) -> Dict:
    """Detect Boston neighborhood and provide market context"""
    
    neighborhood_data = {
        'neighborhood': 'Unknown',
        'market_trends': [],
        'transit_accessibility': 'Unknown',
        'walkability_score': 'Unknown'
    }
    
    # Combine address strings for analysis
    combined_address = f"{address} {full_address}".upper()
    
    # Allston/Brighton
    if any(word in combined_address for word in ['HARVARD', 'ALLSTON', 'BRIGHTON']):
        if 'HARVARD' in combined_address:
            neighborhood_data.update({
                'neighborhood': 'Allston',
                'market_trends': [
                    'Student housing demand from nearby universities',
                    'Young professional influx', 
                    'Transit-oriented development interest',
                    'Gentrification pressure increasing property values',
                    'Two-family home conversion opportunities'
                ],
                'transit_accessibility': 'Good - Green Line B accessible',
                'walkability_score': 'High - Urban neighborhood'
            })
        else:
            neighborhood_data.update({
                'neighborhood': 'Brighton',
                'market_trends': [
                    'Family-oriented development',
                    'Green Line accessibility',
                    'Suburban feel with urban amenities'
                ],
                'transit_accessibility': 'Good - Green Line access',
                'walkability_score': 'Moderate to High'
            })
    
    # Back Bay
    elif any(word in combined_address for word in ['BOYLSTON', 'NEWBURY', 'MARLBOROUGH', 'BEACON', 'COMMONWEALTH']):
        neighborhood_data.update({
            'neighborhood': 'Back Bay',
            'market_trends': [
                'Luxury residential market',
                'Historic brownstone conversions',
                'High-end retail and dining',
                'Premium real estate values'
            ],
            'transit_accessibility': 'Excellent - Multiple Green Line stations',
            'walkability_score': 'Very High - Walker\'s Paradise'
        })
    
    # South End
    elif any(word in combined_address for word in ['WASHINGTON ST', 'TREMONT', 'HARRISON', 'SHAWMUT']) and lat and 42.33 <= lat <= 42.35:
        neighborhood_data.update({
            'neighborhood': 'South End',
            'market_trends': [
                'Victorian architecture premium',
                'LGBTQ+ friendly community',
                'Restaurant and nightlife hub',
                'Luxury condo conversions'
            ],
            'transit_accessibility': 'Excellent - Orange Line access',
            'walkability_score': 'Very High'
        })
    
    # North End
    elif any(word in combined_address for word in ['HANOVER', 'SALEM', 'PRINCE', 'NORTH END']):
        neighborhood_data.update({
            'neighborhood': 'North End',
            'market_trends': [
                'Italian heritage tourism',
                'Historic preservation requirements',
                'Dense residential development',
                'Waterfront proximity premium'
            ],
            'transit_accessibility': 'Good - Walking distance to downtown',
            'walkability_score': 'Very High'
        })
    
    # Cambridge Street Corridor
    elif 'CAMBRIDGE' in combined_address and any(word in combined_address for word in ['STREET', 'ST']):
        neighborhood_data.update({
            'neighborhood': 'West End',
            'market_trends': [
                'Medical district proximity',
                'Mixed-use development opportunities',
                'Transit-oriented development'
            ],
            'transit_accessibility': 'Excellent - Red/Green Line access',
            'walkability_score': 'High'
        })
    
    # Dorchester
    elif any(word in combined_address for word in ['DORCHESTER', 'BLUE HILL', 'COLUMBIA', 'UPHAMS']):
        neighborhood_data.update({
            'neighborhood': 'Dorchester',
            'market_trends': [
                'Affordable housing development',
                'Diverse immigrant communities',
                'Transit expansion benefits',
                'Gentrification concerns'
            ],
            'transit_accessibility': 'Good - Red Line access',
            'walkability_score': 'Moderate'
        })
    
    # Jamaica Plain
    elif any(word in combined_address for word in ['JAMAICA', 'CENTRE ST', 'SOUTH ST']) and 'PLAIN' in combined_address:
        neighborhood_data.update({
            'neighborhood': 'Jamaica Plain',
            'market_trends': [
                'Arts and culture district',
                'Craft brewing and dining scene',
                'Transit-oriented development',
                'Mixed-income housing initiatives'
            ],
            'transit_accessibility': 'Excellent - Orange Line access',
            'walkability_score': 'High'
        })
    
    # Roxbury
    elif any(word in combined_address for word in ['ROXBURY', 'DUDLEY', 'MALCOLM X']):
        neighborhood_data.update({
            'neighborhood': 'Roxbury',
            'market_trends': [
                'Urban renewal and redevelopment',
                'Community-focused development',
                'Affordable housing priorities',
                'Cultural and historic preservation'
            ],
            'transit_accessibility': 'Good - Orange Line access',
            'walkability_score': 'Moderate'
        })
    
    # Somerville (technically not Boston but often included)
    elif any(word in combined_address for word in ['SOMERVILLE', 'DAVIS', 'PORTER']):
        neighborhood_data.update({
            'neighborhood': 'Somerville',
            'market_trends': [
                'Young professional demographic',
                'Tech industry growth',
                'Dense residential development',
                'Green Line extension benefits'
            ],
            'transit_accessibility': 'Excellent - Red Line access',
            'walkability_score': 'Very High'
        })
    
    # Use coordinate-based detection if address-based failed
    if neighborhood_data['neighborhood'] == 'Unknown' and lat and lon:
        coord_neighborhood = detect_neighborhood_by_coordinates(lat, lon)
        if coord_neighborhood:
            neighborhood_data.update(coord_neighborhood)
    
    return neighborhood_data

def detect_neighborhood_by_coordinates(lat: float, lon: float) -> Dict:
    """Detect neighborhood based on coordinates as fallback"""
    
    # Allston/Brighton area
    if 42.34 <= lat <= 42.37 and -71.15 <= lon <= -71.11:
        return {
            'neighborhood': 'Allston/Brighton',
            'market_trends': ['Student housing market', 'Transit accessibility'],
            'transit_accessibility': 'Good - Green Line',
            'walkability_score': 'High'
        }
    
    # Back Bay/South End
    elif 42.34 <= lat <= 42.36 and -71.09 <= lon <= -71.06:
        return {
            'neighborhood': 'Back Bay/South End',
            'market_trends': ['Luxury market', 'Historic properties'],
            'transit_accessibility': 'Excellent - Multiple lines',
            'walkability_score': 'Very High'
        }
    
    # Downtown/Financial District  
    elif 42.35 <= lat <= 42.36 and -71.06 <= lon <= -71.05:
        return {
            'neighborhood': 'Downtown',
            'market_trends': ['Commercial development', 'Mixed-use opportunities'],
            'transit_accessibility': 'Excellent - Transit hub',
            'walkability_score': 'Very High'
        }
    
    # Dorchester
    elif 42.28 <= lat <= 42.32 and -71.10 <= lon <= -71.05:
        return {
            'neighborhood': 'Dorchester',
            'market_trends': ['Affordable housing', 'Community development'],
            'transit_accessibility': 'Good - Red Line',
            'walkability_score': 'Moderate'
        }
    
    # Jamaica Plain
    elif 42.30 <= lat <= 42.33 and -71.12 <= lon <= -71.10:
        return {
            'neighborhood': 'Jamaica Plain',
            'market_trends': ['Arts district', 'Mixed-income development'],
            'transit_accessibility': 'Excellent - Orange Line',
            'walkability_score': 'High'
        }
    
    return None

def identify_regulatory_requirements(analysis: Dict) -> Dict:
    """Identify regulatory requirements for development"""
    
    requirements = {
        'article_80_review': False,
        'affordable_housing_req': 'Unknown',
        'article_37_green_building': False,
        'article_25a_flood_resilience': False,
        'parking_requirements': 'Unknown',
        'historic_review': False,
        'environmental_review': [],
        'community_process': 'Standard',
        'estimated_approval_time': '6-18 months'
    }
    
    try:
        parcel_data = analysis.get('parcel_data', {})
        zoning_analysis = analysis.get('zoning_analysis', {})
        planning_context = zoning_analysis.get('planning_context', {})
        
        # Check for Article 80 requirement (>20,000 sq ft typically)
        living_area = extract_numeric_value(parcel_data.get('living_area', '0'))
        if living_area > 20000:
            requirements['article_80_review'] = True
            requirements['estimated_approval_time'] = '12-24 months'
            requirements['community_process'] = 'Enhanced'
        
        # Check for special overlays
        if planning_context.get('article_25a_overlay'):
            requirements['article_25a_flood_resilience'] = True
            requirements['environmental_review'].append('Coastal flood resilience')
        
        if planning_context.get('historic_district'):
            requirements['historic_review'] = True
            requirements['estimated_approval_time'] = '18-30 months'
        
        # Affordable housing typically required for residential projects >10 units
        property_type = parcel_data.get('property_type', '')
        if property_type and isinstance(property_type, str) and ('family' in property_type.lower() or 'residential' in property_type.lower()):
            requirements['affordable_housing_req'] = 'Likely if >10 units'
        
    except Exception as e:
        print(f"Error identifying regulatory requirements: {e}")
        requirements['error'] = str(e)
    
    return requirements

def identify_development_opportunities(analysis: Dict) -> Dict:
    """Identify specific development opportunities"""
    
    opportunities = {
        'primary_opportunities': [],
        'secondary_opportunities': [],
        'financial_potential': 'Medium',
        'development_scenarios': [],
        'market_positioning': [],
        'value_creation_strategies': []
    }
    
    try:
        parcel_data = analysis.get('parcel_data', {})
        zoning_analysis = analysis.get('zoning_analysis', {})
        development_assessment = analysis.get('development_assessment', {})
        
        # Analyze based on current property characteristics
        lot_size = extract_numeric_value(parcel_data.get('lot_size', '0')) if parcel_data.get('lot_size') else 0
        year_built = parcel_data.get('year_built', '')
        
        if year_built and isinstance(year_built, str) and year_built.isdigit() and int(year_built) < 1950:
            opportunities['primary_opportunities'].append('Historic renovation/adaptive reuse')
            opportunities['value_creation_strategies'].append('Historic tax credits potential')
        
        if lot_size > 5000:  # Larger lots have more development potential
            opportunities['primary_opportunities'].append('Density increase/additional units')
            opportunities['development_scenarios'].append('Multi-family development')
        
        # Analyze zoning opportunities
        zoning_district = zoning_analysis.get('zoning_info', {}).get('zoning_district', '')
        if zoning_district and isinstance(zoning_district, str) and 'B-' in zoning_district:  # Commercial zoning
            opportunities['primary_opportunities'].append('Mixed-use development')
            opportunities['development_scenarios'].append('Ground-floor retail + residential')
            opportunities['financial_potential'] = 'High'
        
        if development_assessment.get('density_increase_possible'):
            opportunities['primary_opportunities'].append('FAR optimization')
        
        # Transit-oriented opportunities
        planning_context = zoning_analysis.get('planning_context', {})
        if planning_context.get('transit_oriented'):
            opportunities['secondary_opportunities'].append('Transit-oriented density bonus')
            opportunities['market_positioning'].append('Transit-accessible luxury housing')
        
        # If we have property value data, assess financial potential
        total_value_str = parcel_data.get('fy2025_total_value', '')
        if total_value_str and isinstance(total_value_str, str) and '$' in total_value_str:
            value = extract_numeric_value(total_value_str)
            if value > 1000000:
                opportunities['financial_potential'] = 'High'
                opportunities['value_creation_strategies'].append('High-value property with development potential')
        
    except Exception as e:
        print(f"Error identifying opportunities: {e}")
        opportunities['error'] = str(e)
    
    return opportunities

def assess_risks_and_challenges(analysis: Dict) -> Dict:
    """Assess development risks and challenges"""
    
    risks = {
        'regulatory_risks': [],
        'market_risks': [],
        'financial_risks': [],
        'technical_challenges': [],
        'timeline_risks': [],
        'overall_risk_level': 'Medium'
    }
    
    try:
        regulatory_req = analysis.get('regulatory_requirements', {})
        planning_context = analysis.get('zoning_analysis', {}).get('planning_context', {})
        
        # Regulatory risks
        if regulatory_req.get('article_80_review'):
            risks['regulatory_risks'].append('Complex Article 80 review process')
            risks['timeline_risks'].append('Extended approval timeline (12-24 months)')
        
        if regulatory_req.get('historic_review'):
            risks['regulatory_risks'].append('Historic preservation restrictions')
            risks['technical_challenges'].append('Historic renovation complexity')
        
        if planning_context.get('article_25a_overlay'):
            risks['technical_challenges'].append('Flood resilience engineering requirements')
            risks['financial_risks'].append('Increased construction costs for resilience')
        
        # Market risks
        neighborhood = analysis.get('market_context', {}).get('neighborhood', '')
        if neighborhood == 'Allston':
            risks['market_risks'].append('Student housing market volatility')
        
        # Financial risks
        parcel_data = analysis.get('parcel_data', {})
        total_value = parcel_data.get('fy2025_total_value', '')
        if total_value and isinstance(total_value, str) and extract_numeric_value(total_value) > 1000000:
            risks['financial_risks'].append('High acquisition cost basis')
        
        # Add risk if no zoning data available
        zoning_info = analysis.get('zoning_analysis', {}).get('zoning_info', {})
        if not zoning_info.get('zoning_district'):
            risks['regulatory_risks'].append('Limited zoning information available - requires detailed analysis')
        
        # Calculate overall risk
        total_risks = (len(risks['regulatory_risks']) + len(risks['market_risks']) + 
                      len(risks['financial_risks']) + len(risks['technical_challenges']))
        
        if total_risks <= 2:
            risks['overall_risk_level'] = 'Low'
        elif total_risks >= 5:
            risks['overall_risk_level'] = 'High'
        
    except Exception as e:
        print(f"Error assessing risks: {e}")
        risks['error'] = str(e)
    
    return risks

def generate_recommendations(analysis: Dict) -> Dict:
    """Generate development recommendations based on comprehensive analysis"""
    
    recommendations = {
        'recommended_strategy': 'Hold and Monitor',
        'next_steps': [],
        'timeline_recommendation': 'Medium-term (2-5 years)',
        'key_considerations': [],
        'professional_consultations': [],
        'financial_structuring': [],
        'risk_mitigation': []
    }
    
    try:
        opportunities = analysis.get('development_opportunities', {})
        risks = analysis.get('risks_and_challenges', {})
        development_assessment = analysis.get('development_assessment', {})
        
        # Determine primary strategy based on feasibility and risks
        if (development_assessment.get('development_feasibility') == 'High' and 
            risks.get('overall_risk_level') in ['Low', 'Medium']):
            recommendations['recommended_strategy'] = 'Pursue Development'
            recommendations['timeline_recommendation'] = 'Near-term (1-3 years)'
            recommendations['next_steps'].extend([
                'Conduct detailed feasibility study',
                'Engage with planning department',
                'Secure development financing'
            ])
        
        elif len(opportunities.get('primary_opportunities', [])) > 0:
            recommendations['recommended_strategy'] = 'Strategic Development'
            recommendations['next_steps'].extend([
                'Detailed zoning analysis',
                'Market study',
                'Preliminary design development'
            ])
        
        # Professional consultations
        if analysis.get('regulatory_requirements', {}).get('historic_review'):
            recommendations['professional_consultations'].append('Historic preservation specialist')
        
        if analysis.get('regulatory_requirements', {}).get('article_80_review'):
            recommendations['professional_consultations'].extend([
                'Land use attorney',
                'Community engagement specialist'
            ])
        
        # Risk mitigation
        for risk_category in ['regulatory_risks', 'market_risks', 'financial_risks']:
            risk_list = risks.get(risk_category, [])
            if risk_list:
                recommendations['risk_mitigation'].extend([
                    f"Address {risk_category.replace('_', ' ')}: {', '.join(risk_list[:2])}"
                ])
        
        # Key considerations
        recommendations['key_considerations'].extend([
            'Monitor zoning changes and planning initiatives',
            'Track comparable development projects',
            'Maintain relationships with local planning officials'
        ])
        
    except Exception as e:
        print(f"Error generating recommendations: {e}")
        recommendations['error'] = str(e)
    
    return recommendations

def extract_numeric_value(text_value: str) -> float:
    """Extract numeric value from text (e.g., '5,000 sq ft' -> 5000)"""
    if not text_value or not isinstance(text_value, str):
        return 0.0
    
    try:
        # Remove common non-numeric characters and extract number
        import re
        numeric_match = re.search(r'[\d,]+\.?\d*', text_value.replace(',', ''))
        if numeric_match:
            return float(numeric_match.group())
    except:
        pass
    
    return 0.0

def format_analysis_for_llm(analysis: Dict) -> str:
    """Format the comprehensive analysis for LLM consumption"""
    
    formatted = f"""## Property Analysis Report

### Property Summary
- **Address**: {analysis['property_summary']['address']}
- **Parcel ID**: {analysis['property_summary']['parcel_id']}

### Current Property Details
- **Lot Size**: {analysis['parcel_data'].get('lot_size', 'Unknown')}
- **Living Area**: {analysis['parcel_data'].get('living_area', 'Unknown')}
- **Year Built**: {analysis['parcel_data'].get('year_built', 'Unknown')}
- **Property Type**: {analysis['parcel_data'].get('property_type', 'Unknown')}
- **Owner**: {analysis['parcel_data'].get('owner', 'Unknown')}
- **FY2025 Total Value**: {analysis['parcel_data'].get('fy2025_total_value', 'Unknown')}

### Zoning Information
- **Zoning District**: {analysis['zoning_analysis'].get('zoning_info', {}).get('zoning_district', 'Unknown')}
- **Height Limit**: {analysis['zoning_analysis'].get('zoning_requirements', {}).get('max_height', 'Unknown')}
- **FAR Limit**: {analysis['zoning_analysis'].get('zoning_requirements', {}).get('max_far', 'Unknown')}
- **Allowed Uses**: {', '.join(analysis['zoning_analysis'].get('zoning_requirements', {}).get('allowed_uses', []))}

### Development Assessment
- **Development Feasibility**: {analysis['development_assessment'].get('development_feasibility', 'Unknown')}
- **Current Utilization**: {analysis['development_assessment'].get('current_utilization', 'Unknown')}
- **Density Increase Possible**: {analysis['development_assessment'].get('density_increase_possible', 'Unknown')}
- **Timeline**: {analysis['development_assessment'].get('development_timeline', 'Unknown')}

### Market Context
- **Neighborhood**: {analysis['market_context'].get('neighborhood', 'Unknown')}
- **Market Trends**: {', '.join(analysis['market_context'].get('market_trends', []))}
- **Transit Accessibility**: {analysis['market_context'].get('transit_accessibility', 'Unknown')}

### Development Opportunities
- **Primary Opportunities**: {', '.join(analysis['development_opportunities'].get('primary_opportunities', []))}
- **Development Scenarios**: {', '.join(analysis['development_opportunities'].get('development_scenarios', []))}
- **Financial Potential**: {analysis['development_opportunities'].get('financial_potential', 'Unknown')}

### Regulatory Requirements
- **Article 80 Review**: {analysis['regulatory_requirements'].get('article_80_review', 'Unknown')}
- **Affordable Housing Req**: {analysis['regulatory_requirements'].get('affordable_housing_req', 'Unknown')}
- **Historic Review**: {analysis['regulatory_requirements'].get('historic_review', 'Unknown')}
- **Approval Timeline**: {analysis['regulatory_requirements'].get('estimated_approval_time', 'Unknown')}

### Risks and Challenges
- **Overall Risk Level**: {analysis['risks_and_challenges'].get('overall_risk_level', 'Unknown')}
- **Regulatory Risks**: {', '.join(analysis['risks_and_challenges'].get('regulatory_risks', []))}
- **Market Risks**: {', '.join(analysis['risks_and_challenges'].get('market_risks', []))}

### Recommendations
- **Recommended Strategy**: {analysis['recommendations'].get('recommended_strategy', 'Unknown')}
- **Timeline**: {analysis['recommendations'].get('timeline_recommendation', 'Unknown')}
- **Next Steps**: {', '.join(analysis['recommendations'].get('next_steps', []))}
"""
    
    return formatted

if __name__ == "__main__":
    # Test the property analyzer with different neighborhoods
    test_addresses = [
        ("263", "N Harvard", "St", "", ""),  # Allston - original test
        ("100", "BOYLSTON", "ST", "", ""),   # Back Bay - commercial
        ("123", "Centre", "St", "", "")      # Jamaica Plain - residential
    ]
    
    for i, (num, street, suffix, unit, _) in enumerate(test_addresses):
        address = f"{num} {street} {suffix}"
        print(f"\n{'='*60}")
        print(f"TEST {i+1}: Analyzing property: {address}")
        print('='*60)
        
        analysis = analyze_property_comprehensive(num, street, suffix, unit, "")
        
        # Print key results
        neighborhood = analysis.get('market_context', {}).get('neighborhood', 'Unknown')
        zoning = analysis.get('zoning_analysis', {}).get('zoning_info', {}).get('zoning_district', 'Unknown')
        value = analysis.get('parcel_data', {}).get('fy2025_total_value', 'Unknown')
        
        print(f"Neighborhood: {neighborhood}")
        print(f"Zoning: {zoning}")  
        print(f"Value: {value}")
        
        if i == 0:  # Only full report for first address
            report = format_analysis_for_llm(analysis)
            print("\nFull Report:")
            print(report)
            
            # Save detailed analysis
            with open('sample_property_analysis.json', 'w') as f:
                json.dump(analysis, f, indent=2) 