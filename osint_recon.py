#!/usr/bin/env python3
"""
OSINT Reconnaissance Tool for Authorized Penetration Testing
Author: berry
Purpose: Legitimate security assessments with proper authorization
"""

import requests
import json
import re
import sys
import argparse
import time
from urllib.parse import quote
import phonenumbers
from phonenumbers import carrier, geocoder, timezone

class OSINTRecon:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
    def validate_phone_number(self, phone_number):
        """Validate and format phone number"""
        try:
            parsed_number = phonenumbers.parse(phone_number, None)
            if phonenumbers.is_valid_number(parsed_number):
                return phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
            else:
                return None
        except:
            return None

    def get_phone_basic_info(self, phone_number):
        """Get basic phone number information using phonenumbers library"""
        try:
            parsed_number = phonenumbers.parse(phone_number, None)
            info = {
                'valid': phonenumbers.is_valid_number(parsed_number),
                'country': geocoder.description_for_number(parsed_number, "en"),
                'carrier': carrier.name_for_number(parsed_number, "en"),
                'timezones': timezone.time_zones_for_number(parsed_number),
                'number_type': self._get_number_type(parsed_number)
            }
            return info
        except Exception as e:
            return {'error': str(e)}

    def _get_number_type(self, parsed_number):
        """Determine phone number type"""
        if phonenumbers.number_type(parsed_number) == phonenumbers.PhoneNumberType.MOBILE:
            return "Mobile"
        elif phonenumbers.number_type(parsed_number) == phonenumbers.PhoneNumberType.FIXED_LINE:
            return "Landline"
        else:
            return "Unknown"

    def search_social_media(self, phone_number, email=None):
        """Search for social media profiles using phone number"""
        results = {}
        
        # Search patterns for common social media platforms
        search_patterns = {
            'facebook': f'site:facebook.com "{phone_number}"',
            'linkedin': f'site:linkedin.com "{phone_number}"',
            'twitter': f'site:twitter.com "{phone_number}"',
            'instagram': f'site:instagram.com "{phone_number}"'
        }
        
        for platform, query in search_patterns.items():
            try:
                # This would typically use search APIs - placeholder for implementation
                results[platform] = f"Search query: {query}"
            except Exception as e:
                results[platform] = f"Error: {str(e)}"
                
        return results

    def check_data_breaches(self, phone_number, email=None):
        """Check if phone/email appears in known data breaches"""
        # Note: This would require integration with services like HaveIBeenPwned API
        # For demonstration purposes only
        return {
            'haveibeenpwned': 'API integration required',
            'breach_alerts': 'Check with authorized breach databases'
        }

    def reverse_phone_lookup(self, phone_number):
        """Perform reverse phone lookup using public APIs"""
        results = {}
        
        # Using Numverify API (requires free API key)
        try:
            # Note: You need to get a free API key from numverify.com
            api_key = "YOUR_NUMVERIFY_API_KEY"  # Replace with actual API key
            url = f"http://apilayer.net/api/validate?access_key={api_key}&number={phone_number}"
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('valid'):
                    results['numverify'] = {
                        'country': data.get('country_name'),
                        'location': data.get('location'),
                        'carrier': data.get('carrier'),
                        'line_type': data.get('line_type')
                    }
        except Exception as e:
            results['numverify'] = f"Error: {str(e)} or API key required"
            
        return results

    def search_public_records(self, phone_number):
        """Search public records and directories"""
        # This would integrate with public record APIs
        return {
            'public_records': 'Integration with public record services required',
            'business_directories': 'Check local business directories',
            'government_records': 'Access authorized government databases'
        }

    def email_from_phone(self, phone_number):
        """Attempt to find associated email addresses"""
        # This is speculative and requires proper authorization
        patterns = [
            f"{phone_number}@",  # Pattern for phone-based emails
            f"{phone_number.replace('+', '')}@"
        ]
        
        results = {}
        for pattern in patterns:
            results[f'pattern_{pattern}'] = f"Search for emails containing: {pattern}"
            
        return results

    def comprehensive_scan(self, phone_number, email=None):
        """Perform comprehensive OSINT scan"""
        print(f"[*] Starting comprehensive OSINT scan for: {phone_number}")
        if email:
            print(f"[*] Additional email target: {email}")
        
        results = {
            'target': phone_number,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'basic_info': self.get_phone_basic_info(phone_number),
            'reverse_lookup': self.reverse_phone_lookup(phone_number),
            'social_media': self.search_social_media(phone_number, email),
            'data_breaches': self.check_data_breaches(phone_number, email),
            'public_records': self.search_public_records(phone_number),
            'email_associations': self.email_from_phone(phone_number)
        }
        
        return results

    def generate_report(self, results, output_file=None):
        """Generate comprehensive report"""
        report = f"""
OSINT RECONNAISSANCE REPORT
===========================
Generated: {results['timestamp']}
Target: {results['target']}

BASIC INFORMATION:
------------------
Valid: {results['basic_info'].get('valid', 'N/A')}
Country: {results['basic_info'].get('country', 'N/A')}
Carrier: {results['basic_info'].get('carrier', 'N/A')}
Timezones: {', '.join(results['basic_info'].get('timezones', []))}
Type: {results['basic_info'].get('number_type', 'N/A')}

REVERSE LOOKUP:
---------------
{json.dumps(results['reverse_lookup'], indent=2)}

SOCIAL MEDIA SEARCH:
--------------------
{json.dumps(results['social_media'], indent=2)}

DATA BREACH CHECK:
------------------
{json.dumps(results['data_breaches'], indent=2)}

PUBLIC RECORDS:
---------------
{json.dumps(results['public_records'], indent=2)}

EMAIL ASSOCIATIONS:
-------------------
{json.dumps(results['email_associations'], indent=2)}

LEGAL DISCLAIMER:
-----------------
This tool is intended for authorized penetration testing and security research only.
Ensure you have proper authorization before using this tool.
Respect privacy laws and terms of service of all platforms.
        """
        
        print(report)
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(report)
            print(f"[+] Report saved to: {output_file}")

def main():
    parser = argparse.ArgumentParser(description='OSINT Reconnaissance Tool for Authorized Penetration Testing')
    parser.add_argument('phone', help='Phone number to investigate')
    parser.add_argument('-e', '--email', help='Associated email address (optional)')
    parser.add_argument('-o', '--output', help='Output file for report')
    parser.add_argument('--api-key', help='Numverify API key for enhanced lookup')
    
    args = parser.parse_args()
    
    # Legal disclaimer
    print("""
⚠️  LEGAL DISCLAIMER:
This tool is for AUTHORIZED penetration testing and security research ONLY.
Ensure you have explicit permission before using this tool.
Misuse of this tool may violate laws and regulations.
    """)
    
    confirm = input("Do you have proper authorization to proceed? (yes/no): ")
    if confirm.lower() != 'yes':
        print("Exiting. Only use with proper authorization.")
        sys.exit(1)
    
    recon = OSINTRecon()
    
    # Validate phone number
    validated_phone = recon.validate_phone_number(args.phone)
    if not validated_phone:
        print(f"[-] Invalid phone number: {args.phone}")
        sys.exit(1)
    
    print(f"[+] Validated phone number: {validated_phone}")
    
    # Perform comprehensive scan
    results = recon.comprehensive_scan(validated_phone, args.email)
    
    # Generate report
    recon.generate_report(results, args.output)

if __name__ == "__main__":
    main()
