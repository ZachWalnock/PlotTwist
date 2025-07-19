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
        lot_size = extract_numeric_value(lot_size_str)
        living_area = extract_numeric_value(living_area_str)
        
        if lot_size > 0 and living_area > 0:
            current_far = living_area / lot_size
            assessment['current_utilization'] = f"FAR: {current_far:.2f}"
            
            # Check against zoning FAR limits
            zoning_req = zoning_analysis.get('zoning_requirements', {})
            max_far_str = zoning_req.get('max_far', '0')
            max_far = extract_numeric_value(max_far_str)
            
            if max_far > current_far:
                assessment['density_increase_possible'] = True
                assessment['expansion_options'].append(f"Can increase FAR by {max_far - current_far:.2f}")
        
        # Analyze zoning district
        zoning_district = zoning_analysis.get('zoning_info', {}).get('zoning_district')
        if zoning_district:
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
        # Extract neighborhood from address
        address = analysis['property_summary']['address']
        if 'Allston' in address:
            context['neighborhood'] = 'Allston'
            context['market_trends'] = [
                'Student housing demand',
                'Young professional influx',
                'Transit-oriented development interest'
            ]
        elif 'Brighton' in address:
            context['neighborhood'] = 'Brighton'
            context['market_trends'] = [
                'Family-oriented development',
                'Green Line accessibility'
            ]
        
        # Check zoning analysis for transit info
        zoning_analysis = analysis.get('zoning_analysis', {})
        planning_context = zoning_analysis.get('planning_context', {})
        
        if planning_context.get('transit_oriented'):
            context['transit_accessibility'] = 'High'
            context['market_trends'].append('TOD bonus potential')
        
    except Exception as e:
        print(f"Error in market context analysis: {e}")
        context['error'] = str(e)
    
    return context

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
        property_type = parcel_data.get('property_type', '').lower()
        if 'family' in property_type or 'residential' in property_type:
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
        lot_size = extract_numeric_value(parcel_data.get('lot_size', '0'))
        year_built = parcel_data.get('year_built', '')
        
        if year_built and year_built.isdigit() and int(year_built) < 1950:
            opportunities['primary_opportunities'].append('Historic renovation/adaptive reuse')
            opportunities['value_creation_strategies'].append('Historic tax credits potential')
        
        if lot_size > 5000:  # Larger lots have more development potential
            opportunities['primary_opportunities'].append('Density increase/additional units')
            opportunities['development_scenarios'].append('Multi-family development')
        
        # Analyze zoning opportunities
        zoning_district = zoning_analysis.get('zoning_info', {}).get('zoning_district', '')
        if 'B-' in zoning_district:  # Commercial zoning
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
        if total_value and extract_numeric_value(total_value) > 1000000:
            risks['financial_risks'].append('High acquisition cost basis')
        
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
    # Test comprehensive analysis
    test_analysis = analyze_property_comprehensive("263", "N Harvard", "St", "", "")
    
    # Print formatted analysis
    formatted_output = format_analysis_for_llm(test_analysis)
    print(formatted_output)
    
    # Save detailed analysis to file
    with open('sample_property_analysis.json', 'w') as f:
        json.dump(test_analysis, f, indent=2) 