#!/usr/bin/env python3
"""
PUCRS Gamification System Backend Test Suite
Tests all backend API endpoints and functionality
"""

import requests
import json
from datetime import datetime, timedelta
import time
import sys

# Backend URL from environment
BACKEND_URL = "https://2c7034bb-9078-4e97-aca9-f2f1e15d9c42.preview.emergentagent.com/api"

class TestResults:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
        
    def log_pass(self, test_name):
        print(f"✅ PASS: {test_name}")
        self.passed += 1
        
    def log_fail(self, test_name, error):
        print(f"❌ FAIL: {test_name} - {error}")
        self.failed += 1
        self.errors.append(f"{test_name}: {error}")
        
    def summary(self):
        total = self.passed + self.failed
        print(f"\n{'='*60}")
        print(f"TEST SUMMARY: {self.passed}/{total} tests passed")
        print(f"{'='*60}")
        if self.errors:
            print("FAILURES:")
            for error in self.errors:
                print(f"  - {error}")
        return self.failed == 0

class PUCRSBackendTester:
    def __init__(self):
        self.results = TestResults()
        self.admin_token = None
        self.student_token = None
        self.professor_token = None
        self.admin_user = None
        self.student_user = None
        self.professor_user = None
        self.challenge_id = None
        self.solution_id = None
        
    def make_request(self, method, endpoint, data=None, headers=None, expected_status=200):
        """Make HTTP request with error handling"""
        url = f"{BACKEND_URL}{endpoint}"
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, timeout=10)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, headers=headers, timeout=10)
            elif method.upper() == "PUT":
                response = requests.put(url, json=data, headers=headers, timeout=10)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=headers, timeout=10)
            else:
                raise ValueError(f"Unsupported method: {method}")
                
            if response.status_code != expected_status:
                return None, f"Expected status {expected_status}, got {response.status_code}: {response.text}"
                
            return response.json() if response.content else {}, None
        except requests.exceptions.RequestException as e:
            return None, f"Request failed: {str(e)}"
        except json.JSONDecodeError as e:
            return None, f"Invalid JSON response: {str(e)}"
    
    def get_auth_headers(self, token):
        """Get authorization headers"""
        return {"Authorization": f"Bearer {token}"}
    
    def test_user_registration(self):
        """Test user registration for different roles"""
        print("\n🔐 Testing User Registration...")
        
        # Test admin registration
        admin_data = {
            "email": "admin@pucrs.edu.br",
            "name": "Maria Silva",
            "password": "AdminPass123!",
            "role": "admin"
        }
        
        response, error = self.make_request("POST", "/register", admin_data)
        if error:
            self.results.log_fail("Admin Registration", error)
            return False
        
        if not response.get("access_token") or not response.get("user"):
            self.results.log_fail("Admin Registration", "Missing token or user data")
            return False
            
        self.admin_token = response["access_token"]
        self.admin_user = response["user"]
        self.results.log_pass("Admin Registration")
        
        # Test student registration
        student_data = {
            "email": "joao.santos@pucrs.edu.br",
            "name": "João Santos",
            "password": "StudentPass123!",
            "role": "student"
        }
        
        response, error = self.make_request("POST", "/register", student_data)
        if error:
            self.results.log_fail("Student Registration", error)
            return False
            
        self.student_token = response["access_token"]
        self.student_user = response["user"]
        self.results.log_pass("Student Registration")
        
        # Test professor registration
        professor_data = {
            "email": "prof.oliveira@pucrs.edu.br",
            "name": "Prof. Carlos Oliveira",
            "password": "ProfPass123!",
            "role": "professor"
        }
        
        response, error = self.make_request("POST", "/register", professor_data)
        if error:
            self.results.log_fail("Professor Registration", error)
            return False
            
        self.professor_token = response["access_token"]
        self.professor_user = response["user"]
        self.results.log_pass("Professor Registration")
        
        # Test duplicate email registration
        response, error = self.make_request("POST", "/register", admin_data, expected_status=400)
        if error and "400" not in error:
            self.results.log_fail("Duplicate Email Prevention", error)
        else:
            self.results.log_pass("Duplicate Email Prevention")
            
        return True
    
    def test_user_login(self):
        """Test user login functionality"""
        print("\n🔑 Testing User Login...")
        
        # Test valid login
        login_data = {
            "email": "admin@pucrs.edu.br",
            "password": "AdminPass123!"
        }
        
        response, error = self.make_request("POST", "/login", login_data)
        if error:
            self.results.log_fail("Valid Login", error)
            return False
            
        if not response.get("access_token"):
            self.results.log_fail("Valid Login", "Missing access token")
            return False
            
        self.results.log_pass("Valid Login")
        
        # Test invalid credentials
        invalid_login = {
            "email": "admin@pucrs.edu.br",
            "password": "WrongPassword"
        }
        
        response, error = self.make_request("POST", "/login", invalid_login, expected_status=401)
        if error and "401" not in error:
            self.results.log_fail("Invalid Credentials Rejection", error)
        else:
            self.results.log_pass("Invalid Credentials Rejection")
            
        return True
    
    def test_profile_access(self):
        """Test profile access with JWT tokens"""
        print("\n👤 Testing Profile Access...")
        
        # Test valid token access
        headers = self.get_auth_headers(self.admin_token)
        response, error = self.make_request("GET", "/me", headers=headers)
        if error:
            self.results.log_fail("Profile Access with Valid Token", error)
            return False
            
        if response.get("email") != "admin@pucrs.edu.br":
            self.results.log_fail("Profile Access with Valid Token", "Incorrect user data")
            return False
            
        self.results.log_pass("Profile Access with Valid Token")
        
        # Test invalid token access
        invalid_headers = {"Authorization": "Bearer invalid_token"}
        response, error = self.make_request("GET", "/me", headers=invalid_headers, expected_status=401)
        if error and "401" not in error:
            self.results.log_fail("Invalid Token Rejection", error)
        else:
            self.results.log_pass("Invalid Token Rejection")
            
        return True
    
    def test_challenge_management(self):
        """Test challenge CRUD operations"""
        print("\n🎯 Testing Challenge Management...")
        
        # Test challenge creation (admin only)
        future_date = (datetime.utcnow() + timedelta(days=30)).isoformat()
        challenge_data = {
            "title": "Inovação em Sustentabilidade PUCRS",
            "description": "Desenvolva uma solução inovadora para reduzir o consumo de energia no campus da PUCRS",
            "category": "sustainability",
            "difficulty": "intermediate",
            "deadline": future_date,
            "criteria": "Originalidade, viabilidade técnica, impacto ambiental e aplicabilidade no campus",
            "points_reward": 150
        }
        
        headers = self.get_auth_headers(self.admin_token)
        response, error = self.make_request("POST", "/challenges", challenge_data, headers=headers)
        if error:
            self.results.log_fail("Challenge Creation (Admin)", error)
            return False
            
        if not response.get("id"):
            self.results.log_fail("Challenge Creation (Admin)", "Missing challenge ID")
            return False
            
        self.challenge_id = response["id"]
        self.results.log_pass("Challenge Creation (Admin)")
        
        # Test non-admin challenge creation (should fail)
        student_headers = self.get_auth_headers(self.student_token)
        response, error = self.make_request("POST", "/challenges", challenge_data, headers=student_headers, expected_status=403)
        if error and "403" not in error:
            self.results.log_fail("Non-Admin Challenge Creation Prevention", error)
        else:
            self.results.log_pass("Non-Admin Challenge Creation Prevention")
        
        # Test challenge retrieval
        response, error = self.make_request("GET", "/challenges", headers=student_headers)
        if error:
            self.results.log_fail("Challenge Retrieval", error)
            return False
            
        if not isinstance(response, list) or len(response) == 0:
            self.results.log_fail("Challenge Retrieval", "No challenges returned")
            return False
            
        self.results.log_pass("Challenge Retrieval")
        
        # Test specific challenge retrieval
        response, error = self.make_request("GET", f"/challenges/{self.challenge_id}", headers=student_headers)
        if error:
            self.results.log_fail("Specific Challenge Retrieval", error)
            return False
            
        if response.get("id") != self.challenge_id:
            self.results.log_fail("Specific Challenge Retrieval", "Incorrect challenge data")
            return False
            
        self.results.log_pass("Specific Challenge Retrieval")
        
        return True
    
    def test_solution_submission(self):
        """Test solution submission system"""
        print("\n📝 Testing Solution Submission...")
        
        if not self.challenge_id:
            self.results.log_fail("Solution Submission", "No challenge available for testing")
            return False
        
        # Test valid solution submission
        solution_data = {
            "challenge_id": self.challenge_id,
            "content": "Proposta de implementação de painéis solares nos telhados dos prédios principais do campus, com sistema de monitoramento inteligente que otimiza o consumo energético baseado em padrões de uso dos ambientes.",
            "files": ["data:text/plain;base64,UHJvcG9zdGEgZGV0YWxoYWRhIGRlIGltcGxlbWVudGHDp8OjbyBkZSBwYWluw6lpcyBzb2xhcmVz"]
        }
        
        student_headers = self.get_auth_headers(self.student_token)
        response, error = self.make_request("POST", "/solutions", solution_data, headers=student_headers)
        if error:
            self.results.log_fail("Valid Solution Submission", error)
            return False
            
        if not response.get("id"):
            self.results.log_fail("Valid Solution Submission", "Missing solution ID")
            return False
            
        self.solution_id = response["id"]
        self.results.log_pass("Valid Solution Submission")
        
        # Test duplicate solution submission (should fail)
        response, error = self.make_request("POST", "/solutions", solution_data, headers=student_headers, expected_status=400)
        if error and "400" not in error:
            self.results.log_fail("Duplicate Solution Prevention", error)
        else:
            self.results.log_pass("Duplicate Solution Prevention")
        
        # Test solution submission to non-existent challenge
        invalid_solution = {
            "challenge_id": "non-existent-id",
            "content": "Test content",
            "files": []
        }
        
        response, error = self.make_request("POST", "/solutions", invalid_solution, headers=student_headers, expected_status=404)
        if error and "404" not in error:
            self.results.log_fail("Invalid Challenge ID Handling", error)
        else:
            self.results.log_pass("Invalid Challenge ID Handling")
            
        return True
    
    def test_solution_retrieval(self):
        """Test solution retrieval endpoints"""
        print("\n📋 Testing Solution Retrieval...")
        
        # Test user's own solutions
        student_headers = self.get_auth_headers(self.student_token)
        response, error = self.make_request("GET", "/solutions/my", headers=student_headers)
        if error:
            self.results.log_fail("User Solutions Retrieval", error)
            return False
            
        if not isinstance(response, list):
            self.results.log_fail("User Solutions Retrieval", "Invalid response format")
            return False
            
        self.results.log_pass("User Solutions Retrieval")
        
        # Test admin solutions access
        admin_headers = self.get_auth_headers(self.admin_token)
        response, error = self.make_request("GET", "/solutions", headers=admin_headers)
        if error:
            self.results.log_fail("Admin Solutions Access", error)
            return False
            
        if not isinstance(response, list):
            self.results.log_fail("Admin Solutions Access", "Invalid response format")
            return False
            
        self.results.log_pass("Admin Solutions Access")
        
        # Test non-admin solutions access (should fail)
        response, error = self.make_request("GET", "/solutions", headers=student_headers, expected_status=403)
        if error and "403" not in error:
            self.results.log_fail("Non-Admin Solutions Access Prevention", error)
        else:
            self.results.log_pass("Non-Admin Solutions Access Prevention")
            
        return True
    
    def test_evaluation_system(self):
        """Test solution evaluation system"""
        print("\n⭐ Testing Evaluation System...")
        
        if not self.solution_id:
            self.results.log_fail("Solution Evaluation", "No solution available for testing")
            return False
        
        # Test solution evaluation by admin
        evaluation_data = {
            "solution_id": self.solution_id,
            "score": 120,
            "feedback": "Excelente proposta! A ideia dos painéis solares é muito viável e o sistema de monitoramento inteligente demonstra inovação. Sugestão: incluir análise de custo-benefício detalhada."
        }
        
        admin_headers = self.get_auth_headers(self.admin_token)
        response, error = self.make_request("PUT", "/solutions/evaluate", evaluation_data, headers=admin_headers)
        if error:
            self.results.log_fail("Admin Solution Evaluation", error)
            return False
            
        if not response.get("message"):
            self.results.log_fail("Admin Solution Evaluation", "Missing success message")
            return False
            
        self.results.log_pass("Admin Solution Evaluation")
        
        # Test non-admin evaluation (should fail)
        student_headers = self.get_auth_headers(self.student_token)
        response, error = self.make_request("PUT", "/solutions/evaluate", evaluation_data, headers=student_headers, expected_status=403)
        if error and "403" not in error:
            self.results.log_fail("Non-Admin Evaluation Prevention", error)
        else:
            self.results.log_pass("Non-Admin Evaluation Prevention")
        
        # Test evaluation of non-existent solution
        invalid_evaluation = {
            "solution_id": "non-existent-id",
            "score": 100,
            "feedback": "Test feedback"
        }
        
        response, error = self.make_request("PUT", "/solutions/evaluate", invalid_evaluation, headers=admin_headers, expected_status=404)
        if error and "404" not in error:
            self.results.log_fail("Invalid Solution ID Handling", error)
        else:
            self.results.log_pass("Invalid Solution ID Handling")
            
        return True
    
    def test_leaderboard(self):
        """Test leaderboard functionality"""
        print("\n🏆 Testing Leaderboard...")
        
        # Test leaderboard access (should be public)
        response, error = self.make_request("GET", "/leaderboard")
        if error:
            self.results.log_fail("Leaderboard Access", error)
            return False
            
        if not isinstance(response, list):
            self.results.log_fail("Leaderboard Access", "Invalid response format")
            return False
            
        # Check if leaderboard contains expected user data
        found_student = False
        for entry in response:
            if entry.get("name") == "João Santos":
                found_student = True
                if entry.get("points", 0) < 120:  # Should have points from evaluation
                    self.results.log_fail("Leaderboard Points Update", f"Expected at least 120 points, got {entry.get('points', 0)}")
                    return False
                break
        
        if not found_student:
            self.results.log_fail("Leaderboard User Presence", "Student not found in leaderboard")
            return False
            
        self.results.log_pass("Leaderboard Access")
        self.results.log_pass("Leaderboard Points Update")
        
        return True
    
    def test_admin_statistics(self):
        """Test admin dashboard statistics"""
        print("\n📊 Testing Admin Statistics...")
        
        # Test admin stats access
        admin_headers = self.get_auth_headers(self.admin_token)
        response, error = self.make_request("GET", "/admin/stats", headers=admin_headers)
        if error:
            self.results.log_fail("Admin Stats Access", error)
            return False
        
        required_fields = ["total_users", "total_challenges", "active_challenges", "total_solutions", "evaluated_solutions", "pending_evaluations"]
        for field in required_fields:
            if field not in response:
                self.results.log_fail("Admin Stats Completeness", f"Missing field: {field}")
                return False
        
        # Validate expected values
        if response["total_users"] < 3:  # Should have at least admin, student, professor
            self.results.log_fail("Admin Stats Accuracy", f"Expected at least 3 users, got {response['total_users']}")
            return False
            
        if response["total_challenges"] < 1:  # Should have at least one challenge
            self.results.log_fail("Admin Stats Accuracy", f"Expected at least 1 challenge, got {response['total_challenges']}")
            return False
            
        if response["total_solutions"] < 1:  # Should have at least one solution
            self.results.log_fail("Admin Stats Accuracy", f"Expected at least 1 solution, got {response['total_solutions']}")
            return False
            
        self.results.log_pass("Admin Stats Access")
        self.results.log_pass("Admin Stats Completeness")
        self.results.log_pass("Admin Stats Accuracy")
        
        # Test non-admin stats access (should fail)
        student_headers = self.get_auth_headers(self.student_token)
        response, error = self.make_request("GET", "/admin/stats", headers=student_headers, expected_status=403)
        if error and "403" not in error:
            self.results.log_fail("Non-Admin Stats Access Prevention", error)
        else:
            self.results.log_pass("Non-Admin Stats Access Prevention")
            
        return True
    
    def run_all_tests(self):
        """Run complete test suite"""
        print("🚀 Starting PUCRS Gamification Backend Test Suite")
        print(f"Testing backend at: {BACKEND_URL}")
        print("="*60)
        
        # Run tests in logical order
        tests = [
            self.test_user_registration,
            self.test_user_login,
            self.test_profile_access,
            self.test_challenge_management,
            self.test_solution_submission,
            self.test_solution_retrieval,
            self.test_evaluation_system,
            self.test_leaderboard,
            self.test_admin_statistics
        ]
        
        for test in tests:
            try:
                success = test()
                if not success:
                    print(f"⚠️  Test {test.__name__} failed, continuing with remaining tests...")
            except Exception as e:
                self.results.log_fail(test.__name__, f"Unexpected error: {str(e)}")
                print(f"💥 Unexpected error in {test.__name__}: {str(e)}")
        
        return self.results.summary()

if __name__ == "__main__":
    tester = PUCRSBackendTester()
    success = tester.run_all_tests()
    
    if not success:
        print("\n🔍 Some tests failed. Check the errors above for details.")
        sys.exit(1)
    else:
        print("\n🎉 All tests passed! Backend is working correctly.")
        sys.exit(0)