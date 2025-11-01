#!/usr/bin/env python3
"""
Enhanced OSINT Reconnaissance Tool with Social Media & Email Discovery
Author: HackerAI Assistant
Purpose: Legitimate security assessments with proper authorization
"""

import requests
import json
import re
import sys
import argparse
import time
import urllib.parse
from urllib.parse import quote, urlencode
import phonenumbers
from phonenumbers import carrier, geocoder, timezone
import concurrent.futures

class EnhancedOSINTRecon:
    def __init__(self, api_key=None):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.numverify_api_key = api_key
        
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

    def get_enhanced_phone_info(self, phone_number):
        """Get comprehensive phone information"""
        try:
            parsed_number = phonenumbers.parse(phone_number, None)
            info = {
                'valid': phonenumbers.is_valid_number(parsed_number),
                'country': geocoder.description_for_number(parsed_number, "en"),
                'carrier': carrier.name_for_number(parsed_number, "en"),
                'timezones': timezone.time_zones_for_number(parsed_number),
                'number_type': self._get_number_type(parsed_number),
                'national_format': phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.NATIONAL),
                'international_format': phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL),
                'e164_format': phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
            }
            return info
        except Exception as e:
            return {'error': str(e)}

    def _get_number_type(self, parsed_number):
        """Determine phone number type"""
        number_type = phonenumbers.number_type(parsed_number)
        if number_type == phonenumbers.PhoneNumberType.MOBILE:
            return "Mobile"
        elif number_type == phonenumbers.PhoneNumberType.FIXED_LINE:
            return "Landline"
        elif number_type == phonenumbers.PhoneNumberType.VOIP:
            return "VOIP"
        else:
            return "Unknown"

    def enhanced_reverse_phone_lookup(self, phone_number):
        """Perform enhanced reverse phone lookup using Numverify API"""
        results = {}
        
        if self.numverify_api_key:
            try:
                url = f"http://apilayer.net/api/validate?access_key={self.numverify_api_key}&number={phone_number}"
                response = self.session.get(url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('valid'):
                        results['numverify'] = data
                    else:
                        results['numverify'] = {'error': 'Invalid number according to Numverify'}
                else:
                    results['numverify'] = {'error': f'API request failed with status {response.status_code}'}
            except Exception as e:
                results['numverify'] = {'error': str(e)}
        else:
            results['numverify'] = {'error': 'No API key provided'}
            
        return results

    def search_social_media_profiles(self, phone_number, email=None):
        """Search for social media profiles using phone number and email"""
        results = {}
        clean_number = phone_number.replace('+', '').replace(' ', '')
        
        # Social media search URLs with phone number
        social_media_searches = {
            'Facebook': f'https://www.facebook.com/login/identify?ctx=recover&phone={clean_number}',
            'Facebook Search': f'https://www.facebook.com/public?query={clean_number}',
            'LinkedIn': f'https://www.linkedin.com/search/results/all/?keywords={clean_number}',
            'Twitter': f'https://twitter.com/search?q={clean_number}&src=typed_query',
            'Instagram': f'https://www.instagram.com/accounts/account_recovery/?phone_number={clean_number}',
            'WhatsApp': f'https://wa.me/{clean_number}',
            'Telegram': f'https://t.me/{clean_number}',
            'Truecaller': f'https://www.truecaller.com/search/in/{clean_number[2:]}',  # Remove country code
            'Signal': 'https://signal.org/ (Check if number is registered)',
            'Snapchat': f'https://accounts.snapchat.com/accounts/login?continue=%2Faccounts%2Fwelcome?phone_number=%2B{clean_number}'
        }
        
        # Email-based searches if email provided
        if email:
            email_searches = {
                'Facebook Email': f'https://www.facebook.com/login/identify?ctx=recover&email={email}',
                'LinkedIn Email': f'https://www.linkedin.com/search/results/all/?keywords={email}',
                'Twitter Email': f'https://twitter.com/search?q={email}&src=typed_query',
                'Instagram Email': f'https://www.instagram.com/accounts/account_recovery/?email={email}',
                'Have I Been Pwned': f'https://haveibeenpwned.com/account/{email}',
                'Google Search': f'https://www.google.com/search?q="{email}"',
                'Gravatar': f'https://en.gravatar.com/{email}'
            }
            social_media_searches.update(email_searches)
        
        results['search_urls'] = social_media_searches
        return results

    def generate_email_patterns(self, phone_number, name_variations=None):
        """Generate potential email patterns based on phone number"""
        clean_number = phone_number.replace('+', '').replace(' ', '')
        short_number = clean_number[2:] if clean_number.startswith('91') else clean_number  # Remove country code
        
        email_patterns = {}
        
        # Common email providers
        providers = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'rediffmail.com', 'icloud.com']
        
        # Phone-based email patterns
        for provider in providers:
            email_patterns[f'full_phone_{provider}'] = f'{clean_number}@{provider}'
            email_patterns[f'short_phone_{provider}'] = f'{short_number}@{provider}'
            email_patterns[f'phone91_{provider}'] = f'91{short_number}@{provider}'
        
        # Common Indian email patterns
        indian_patterns = {
            'jio_pattern': f'{short_number}@jio.com',
            'airtel_pattern': f'{short_number}@airtel.com',
            'vodafone_pattern': f'{short_number}@vodafone.com'
        }
        email_patterns.update(indian_patterns)
        
        return email_patterns

    def search_public_databases(self, phone_number):
        """Search public databases and directories"""
        clean_number = phone_number.replace('+91', '')
        
        databases = {
            'IndiaTrace': f'https://www.indiatrace.com/trace-mobile-number-location/trace-mobile-number.php?number={clean_number}',
            'BharatiyaMobile': f'https://trace.bharatiyamobile.com/?numb={clean_number}',
            'Truecaller Web': f'https://www.truecaller.com/search/in/{clean_number}',
            'NumberGuru': f'https://www.numberguru.com/phone/{clean_number}',
            'SpyDialer': f'https://www.spydialer.com/default.aspx?phone={clean_number}',
            'SyncMe': f'https://sync.me/search/?number={clean_number}',
            'Whitepages': f'https://www.whitepages.com/phone/{clean_number}',
            'ZabaSearch': f'https://www.zabasearch.com/phone/{clean_number}'
        }
        
        return databases

    def check_data_breaches(self, email=None, phone_number=None):
        """Check data breaches using public APIs"""
        breach_results = {}
        
        if email:
            try:
                # Have I Been Pwned API (email)
                url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}"
                headers = {'User-Agent': 'OSINT-Recon-Tool'}
                response = self.session.get(url, headers=headers, timeout=10)
                if response.status_code == 200:
                    breach_results['email_breaches'] = response.json()
                elif response.status_code == 404:
                    breach_results['email_breaches'] = 'No breaches found for this email'
                else:
                    breach_results['email_breaches'] = f'API error: {response.status_code}'
            except Exception as e:
                breach_results['email_breaches'] = f'Error: {str(e)}'
        
        # Phone number breach checking (limited availability)
        if phone_number:
            clean_number = phone_number.replace('+', '')
            breach_results['phone_breach_info'] = f'Check: https://haveibeenpwned.com/ (Phone breach data limited)'
        
        return breach_results

    def reverse_username_search(self, phone_number):
        """Generate potential usernames from phone number"""
        clean_number = phone_number.replace('+', '').replace(' ', '')
        short_number = clean_number[2:] if clean_number.startswith('91') else clean_number
        
        username_patterns = {
            'full_phone': clean_number,
            'short_phone': short_number,
            'phone_with_91': f'91{short_number}',
            'phone_jio': f'jio{short_number}',
            'phone_user': f'user{short_number}',
            'phone_mobile': f'mobile{short_number}'
        }
        
        return username_patterns

    def comprehensive_scan(self, phone_number, email=None):
        """Perform comprehensive OSINT scan"""
        print(f"[*] Starting comprehensive OSINT scan for: {phone_number}")
        if email:
            print(f"[*] Additional email target: {email}")
        
        # Validate phone number first
        validated_phone = self.validate_phone_number(phone_number)
        if not validated_phone:
            return {'error': 'Invalid phone number format'}
        
        results = {
            'target': {
                'phone': phone_number,
                'validated_format': validated_phone,
                'email': email
            },
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'basic_info': self.get_enhanced_phone_info(phone_number),
            'enhanced_lookup': self.enhanced_reverse_phone_lookup(phone_number),
            'social_media_search': self.search_social_media_profiles(phone_number, email),
            'email_patterns': self.generate_email_patterns(phone_number),
            'public_databases': self.search_public_databases(phone_number),
            'data_breaches': self.check_data_breaches(email, phone_number),
            'username_patterns': self.reverse_username_search(phone_number),
            'investigation_links': self.generate_investigation_links(phone_number, email)
        }
        
        return results

    def generate_investigation_links(self, phone_number, email=None):
        """Generate direct investigation links"""
        clean_number = phone_number.replace('+', '')
        short_number = clean_number[2:] if clean_number.startswith('91') else clean_number
        
        links = {
            'google_search_phone': f'https://www.google.com/search?q="{phone_number}"',
            'google_search_short': f'https://www.google.com/search?q="{short_number}"',
            'duckduckgo_phone': f'https://duckduckgo.com/?q="{phone_number}"',
            'bing_search': f'https://www.bing.com/search?q="{phone_number}"'
        }
        
        if email:
            links.update({
                'google_search_email': f'https://www.google.com/search?q="{email}"',
                'email_breach_check': 'https://haveibeenpwned.com/',
                'email_reputation': 'https://www.email-validator.net/'
            })
        
        return links

    def generate_detailed_report(self, results, output_file=None):
        """Generate comprehensive detailed report"""
        report = f"""
COMPREHENSIVE OSINT RECONNAISSANCE REPORT
==========================================
Generated: {results['timestamp']}
Target Phone: {results['target']['phone']}
Validated Format: {results['target']['validated_format']}
Target Email: {results['target']['email'] or 'Not provided'}

BASIC PHONE INFORMATION:
------------------------
{json.dumps(results['basic_info'], indent=2)}

ENHANCED NUMVERIFY LOOKUP:
--------------------------
{json.dumps(results['enhanced_lookup'], indent=2)}

SOCIAL MEDIA SEARCH LINKS:
--------------------------
Direct search URLs for investigation:
"""
        
        # Social media links
        for platform, url in results['social_media_search']['search_urls'].items():
            report += f"- {platform}: {url}\n"
        
        report += f"""
POTENTIAL EMAIL PATTERNS:
-------------------------
Generated email addresses to investigate:
"""
        for pattern, email in results['email_patterns'].items():
            report += f"- {pattern}: {email}\n"
        
        report += f"""
PUBLIC DATABASE LINKS:
----------------------
{json.dumps(results['public_databases'], indent=2)}

DATA BREACH INFORMATION:
------------------------
{json.dumps(results['data_breaches'], indent=2)}

USERNAME PATTERNS:
------------------
Potential usernames derived from phone number:
{json.dumps(results['username_patterns'], indent=2)}

ADDITIONAL INVESTIGATION LINKS:
-------------------------------
{json.dumps(results['investigation_links'], indent=2)}

INVESTIGATION CHECKLIST:
------------------------
1. ✅ Check all social media links above
2. ✅ Verify email patterns in password recovery systems
3. ✅ Search public databases for additional info
4. ✅ Check data breach results
5. ✅ Use username patterns for account discovery
6. ✅ Perform Google/DuckDuckGo searches
7. ✅ Check if number appears in business directories
8. ✅ Look for associated images/videos online

LEGAL DISCLAIMER:
-----------------
This report is for AUTHORIZED penetration testing and security research ONLY.
Ensure proper authorization before using any information gathered.
Respect all privacy laws and platform terms of service.
        """
        
        print(report)
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(report)
            print(f"[+] Detailed report saved to: {output_file}")

def main():
    parser = argparse.ArgumentParser(description='Enhanced OSINT Reconnaissance Tool')
    parser.add_argument('phone', help='Phone number to investigate')
    parser.add_argument('-e', '--email', help='Associated email address (optional)')
    parser.add_argument('--api-key', help='Numverify API key for enhanced lookup')
    parser.add_argument('-o', '--output', help='Output file for detailed report')
    
    args = parser.parse_args()
    
    # Legal disclaimer
    print("""
🚀 ENHANCED OSINT RECONNAISSANCE TOOL
====================================
⚠️  LEGAL DISCLAIMER:
This tool is for AUTHORIZED penetration testing and security research ONLY.
Ensure you have explicit permission before using this tool.
Misuse may violate privacy laws and regulations.
    """)
    
    confirm = input("Do you have proper authorization to proceed? (yes/no): ")
    if confirm.lower() != 'yes':
        print("Exiting. Only use with proper authorization.")
        sys.exit(1)
    
    # Initialize with API key
    recon = EnhancedOSINTRecon(api_key=args.api_key)
    
    # Perform comprehensive scan
    print(f"[*] Starting enhanced scan for: {args.phone}")
    results = recon.comprehensive_scan(args.phone, args.email)
    
    if 'error' in results:
        print(f"[-] Error: {results['error']}")
        sys.exit(1)
    
    # Generate detailed report
    recon.generate_detailed_report(results, args.output)

if __name__ == "__main__":
    main()
