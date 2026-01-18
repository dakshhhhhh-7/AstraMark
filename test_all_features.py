"""
Quick Test Script for AstraMark Enhanced
Run this to test all features automatically
"""
import requests
import json
import time

BASE_URL = "http://localhost:8001/api"

def print_section(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60 + "\n")

def test_health():
    print_section("TEST 1: Health Check")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_analysis():
    print_section("TEST 2: Create Analysis")
    
    data = {
        "business_type": "AI SaaS Platform",
        "target_market": "Tech startups in USA",
        "monthly_budget": "$10,000",
        "primary_goal": "Acquire 1000 users in 3 months",
        "additional_info": "B2B focus with freemium model"
    }
    
    print("Sending request... (this takes 20-30 seconds)")
    start_time = time.time()
    
    response = requests.post(f"{BASE_URL}/analyze", json=data)
    
    elapsed = time.time() - start_time
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response Time: {elapsed:.2f} seconds")
    
    if response.status_code == 200:
        result = response.json()
        analysis_id = result['id']
        
        print(f"\n✅ Analysis Created!")
        print(f"   ID: {analysis_id}")
        print(f"   Overview: {result['overview'][:100]}...")
        print(f"   Confidence Score: {result['confidence_score']}%")
        print(f"   Virality Score: {result['virality_score']}/100")
        print(f"   Retention Score: {result['retention_score']}/100")
        print(f"   AI Verdict: {result['ai_verdict']}")
        
        print(f"\n✅ Competitor Insights:")
        for comp in result.get('competitor_insights', [])[:2]:
            print(f"   - {comp['name']}: {comp.get('estimated_traffic', 'N/A')} traffic")
        
        print(f"\n✅ Blockchain Proof:")
        proof = result.get('blockchain_proof', {})
        print(f"   Hash: {proof.get('hash', 'N/A')[:32]}...")
        print(f"   Network: {proof.get('network', 'N/A')}")
        
        print(f"\n✅ Market Signals:")
        for signal in result.get('market_signals', [])[:2]:
            print(f"   [{signal['severity'].upper()}] {signal['message']}")
        
        return analysis_id
    else:
        print(f"❌ Error: {response.text}")
        return None

def test_pdf_export(analysis_id):
    print_section("TEST 3: Export PDF")
    
    if not analysis_id:
        print("⚠️  Skipping (no analysis ID)")
        return False
    
    print(f"Exporting analysis: {analysis_id}")
    response = requests.get(f"{BASE_URL}/export/pdf/{analysis_id}")
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        filename = f"test_report_{analysis_id[:8]}.pdf"
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"✅ PDF saved: {filename}")
        print(f"   Size: {len(response.content)} bytes")
        return True
    else:
        print(f"❌ Error: {response.text}")
        return False

def test_pitch_deck(analysis_id):
    print_section("TEST 4: Generate Pitch Deck")
    
    if not analysis_id:
        print("⚠️  Skipping (no analysis ID)")
        return False
    
    print("Generating pitch deck... (this takes 15-20 seconds)")
    response = requests.post(f"{BASE_URL}/generate/pitch-deck?analysis_id={analysis_id}")
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Pitch Deck Generated!")
        print(f"   Total Slides: {result['total_slides']}")
        
        slides = result.get('pitch_deck', {}).get('slides', [])
        if slides:
            print(f"\n   First 3 Slides:")
            for slide in slides[:3]:
                print(f"   {slide['slide_number']}. {slide['title']}")
        
        return True
    else:
        print(f"❌ Error: {response.text}")
        return False

def test_content_calendar(analysis_id):
    print_section("TEST 5: Generate Content Calendar")
    
    if not analysis_id:
        print("⚠️  Skipping (no analysis ID)")
        return False
    
    print("Generating content calendar... (this takes 20-30 seconds)")
    response = requests.post(f"{BASE_URL}/generate/content-calendar?analysis_id={analysis_id}&weeks=4")
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Content Calendar Generated!")
        print(f"   Duration: {result['duration_weeks']} weeks")
        print(f"   Total Posts: {result['total_posts']}")
        return True
    else:
        print(f"❌ Error: {response.text}")
        return False

def test_email_sequence(analysis_id):
    print_section("TEST 6: Generate Email Sequence")
    
    if not analysis_id:
        print("⚠️  Skipping (no analysis ID)")
        return False
    
    print("Generating email sequence... (this takes 10-15 seconds)")
    response = requests.post(f"{BASE_URL}/generate/email-sequence?analysis_id={analysis_id}&sequence_type=onboarding")
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Email Sequence Generated!")
        print(f"   Sequence Type: {result['sequence_type']}")
        print(f"   Total Emails: {result['total_emails']}")
        
        emails = result.get('email_sequence', {}).get('emails', [])
        if emails:
            print(f"\n   First 2 Emails:")
            for email in emails[:2]:
                print(f"   {email['email_number']}. {email['subject_line']} (Day {email['send_delay_days']})")
        
        return True
    else:
        print(f"❌ Error: {response.text}")
        return False

def test_market_signals():
    print_section("TEST 7: Market Signals")
    
    response = requests.get(f"{BASE_URL}/market/signals?limit=5")
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        signals = result.get('signals', [])
        
        if signals:
            print(f"✅ Market Signals Retrieved!")
            print(f"   Count: {result['count']}")
            print(f"\n   Latest Signals:")
            for signal in signals[:3]:
                print(f"   [{signal.get('severity', 'info').upper()}] {signal.get('message', 'N/A')}")
        else:
            print("⚠️  No signals yet (wait 30 minutes for background scanner)")
        
        return True
    else:
        print(f"❌ Error: {response.text}")
        return False

def main():
    print("\n" + "🚀"*30)
    print("  AstraMark Enhanced - Automated Test Suite")
    print("🚀"*30)
    
    results = {
        "Health Check": False,
        "Create Analysis": False,
        "Export PDF": False,
        "Pitch Deck": False,
        "Content Calendar": False,
        "Email Sequence": False,
        "Market Signals": False
    }
    
    try:
        # Test 1: Health Check
        results["Health Check"] = test_health()
        
        # Test 2: Create Analysis
        analysis_id = test_analysis()
        results["Create Analysis"] = analysis_id is not None
        
        if analysis_id:
            # Test 3: PDF Export
            results["Export PDF"] = test_pdf_export(analysis_id)
            
            # Test 4: Pitch Deck
            results["Pitch Deck"] = test_pitch_deck(analysis_id)
            
            # Test 5: Content Calendar
            results["Content Calendar"] = test_content_calendar(analysis_id)
            
            # Test 6: Email Sequence
            results["Email Sequence"] = test_email_sequence(analysis_id)
        
        # Test 7: Market Signals
        results["Market Signals"] = test_market_signals()
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to server!")
        print("   Make sure the backend is running on http://localhost:8001")
        print("   Run: python -m uvicorn server_enhanced:app --reload --port 8001")
        return
    
    # Summary
    print_section("TEST SUMMARY")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, passed_test in results.items():
        status = "✅ PASS" if passed_test else "❌ FAIL"
        print(f"{status}  {test_name}")
    
    print(f"\n{'='*60}")
    print(f"  Results: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
    print(f"{'='*60}\n")
    
    if passed == total:
        print("🎉 All tests passed! Your system is fully functional!")
    elif passed >= total * 0.7:
        print("⚠️  Most tests passed. Check failed tests above.")
    else:
        print("❌ Many tests failed. Check server logs and configuration.")

if __name__ == "__main__":
    main()
