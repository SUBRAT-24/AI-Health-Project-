#!/usr/bin/env python
"""
Chatbot Functionality Test
Tests all chatbot capabilities
"""

import requests

def test_chatbot():
    API_BASE_URL = 'http://localhost:5000/api'
    
    tests = [
        ('headache', ['headache', 'rest', 'remedies']),
        ('fever', ['fever', 'hydrated', 'temperature']),
        ('diet recommendation', ['balanced', 'nutrition', 'diet']),
        ('exercise advice', ['exercise', 'activity']),
        ('sleep problem', ['sleep', 'rest']),
        ('stress management', ['stress', 'relax']),
        ('help', ['help', 'assist']),
    ]
    
    print('\n' + '='*60)
    print('[CHATBOT FULL FUNCTIONALITY TEST]')
    print('='*60 + '\n')
    
    passed = 0
    total = len(tests)
    
    for query, keywords in tests:
        try:
            response = requests.post(
                f'{API_BASE_URL}/chatbot/message',
                json={'message': query},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                bot_response = data.get('response', '').lower()
                
                # Check if any keyword is in response
                found_keyword = any(kw.lower() in bot_response for kw in keywords)
                
                if found_keyword:
                    print(f'[OK] Query: {query}')
                    print(f'     Response preview: {bot_response[:80]}...\n')
                    passed += 1
                else:
                    print(f'[WARN] Query: {query}')
                    print(f'       Expected keywords: {keywords}')
                    print(f'       Response: {bot_response[:80]}...\n')
            else:
                print(f'[ERROR] Query: {query}')
                print(f'        Status code: {response.status_code}\n')
        
        except Exception as e:
            print(f'[ERROR] Query: {query}')
            print(f'        Error: {str(e)}\n')
    
    print('='*60)
    print(f'[RESULT] {passed}/{total} tests passed')
    print(f'[STATUS] Chatbot is {"FULLY FUNCTIONAL" if passed == total else "PARTIALLY FUNCTIONAL"}')
    print('='*60 + '\n')

if __name__ == '__main__':
    test_chatbot()
